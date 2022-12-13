import copy
from datetime import datetime

from apps import db
from apps.algorithms.models import Projects


def get_project_details(project_uuid, user_id):
    if project_uuid:

        project_details_obj = db.session.query(Projects).filter(Projects.created_by == user_id).filter(Projects.uuid==project_uuid).first()

        if project_details_obj:
            project_details = project_details_obj.as_dict()
        else:
            project_details={}

        return project_details, project_details_obj


def update_general_settings(data,project_details_obj):
    if project_details_obj:
        gen_settings = copy.deepcopy(project_details_obj.general_settings)
        gen_settings.update(data)
        project_details_obj.general_settings = gen_settings
        project_details_obj.modified_on = datetime.now()
        db.session.commit()


def update_intervention_settings(data,project_details_obj):
    if project_details_obj:
        settings = copy.deepcopy(project_details_obj.intervention_settings)
        settings.update(data)
        project_details_obj.intervention_settings = settings
        project_details_obj.modified_on = datetime.now()
        db.session.commit()


def update_model_settings(data,project_details_obj):
    if project_details_obj:
        settings = copy.deepcopy(project_details_obj.model_settings)
        settings.update(data)
        project_details_obj.model_settings = settings
        project_details_obj.modified_on = datetime.now()
        db.session.commit()


def update_covariates_settings(data,project_details_obj, cov_id=None):
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