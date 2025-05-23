import copy
from datetime import datetime

from flask import request

from apps import db
from apps.algorithms.models import Projects, ProjectMenu
from apps.authentication.models import Users
from apps.api.models import Survey


def get_survey_details(project_uuid):
    if project_uuid:
        survey_details_obj = db.session.query(Survey).filter(Survey.proj_uuid == project_uuid).first()
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
        project_details_obj.general_settings = gen_settings
        project_details_obj.modified_on = datetime.now()
        db.session.commit()

def update_general_settings_collaborators(data, project_details_obj, current_user):  # data: email
    if project_details_obj:
        gen_settings = copy.deepcopy(project_details_obj.general_settings)

        user = db.session.query(Users).filter(Users.email == data).first()
        new_collaborator = {'email': data, 'displayname': user.displayname, 'id': user.id}

        if gen_settings.get('collaborators'):
            existing_collabs = gen_settings['collaborators']
            if not any(c['email'] == data for c in existing_collabs):
                existing_collabs.append(new_collaborator)
            gen_settings['collaborators'] = existing_collabs
        else:  # First time adding a collaborator
            c = db.session.query(Users).filter(Users.email == current_user).first()
            current_user = {'email': current_user, 'displayname': c.displayname, 'id': c.id}
            gen_settings['collaborators'] = [current_user, new_collaborator]
        print('after: ', gen_settings)
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
