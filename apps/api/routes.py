'''
Copyright (c) 2022 University of Memphis, mDOT Center. All rights reserved. 

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer. 

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution. 

3. Neither the name of the copyright holder nor the names of its contributors
may be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import traceback

import pandas as pd
from flask import jsonify, request, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from apps import db
from apps.algorithms.models import Projects
from apps.api import blueprint
from apps.api.codes import StatusCode
from apps.api.sql_helper import get_tuned_params, json_to_series, save_decision, store_tuned_params, get_merged_data
from apps.learning_methods.learning_method_service import get_all_available_methods
from .models import Data, Decision, AlgorithmTunedParams
from .util import get_class_object, pJITAI_token_required, _add_log
from uuid import uuid4
from datetime import datetime
import json
import random


def _save_each_data_row(user_id: int,
                        proj_uuid: str,
                        timestamp: str,
                        proximal_outcome: float,
                        proximal_outcome_timestamp: str,
                        decision_id: int) -> dict:
    resp = "Data has successfully added"
    try:

        decision_obj = Decision.query.filter(Decision.id == decision_id).first()

        if decision_obj:
            data_obj = Data(user_id=user_id,
                            proj_uuid=proj_uuid,
                            timestamp=timestamp,
                            decision_id=decision_id,
                            proximal_outcome=proximal_outcome,
                            proximal_outcome_timestamp=proximal_outcome_timestamp)
            db.session.add(data_obj)
            db.session.commit()

            return data_obj
        else:
            raise Exception(f'Error saving data: {resp}. {decision_id} was not found.')

    except SQLAlchemyError as e:
        resp = str(e.__dict__['orig'])
        db.session.rollback()
        print(traceback.format_exc())
        raise Exception(f'Error saving data: {resp}')
    except:
        raise Exception(f'Error saving data: {resp}')


# API METHODS ARE BELOW

# @blueprint.route('<uuid>', methods=['GET'])
@blueprint.route('<uuid>', methods=['POST'])
# @pJITAI_token_required
def model(uuid: str) -> dict:
    proj = db.session.query(Projects).filter(Projects.uuid == uuid).filter(Projects.project_status == 1).first()
    result = {"status": "ERROR: Project not found"}
    if proj:
        result = proj.as_dict()
    return result


@blueprint.route('<uuid>/decision', methods=['POST', 'GET'])
@pJITAI_token_required
def decision(uuid: str) -> dict:
    data = request.json
    try:
        
        # TODO: Do something with input_data['eligilibity'] (https://github.com/mDOT-Center/pJITAI/issues/21)

        user_id = data['user_id']
        timestamp = data['timestamp']
        state_data = data['state_data']
        tuned_params_dict = get_tuned_params(uuid)

        input_data = pd.DataFrame(state_data)  # Should be in pd.DataFrame
        tuned_params = pd.DataFrame(tuned_params_dict)  # Should be pd.DataFrame

        proj = Projects.query.filter(Projects.uuid == uuid).first() # retrieve project data
        proj_type = proj.general_settings.get("personalization_method")
        class_obj = get_class_object(f"apps.learning_methods.{proj_type}.{proj_type}")
        obj = class_obj(proj.as_dict())

        my_decision, pi, status, random_number = obj.decision(user_id, timestamp, tuned_params, input_data)

        message = ""
        if status == "SUCCESS":
            message = "Decision made successfully"
        
        decision = Decision(user_id=user_id,
                            proj_uuid=uuid,
                            state_data=json.dumps(state_data),
                            timestamp=timestamp,
                            decision=my_decision,
                            status_code=status,
                            status_message=message,
                            pi=pi,
                            random_number=random_number)
        save_decision(decision)  # Save the decision to the database

        decision_output = decision.as_dict()
        if len(decision_output) > 0:
            result = {
                "status_code": status,
                "status_message": message,
                "decision_result": decision_output,
            }
            # Only one row is currently supported.  Extract it and convert to a dictionary before returning to the calling library.
            _add_log(proj_uuid=uuid, log_detail={'input_data': input_data.iloc[0].to_dict(), 'response': result,
                                                 'http_status_code': 200})
            return result, 200
        else:
            result = {
                'status_code': StatusCode.ERROR.value,
                'status_message': f'A decision was unable to be made for: {uuid} with data: {input_data}'
            }
            _add_log(proj_uuid=uuid, log_detail={'input_data': input_data.iloc[0].to_dict(
            ), 'response': None, 'error': result, 'http_status_code': 400})
            return result, 400
    except Exception as e:
        traceback.print_exc()
        result = {
            "status_code": StatusCode.ERROR.value,
            "status_message": str(e),
        }
        _add_log(proj_uuid=uuid,
                 log_detail={'input_data': input_data, 'response': None, 'error': result, 'http_status_code': 400})
        return result, 400


@blueprint.route('<uuid>/upload', methods=['POST'])
@pJITAI_token_required  # TODO: This should actually check the token
def upload(uuid: str) -> dict:
    input_data = request.json
    try:
        user_id = input_data['user_id']
        proj_uuid = uuid
        timestamp = input_data['timestamp']
        proximal_outcome = input_data['proximal_outcome']
        proximal_outcome_timestamp = input_data['proximal_outcome_timestamp']
        decision_id = input_data['decision_id']

        data = _save_each_data_row(user_id=user_id,
                            proj_uuid=proj_uuid,
                            timestamp=timestamp,
                            proximal_outcome=proximal_outcome,
                            proximal_outcome_timestamp=proximal_outcome_timestamp,
                            decision_id=decision_id)

        result = {
            "status_code": StatusCode.SUCCESS.value,
            "status_message": f"Data uploaded to model {uuid}",
            "upload_result": data.as_dict(),
        }
        _add_log(proj_uuid=uuid,
                 log_detail={'input_data': data.as_dict(), 'response': result, 'http_status_code': 200})
        return result, 200
    except Exception as e:
        traceback.print_exc()
        result = {
            'status_code': StatusCode.ERROR.value,
            'status_message': f'Upload was unable to be made for: {uuid} with input data: {input_data}'
        }
        _add_log(proj_uuid=uuid,
                 log_detail={'input_data': input_data, 'response': None, 'error': result, 'http_status_code': 400})
        return result, 400


@blueprint.route('<uuid>/update', methods=['POST'])
@pJITAI_token_required
def update(uuid: str) -> dict:
    update_data = request.json
    try:
        user_id = update_data['user_id']

        df_update_data = get_merged_data(uuid, user_id)

        proj = Projects.query.filter(Projects.uuid == uuid).first() # retrieve project data
        proj_type = proj.general_settings.get("personalization_method")
        class_obj = get_class_object(f"apps.learning_methods.{proj_type}.{proj_type}")
        obj = class_obj(proj.as_dict())

        update_result = obj.update(df_update_data)
        
        theta_mu = update_result.iloc[0]['theta_mu']
        theta_Sigma = update_result.iloc[0]['theta_Sigma']
        degree = update_result.iloc[0]['degree']
        scale = update_result.iloc[0]['scale']
        timestamp = str(datetime.now())

        algo_tuned_params = store_tuned_params(user_id=user_id,  # save to AlgoTunedParams
                           proj_uuid=uuid,
                           timestamp=timestamp,
                           theta_mu=theta_mu,
                           theta_Sigma=theta_Sigma,
                           degree=degree,
                           scale=scale)
        ##########################################
        result = {
            "status_code": StatusCode.SUCCESS.value,
            "status_message": "Update has been made successfully.",
            "update_result": algo_tuned_params.as_dict(),
        }
        _add_log(proj_uuid=uuid, log_detail={'response': result, 'http_status_code': 200})
        return result, 200

    except Exception as e:
        traceback.print_exc()
        result = {
            "status_code": StatusCode.ERROR.value,
            "status_message": str(e),
        }
        _add_log(proj_uuid=uuid,
                 log_detail={'response': None, 'error': result, 'http_status_code': 400})
        return result, 400


@blueprint.route('/search/<query>', methods=['POST', 'GET'])  # or UUID
@login_required
def search(query):
    results = []
    search_query = "%{}%".format(query)
    proj = Projects.query.filter(Projects.general_settings.like(search_query)).all()
    if not proj:
        return {"status": "error", "message": "No result found."}, 400
    else:
        for al in proj:
            results.append(al.as_dict())
        return jsonify(results)

@blueprint.route('/end_userstudy/<uuid>', methods=['GET'])
@login_required
def end_userstudy(uuid):
    segment = 'configuration_final'
    return render_template("design/projects/end_userstudy.html", project_uuid=uuid, segment=segment)

@blueprint.route('/projects/<uuid>', methods=['GET'])  # or UUID
@login_required
def proj(uuid):
    time = str(datetime.now())
    proj = db.session.query(Projects).filter(Projects.uuid == uuid).filter(Projects.project_status == 1).first()
    covariate_names = []
    for k, v in proj.as_dict()['covariates'].items():
        for key, value in v.items():
            if key == 'covariate_name':
                covariate_names.append(value)
    base_url = request.host

    max_id = db.session.query(func.max(Decision.id)).scalar()
    max_proximal = float(proj.model_settings.get("max_proximal_outcome"))
    min_proximal = float(proj.model_settings.get("min_proximal_outcome"))
    random_proximal = (random.random() * (max_proximal - min_proximal)) + min_proximal

    modified_on = ""
    modified_on = proj.as_dict().get("modified_on", "")
    if not modified_on:
        modified_on = datetime.now()

    user_id = current_user.get_id()

    if not proj:
        return {"status": "error",
                "message": "Project ID does not exist or project has not been finalized yet."}, 400
    segment = 'main_project_page_finalized'
    return render_template("design/projects/final_page.html", project_uuid=uuid, proj=proj.as_dict(), covariate_names=covariate_names, user_id=user_id,
                           segment=segment, time=time, base_url=base_url, token=proj.auth_token, max_id=max_id, random_proximal=random_proximal, modified_on=modified_on)

def get_algo_name(uuid):
    proj = db.session.query(Projects).filter(Projects.uuid == uuid).filter(Projects.project_status == 1).first()
    return proj.general_settings.get("personalization_method")