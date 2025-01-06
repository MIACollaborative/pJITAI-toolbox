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

import uuid
from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from apps import db


def time_8601() -> str:
    time = datetime.now()
    return time.astimezone().isoformat()


@dataclass
class AlgorithmTunedParams(db.Model):  # YS: Should match 'tuned_params' in test_thompson.py
    __tablename__ = 'algorithm_tuned_params'  # YS: used in decision(), update()
    id = db.Column(db.Integer, primary_key=True, nullable=False)  
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'),
                        nullable=False)
    proj_uuid = db.Column('proj_uuid', db.String(36))
    timestamp = db.Column('timestamp',
                          db.String(100),
                          default=time_8601)
    theta_mu = db.Column('theta_mu', db.JSON)  # added by YS, theta_mu is np.ndarray -> save in JSON
    theta_Sigma = db.Column('theta_Sigma', db.JSON)  # added by YS, theta_Sigma is np.ndarray -> save in JSON
    degree = db.Column('degree', db.Float)  # added by YS
    scale = db.Column('scale', db.JSON)  # added by YS, scale is np.ndarray -> save in JSON

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@dataclass
class Decision(db.Model):  # YS: saved in decision()
    __tablename__ = 'decision'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'),
                        nullable=False)
    # algo_uuid = db.Column('algo_uuid', db.String(36))  # YS: changed to project id
    proj_uuid = db.Column('proj_uuid', db.String(36))

    state_data = db.Column('state_data', db.JSON)   # YS: 👇 example of state_data
                                                    # hs1_state_data = { # state data, must match covariates? # Jane: Yes  # YS: These data should be attached from client session
                                                    #   'Location_validation_status_code': ['SUCCESS'],
                                                    #   'Location': 1, 
                                                    # }
    timestamp = db.Column('timestamp',  # YS: Used in update()
                          db.String(100),
                          default=time_8601)
    decision = db.Column('decision', db.Integer)  # YS: One of Return values of decision(), Used in update()

    status_code = db.Column('status_code', db.String(250))  # YS: One of Return values of decision()
    status_message = db.Column('status_message', db.String(250))  # YS: needed for detail info
    pi = db.Column('pi', db.Float)  # added by YS, pi is decision probability
    random_number = db.Column('random_number', db.Float)  # added by YS, random number used for decision() in TS

    # TODO: Add eligible variable (TWH)
    # TODO: Add eligibility vector which comes from the user API call (TWH)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            setattr(self, property, value)

    def __repr__(self):
        return str(self.id)

    def as_dataframe(self):
        # temp = self.as_dict()
        # temp.pop('decision_options')
        # result = pd.DataFrame(temp, index=[0])
        # result['decision_options'] = None
        # result['decision_options'].astype(object)
        # result.at[0, 'decision_options'] = self.as_dict()['decision_options']
        return self.as_dict()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@dataclass
class Data(db.Model):  # YS: Used in update(), upload()
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'),
                        nullable=False)
    # algo_uuid = db.Column('algo_uuid', db.String(36))
    proj_uuid = db.Column('proj_uuid', db.String(36))  # YS: Changed to project id
    timestamp = db.Column('timestamp',
                          db.String(100),
                          default=time_8601)

    proximal_outcome = db.Column('proximal_outcome', db.Float)  # YS: Used in update()
    proximal_outcome_timestamp = db.Column('proximal_outcome_timestamp',
                                           db.String(64))

    decision_id = db.Column(db.Integer,
                            db.ForeignKey('decision.id'),
                            nullable=False)  # YS: Need this

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            setattr(self, property, value)

    def __repr__(self):
        return str(self.id)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@dataclass
class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    algo_uuid = db.Column('algo_uuid', db.String(36))
    details = db.Column('details', db.JSON)
    timestamp = db.Column('timestamp',
                          db.String(100),
                          default=time_8601)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@dataclass
class Cron(db.Model):
    __tablename__ = 'cron'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    algo_uuid = db.Column('algo_uuid', db.String(36))
    details = db.Column('details', db.JSON)
    timestamp = db.Column('timestamp',
                          db.String(100),
                          default=time_8601)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            setattr(self, property, value)

    def __repr__(self):
        return str(self.name)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
