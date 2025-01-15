import sys
import os
import random
import pandas as pd
import numpy as np
import pytest

# add .. to the path, so 'apps' will resolve correctly
sys.path.append(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))

from apps.learning_methods.ThompsonSampling import ThompsonSampling
from tests.test_cases import hs1, hs1_state_data, hs1_update_rows, hs1_update_point, hs1_decision_freq, hs1_continuous_not_tailoring, hs2_binary_tailoring_continuous_not_tailoring, hs2_state_data, hs1_int_tailoring, hs1_int_state_data, hs1_continuous_tailoring, hs1_continuous_state_data, hs1_binary_not_tailoring, hs1_binary_not_tailoring_state_data, hs1_int_not_tailoring, hs1_int_not_tailoring_state_data, hs2_update_rows

def _initialize(monkeypatch, config):
  ts = ThompsonSampling(config=config)
  return ts

def _decision(monkeypatch, example, state_data):

  ts = _initialize(monkeypatch, example)

  # DECISION PARAMS 
  user_id = 1
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

  decision, pi, status, random_number = ts.decision(user_id, timestamp, tuned_params, input_data)
  # print(pi) # just to see if it works; still need to write an actual test

  return decision, pi, status


def _update(monkeypatch, config, update_rows):
  # TODO: provide the data that the algo would read from the DB, given the HS config and N expected uploads  
  # TODO: provide starting values for tuned params
  # ^^^ are these all done?
  # TODO: test that the resulting values for tuned params are correct given the inputs

  the_data_frame = pd.DataFrame(update_rows)
  ts = _initialize(monkeypatch, config)
  tuned_params = ts.update(the_data_frame)
  # print(tuned_params.iloc[0]['degree'])
  return tuned_params


def test_init_hs_example(monkeypatch):
  ts = _initialize(monkeypatch, hs1)
  assert ts._default_mu == 0
  assert ts._state_dim == len(hs1["covariates"].items())  # _state_dim should match the number of covariates
  assert ts._feature_name_list[0] == "Location"  # _feature_name_list contains 'covariate_name'
  assert ts._action_center_ind == np.array([[1]])  # 1 for tailoring

def test_init_hs_update_point(monkeypatch):  ## YS: Currently, update point is not being used anywhere in the TS class
  ts = _initialize(monkeypatch, hs1_update_point) 
  # TODO: test that it was initialized as expected

def test_init_hs_decision_freq(monkeypatch):  ## YS: Currently, decision freq is not being used anywhere in the TS class
  ts = _initialize(monkeypatch, hs1_decision_freq)
  # TODO: test that it was initialized as expected

def test_init_hs_continous_not_tailoring(monkeypatch):
  ts = _initialize(monkeypatch, hs1_continuous_not_tailoring)
  assert ts.features[0]['feature_parameter_beta_selected_features'] == 'no'  # 'yes' for tailoring, 'no' for not tailoring cov
  assert ts._action_center_ind == np.array([[0]])  # 0 for not tailoring

def test_init_hs_two_binary_tailoring_continous_not_tailoring(monkeypatch):
  ts = _initialize(monkeypatch, hs2_binary_tailoring_continuous_not_tailoring)
  assert ts._state_dim == len(hs2_binary_tailoring_continuous_not_tailoring["covariates"].items()) 
  assert ts._feature_name_list[1] == "(log) Prior 30 minute step count" 

# TODO: write decision tests for all example configs; need to figure out correct input_data

def test_decision_1cv_binary_tailoring(monkeypatch):
  monkeypatch.setattr(random, 'uniform', lambda x, y: 0.1) ## less than pi
  assert random.uniform(0, 1) == 0.1
  decision, pi, status = _decision(monkeypatch, hs1, hs1_state_data)
  assert decision == 1
  assert pi == 0.2386883044226933
  assert status == 'SUCCESS'
  monkeypatch.setattr(random, 'uniform', lambda x, y: 0.3) ## greater than pi
  decision, pi, status = _decision(monkeypatch, hs1, hs1_state_data)
  assert decision == 0

def test_decision_2cv_binary_tailoring_continuous_not_tailoring(monkeypatch):
  monkeypatch.setattr(random, 'uniform', lambda x, y: 0.1) ## less than pi
  assert random.uniform(0, 1) == 0.1
  decision, pi, status = _decision(monkeypatch, hs2_binary_tailoring_continuous_not_tailoring, hs2_state_data)
  assert decision == 1
  assert pi == 0.2386883044226933
  assert status == 'SUCCESS'
  monkeypatch.setattr(random, 'uniform', lambda x, y: 0.3) ## greater than pi
  decision, pi, status = _decision(monkeypatch, hs2_binary_tailoring_continuous_not_tailoring, hs2_state_data)
  assert decision == 0

def test_decision_1cv_int_tailoring(monkeypatch):
  monkeypatch.setattr(random, 'uniform', lambda x, y: 0.1) ## less than pi
  assert random.uniform(0, 1) == 0.1
  decision, pi, status = _decision(monkeypatch, hs1_int_tailoring, hs1_int_state_data)
  assert decision == 1
  assert pi == 0.19656393934600958
  assert status == 'SUCCESS'
  monkeypatch.setattr(random, 'uniform', lambda x, y: 0.3) ## greater than pi
  decision, pi, status = _decision(monkeypatch, hs1_int_tailoring, hs1_int_state_data)
  assert decision == 0

def test_decision_1cv_continuous_tailoring(monkeypatch):
  monkeypatch.setattr(random, 'uniform', lambda x, y: 0.1) ## less than pi
  assert random.uniform(0, 1) == 0.1
  decision, pi, status = _decision(monkeypatch, hs1_continuous_tailoring, hs1_continuous_state_data)
  assert decision == 1
  assert pi == 0.1875136233679039
  assert status == 'SUCCESS'
  monkeypatch.setattr(random, 'uniform', lambda x, y: 0.3) ## greater than pi
  decision, pi, status = _decision(monkeypatch, hs1_continuous_tailoring, hs1_continuous_state_data)
  assert decision == 0

def test_decision_1cv_binary_not_tailoring(monkeypatch):
  monkeypatch.setattr(random, 'uniform', lambda x, y: 0.1) ## less than pi
  assert random.uniform(0, 1) == 0.1
  decision, pi, status = _decision(monkeypatch, hs1_binary_not_tailoring, hs1_binary_not_tailoring_state_data)
  assert decision == 1
  assert pi == 0.8
  assert status == 'SUCCESS'
  monkeypatch.setattr(random, 'uniform', lambda x, y: 0.9) ## greater than pi
  decision, pi, status = _decision(monkeypatch, hs1_binary_not_tailoring, hs1_binary_not_tailoring_state_data)
  assert decision == 0

def test_decision_1cv_int_not_tailoring(monkeypatch):
  monkeypatch.setattr(random, 'uniform', lambda x, y: 0.1) ## less than pi
  assert random.uniform(0, 1) == 0.1
  decision, pi, status = _decision(monkeypatch, hs1_int_not_tailoring, hs1_int_not_tailoring_state_data)
  assert decision == 1
  assert pi == 0.8
  assert status == 'SUCCESS'
  monkeypatch.setattr(random, 'uniform', lambda x, y: 0.9) ## greater than pi
  decision, pi, status = _decision(monkeypatch, hs1_int_not_tailoring, hs1_int_not_tailoring_state_data)
  assert decision == 0

# TODO: write update tests for all example configs; need to figure out correct input_data

def test_update_1cv_binary_tailoring(monkeypatch):
  result = _update(monkeypatch, hs1, hs1_update_rows)
  
  assert result.columns[1] == 'user_id'
  assert result.iloc[0]['degree'] == 9.0

def test_update_2cv_binary_tailoring_continuous_not_tailoring(monkeypatch):
  result = _update(monkeypatch, hs2_binary_tailoring_continuous_not_tailoring, hs2_update_rows)
  
  assert result.columns[1] == 'user_id'

def _test_upload(monkeypatch):  # YS: Don't need to implement this in TS. We can handle upload() in api/routes.py
  # TODO: provide example data that matches what would be expected given the HeartSteps Example config
  # TODO: call ts.upload with the data (and anything else that's needed)
  # TODO: verify that "it worked"--i.e., what would be written to the DB is correct given the data

  assert False