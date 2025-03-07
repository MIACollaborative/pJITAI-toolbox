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
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc

from apps import db
from apps.api.models import Data, AlgorithmTunedParams, Decision, Comment
from apps.algorithms.models import Projects
from apps.learning_methods.ThompsonSampling import ThompsonSampling
import json

def get_comments(project_uuid, page_name):
    if project_uuid:
        print('page_name:', page_name)
        comments_obj = db.session.query(Comment).filter(Comment.page_name == page_name).all()
        comments_details = []
        if comments_obj:            
            for c in comments_obj:
                comments_details.append(c.as_dict())
        print(comments_details)
        return comments_details

def save_decision(decision: Decision):
    try:
        db.session.add(decision)
        db.session.commit()
    except SQLAlchemyError as e:
        resp = str(e.__dict__['orig'])
        db.session.rollback()
        print(traceback.format_exc())
        return {"ERROR": resp}
    except:
        print(traceback.format_exc())


def get_decision_data(proj_uuid: str, user_id: str = None):
    '''
    Get data from data table, created pandas DF (parse all the dict and convert them into columns)
    :param proj_uuid:
    :param user_id:
    :return: pandas DF
    '''
    data = (Decision.query.filter(Decision.proj_uuid == proj_uuid)
                        .filter(Decision.user_id == user_id)
                        .order_by(Decision.timestamp.desc()))
    # else:
    #     data = Decision.query.filter(Decision.proj_uuid == proj_uuid).order_by(Decision.timestamp.desc())
    if data:
        df_from_records = pd.read_sql(data.statement, db.session().bind)
        return df_from_records
    return pd.DataFrame()


def get_merged_data(proj_uuid: str, user_id: str):
    '''
    Get data from data table, created pandas DF (parse all the dict and convert them into columns)
    :param proj_uuid:
    :param user_id:
    :return: pandas DF
    '''
    decision_data = (Decision.query.filter(Decision.proj_uuid == proj_uuid)
                                .filter(Decision.user_id == user_id)
                                .order_by(Decision.timestamp.desc())
                                .all())
                                
    # print(decision_data)
    if not decision_data:
        raise Exception(f'No decision data for the project.')

    merged_data = []
    for dec in decision_data:
        merged_dict = {}
        id = dec.id
        decision_timestamp = dec.timestamp
        decision = dec.decision
        pi = dec.pi
        state_data = json.loads(dec.state_data)

        data = (Data.query.filter(Data.proj_uuid == proj_uuid)
                                .filter(Data.user_id == user_id)
                                .filter(Data.decision_id == id)  # Choose Data with the same decision_id
                                .order_by(Data.timestamp.desc())
                                .first())  # Choose only the first one
        if data == None:  # If Data doesn't exist (no upload)
            continue
        else:
            proximal_outcome = data.proximal_outcome

            merged_dict['id'] = id
            merged_dict['user_id'] = user_id
            merged_dict['proj_uuid'] = proj_uuid
            merged_dict['decision_timestamp'] = decision_timestamp
            merged_dict['decision'] = decision
            merged_dict['pi'] = pi
            for key, value in state_data.items():
                merged_dict[key] = value
            merged_dict['proximal_outcome'] = proximal_outcome

            merged_data.append(merged_dict)

    if not merged_data:
        raise Exception(f'No uploaded data for the project.')
    
    df_merged_data = pd.DataFrame(merged_data)
    print('-------df_merged_data--------------')
    print(df_merged_data)
    print('---------------------')
    return df_merged_data


def get_data(proj_uuid: str, user_id: str = None):
    '''
    Get data from data table, created pandas DF (parse all the dict and convert them into columns)
    :param proj_uuid:
    :param user_id:
    :return: pandas DF
    '''
    data = (Data.query.filter(Data.proj_uuid == proj_uuid)
                    .filter(Data.user_id == user_id)
                    .order_by(Data.timestamp.desc()))
    # else:
    #     data = Data.query.filter(Data.proj_uuid == proj_uuid).order_by(Data.timestamp.desc())
    if data:
        df_from_records = pd.read_sql(data.statement, db.session().bind)

        result = pd.concat([df_from_records, df_from_records['values'].apply(json_to_series)], axis=1)
        result.drop('values', axis=1, inplace=True)
        return result
    
    return pd.DataFrame()


def json_to_series(variable_list):
    keys = []
    values = []

    for variable in variable_list:
        keys.append(variable['name'])
        values.append(variable['value'])
        # for validation_key, validation_value in variable['validation'].items():  # YS: what is validation?
        #     keys.append(f'{variable["name"]}_validation_{validation_key}')
        #     values.append(validation_value)

    return pd.Series(values, index=keys)


def get_tuned_params(proj_uuid: str):
    '''
    Get data from AlgorithmsTunedParams table
    '''
    alg_params = (AlgorithmTunedParams.query
                    .filter(AlgorithmTunedParams.proj_uuid == proj_uuid)
                    .order_by(desc(AlgorithmTunedParams.timestamp))  # YS: Retrieve newest timestamp
                    .first())
    
    if alg_params != None:
        print("get_tuned_params: AlgoTunedParams exists!")
        tuned_params = {
            'theta_mu': [alg_params.theta_mu],
            'theta_Sigma': [alg_params.theta_Sigma],
            'degree': [alg_params.degree],
            'scale': [alg_params.scale],
        }
        return tuned_params
    else:
        print("get_tuned_params: AlgoTunedParams doesn't exist!")
        proj = Projects.query.filter(Projects.uuid == proj_uuid).first().as_dict()
        ts = ThompsonSampling(proj)
        tuned_params = {
            'theta_mu': [ts._theta_mu_ini],
            'theta_Sigma': [ts._theta_Sigma_ini],
            'degree': [ts._L_ini], 
            'scale': [ts._noise_ini]
        }
        return tuned_params

def store_tuned_params(user_id, proj_uuid, timestamp, theta_mu, theta_Sigma, degree, scale):
    try:
        algo_obj = AlgorithmTunedParams(user_id=user_id,
                                        proj_uuid=proj_uuid,
                                        timestamp=timestamp,
                                        theta_mu=theta_mu,
                                        theta_Sigma=theta_Sigma,
                                        degree=degree,
                                        scale=scale)
        db.session.add(algo_obj)
        db.session.commit()
        return algo_obj
    except SQLAlchemyError as e:
        resp = str(e.__dict__['orig'])
        db.session.rollback()
        print(traceback.format_exc())
        return {"ERROR": resp}
    except:
        print(traceback.format_exc())
