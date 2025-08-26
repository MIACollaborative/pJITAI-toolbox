import copy
from datetime import datetime

from flask import request

from apps import db
from apps.algorithms.models import Projects, ProjectMenu, ProjectLogs
from apps.authentication.models import Users
from apps.api.models import Survey


def get_survey_details(project_uuid, user_id):
    if project_uuid:
        survey_details_obj = db.session.query(Survey).filter(Survey.proj_uuid == project_uuid).filter(Survey.created_by == user_id).first()
        if survey_details_obj:
            survey_details = survey_details_obj.as_dict()
        else:
            survey_details = {}
        return survey_details, survey_details_obj

def get_project_details(project_uuid, user_id):
    if project_uuid:

        project_details_obj = db.session.query(Projects).filter(
            Projects.uuid == project_uuid).first()

        if project_details_obj:
            project_details = project_details_obj.as_dict()
        else:
            project_details = {}

        return project_details, project_details_obj


def update_general_settings(data, project_details_obj):
    if project_details_obj:
        gen_settings = copy.deepcopy(project_details_obj.general_settings)
        gen_settings.update(data)

        if not project_details_obj.general_settings.get('team_members'):  # Add owner as team member for the first time
            user_id = int(project_details_obj.created_by)
            u = db.session.query(Users).filter(Users.id == user_id).first()
            current_user = {'id': u.id, 'displayname': u.displayname, 'email': u.email}
            gen_settings['team_members'] = [current_user]
        project_details_obj.general_settings = gen_settings
        project_details_obj.modified_on = datetime.now()
        db.session.commit()

def delete_general_settings_team_members(data, project_details_obj):  # data: member_id
    if project_details_obj:
        gen_settings = copy.deepcopy(project_details_obj.general_settings)

        if gen_settings.get('team_members'):
            existing_team_members = gen_settings['team_members']
            updated_team_members = [t for t in existing_team_members if str(t['id']) != str(data)]
            gen_settings['team_members'] = updated_team_members
        project_details_obj.general_settings = gen_settings
        project_details_obj.modified_on = datetime.now()
        db.session.commit()

def update_general_settings_team_members(data, project_details_obj):  # data: email
    if project_details_obj:
        gen_settings = copy.deepcopy(project_details_obj.general_settings)

        user = db.session.query(Users).filter(Users.email == data).first()
        new_team_member = {'email': data, 'displayname': user.displayname, 'id': user.id}

        if gen_settings.get('team_members'):
            existing_team_members = gen_settings['team_members']
            if not any(t['email'] == data for t in existing_team_members):
                existing_team_members.append(new_team_member)
            gen_settings['team_members'] = existing_team_members
        project_details_obj.general_settings = gen_settings
        project_details_obj.modified_on = datetime.now()
        db.session.commit()

def update_intervention_settings(data, project_details_obj):
    if project_details_obj:
        settings = copy.deepcopy(project_details_obj.intervention_settings)
        settings.update(data)
        project_details_obj.intervention_settings = settings
        project_details_obj.modified_on = datetime.now()
        db.session.commit()


def update_model_settings(data, project_details_obj):
    if project_details_obj:
        settings = copy.deepcopy(project_details_obj.model_settings)
        settings.update(data)
        project_details_obj.model_settings = settings
        project_details_obj.modified_on = datetime.now()
        db.session.commit()


def update_covariates_settings(data, project_details_obj, cov_id=None):
    cov_vars = {}
    if project_details_obj:
        settings = copy.deepcopy(project_details_obj.covariates)
        if settings.get(cov_id):
            settings.get(cov_id).update(data)
        elif data:
            cov_vars[cov_id] = data
            settings.update(cov_vars)
        if settings:
            project_details_obj.covariates = settings
            project_details_obj.modified_on = datetime.now()
            db.session.commit()


def add_menu(user_id, project_uuid, page_url):
    if not db.session.query(ProjectMenu).filter(ProjectMenu.created_by == user_id).filter(
            ProjectMenu.page_url == page_url).first():
        ProjectMenu(created_by=user_id, project_uuid=project_uuid, page_url=request.path).save()


def get_project_menu_pages(user_id, project_uuid):
    result = []
    all_pages = db.session.query(ProjectMenu).filter(ProjectMenu.created_by == user_id).filter(
        ProjectMenu.project_uuid == project_uuid).all()
    for ap in all_pages:
        result.append(ap.page_url)
    return result

def get_all_users(user_id):
    result = []
    all_users = db.session.query(Users).filter(Users.id != user_id).all()
    for u in all_users:
        user = {}
        user['displayname'] = u.displayname
        user['email'] = u.email
        result.append(user)
    return result

def add_project_logs(project_uuid, details, page_name, timestamp, created_by):
    ProjectLogs(project_uuid=project_uuid, 
                details=details,
                page_name=page_name,
                timestamp=timestamp,
                created_by=created_by).save()
