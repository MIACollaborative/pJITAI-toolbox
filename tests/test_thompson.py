import sys
import os
import random
import pandas as pd
import numpy as np
import pytest

# add .. to the path, so 'apps' will resolve correctly
sys.path.append(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))

from apps.learning_methods.ThompsonSampling import ThompsonSampling
from tests.test_cases import hs1, hs1_state_data, hs1_update_rows, heart_steps_update_point, heart_steps_decision_freq, heart_steps_covariate_not_tailoring

def _initialize(monkeypatch, config):

  # TODO: why is all this happening out here? It seems like we're just renaming stuff
  # can't TS just take in a project config and do all this internally?


  # ## create features
  # features = {}
  # key_init = 0
  # for key, value in config["covariates"].items():
  #   feature = {}
  #   feature['feature_name']=value['covariate_name']
  #   feature['feature_parameter_alpha0_mu']=value['main_effect_prior_mean']
  #   feature['feature_parameter_alpha0_sigma']=value['main_effect_prior_standard_deviation']
  #   feature['feature_parameter_beta_selected_features']=value['tailoring_variable']
  #   feature['feature_parameter_beta_mu']=value['interaction_coefficient_prior_mean']
  #   feature['feature_parameter_beta_sigma']=value['interaction_coefficient_prior_standard_deviation']
  #   ### Jane2
  #   feature['feature_parameter_state_lower']=value['covariate_min_val']
  #   feature['feature_parameter_state_upper']=value['covariate_max_val']

  #   features[key_init]=feature
  #   key_init+=1

  # ## create standalone_parameters
  # standalone_parameters = {}
  # standalone_parameters['alpha_0_mu_bias'] = config['model_settings']['intercept_prior_mean']
  # standalone_parameters['alpha_0_sigma_bias'] = config['model_settings']['intercept_prior_standard_deviation']
  # standalone_parameters['beta_mu_bias'] = config['model_settings']['treatment_prior_mean']
  # standalone_parameters['beta_sigma_bias'] = config['model_settings']['treatment_prior_standard_deviation']
  # standalone_parameters['noise_degree'] = config['model_settings']['noise_degree_of_freedom']
  # standalone_parameters['noise_scale'] = config['model_settings']['noise_scale']
  # ### Jane2
  # standalone_parameters['min_proximal_outcome'] = config['model_settings']['min_proximal_outcome']
  # standalone_parameters['max_proximal_outcome'] = config['model_settings']['max_proximal_outcome']

  # ## create other_parameters
  # other_parameters = {}
  # other_parameters['lower_clip'] = config['intervention_settings']['intervention_probability_lower_bound']
  # other_parameters['upper_clip'] = config['intervention_settings']['intervention_probability_upper_bound']

  # ts=ThompsonSampling(features, standalone_parameters, other_parameters)
  ts = ThompsonSampling(config=config)
  return ts

def _decision(monkeypatch, example, state_data):

  ts = _initialize(monkeypatch, example)
  #ts = ThompsonSampling(features) # TODO: initialize TS from HS config params above. << is this obsolete?

  # DECISION PARAMS 
  user_id = 'user1'
  timestamp = '2024-10-23T16:57:39Z'

  # Create a DataFrame with the required values
  tuned_params_dict = {
      'theta_mu': [ts._theta_mu_ini], #can't figure out the dimensions of any of these
      'theta_Sigma': [ts._theta_Sigma_ini],
      'degree': [ts._L_ini], 
      'scale': [ts._noise_ini]
  }
  tuned_params = pd.DataFrame(tuned_params_dict)

  input_data =  pd.DataFrame(state_data)

  decision, pi, status = ts.decision(user_id, timestamp, tuned_params, input_data)
  print(pi) # just to see if it works; still need to write an actual test
  # TODO: verify that the decision that's produced is correct given the input data, HS config, and provided values for tuned params
  ###########
  #  end test_decision()
  ###########


def _update(monkeypatch, config, update_rows):
  # TODO: provide the data that the algo would read from the DB, given the HS config and N expected uploads  
  # TODO: provide starting values for tuned params
  # ^^^ are these all done?
  # TODO: test that the resulting values for tuned params are correct given the inputs
  
  row0={
    "id": 537, # Jane: This is the ID that can match with each decision
    "user_id": "user1",
    "algo_uuid": "697e03e8-2065-4050-9c07-2ef87f2f39ce",
    "decision_timestamp": "2024-10-23T16:57:39Z",
    "decision": 1,
    "decision_probability": 0.6,
    "proximal_outcome": 0.5,
    "Location": 1,
    "Location_validation_status_code": "SUCCESS",
  }
  row1={
    "id": 538, 
    "user_id": "user1",
    "algo_uuid": "697e03e8-2065-4050-9c07-2ef87f2f39ce",
    "decision_timestamp": "2024-10-23T16:57:39Z",
    "decision": 0,
    "decision_probability": 0.2,
    "proximal_outcome": 0.1,
    "Location": 1,
    "Location_validation_status_code": "SUCCESS",
  }
  row2={
    "id": 539, 
    "user_id": "user1",
    "algo_uuid": "697e03e8-2065-4050-9c07-2ef87f2f39ce",
    "decision_timestamp": "2024-10-23T16:57:39Z",
    "decision": 0,
    "decision_probability": 0.3,
    "proximal_outcome": 0.7,
    "Location": 0,
    "Location_validation_status_code": "SUCCESS",
  }
  row3={
    "id": 540, 
    "user_id": "user1",
    "algo_uuid": "697e03e8-2065-4050-9c07-2ef87f2f39ce",
    "decision_timestamp": "2024-10-23T16:57:39Z",
    "decision": 0,
    "decision_probability": 0.7,
    "proximal_outcome": 0.1,
    "Location": 1,
    "Location_validation_status_code": "SUCCESS",
  }

  the_data_frame = pd.DataFrame(update_rows)
  ts = _initialize(monkeypatch, config)
  tuned_params = ts.update(the_data_frame)


def test_init_hs_example(monkeypatch):
  _initialize(monkeypatch, hs1)
  # TODO: test that it was initialized as expected

def test_init_hs_update_point(monkeypatch):
  _initialize(monkeypatch, heart_steps_update_point)
  # TODO: test that it was initialized as expected

def test_init_hs_decision_freq(monkeypatch):
  _initialize(monkeypatch, heart_steps_decision_freq)
  # TODO: test that it was initialized as expected

def test_init_hs_covariate_not_tailoring(monkeypatch):
  _initialize(monkeypatch, heart_steps_covariate_not_tailoring)
  # now test that it was initialized as expected

# TODO: write decision tests for all example configs; need to figure out correct input_data

def test_decision_1cv_binary_tailoring (monkeypatch):
  _decision(monkeypatch, hs1, hs1_state_data)
  # TODO: test correct output

def test_update_1cv_binary_tailoring(monkeypatch):
  _update(monkeypatch, hs1, hs1_update_rows)
  # TODO: test correct output

def _test_upload(monkeypatch):
  # TODO: provide example data that matches what would be expected given the HeartSteps Example config
  # TODO: call ts.upload with the data (and anything else that's needed)
  # TODO: verify that "it worked"--i.e., what would be written to the DB is correct given the data
  
  assert False # fail
