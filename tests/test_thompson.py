import sys
import os
import random
import pandas as pd
import numpy as np
import pytest


sys.path.append(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))

from apps.learning_methods.ThompsonSampling import ThompsonSampling
from apps.api import sql_helper

def test_example(monkeypatch):
  assert (3 + 4) == 7
  assert (5 + 7) != 11
  monkeypatch.setattr(random, 'random', lambda: 0.6) # how to use monkeypatch
  assert (random.random() > 0.5)


def test_decision(monkeypatch):

  heart_steps_example = {
    "algo_type": "algorithm_type",
    "covariates": { # aka features? called "covariates" in the UI--how many can there be and what are their possible settings?
      "4b9f1794-b29f-4f5e-9895-1ef12e904370": { # does not appear to map to anything, but maybe somewhat to self.parameters?
        "covariate_max_val": "1",
        "covariate_meaning_0": "Home or Work",
        "covariate_meaning_1": "Neither at home nor at work",
        "covariate_min_val": "0",
        "covariate_name": "Location",
        "covariate_type": "Binary",
        "interaction_coefficient_prior_mean": "-0.33",
        "interaction_coefficient_prior_standard_deviation": "1.38",
        "main_effect_prior_mean": "0",
        "main_effect_prior_standard_deviation": "3.16",
        "tailoring_variable": "yes"
      }
    },
    "created_by": 2,
    "created_on": "Wed, 16 Oct 2024 21:17:24 GMT",
    "general_settings": { # Project settings, not used by Algo
      "intervention_component_name": "activity suggestions",
      "personalization_method": "ThompsonSampling",
      "personalized_scenario": "I am using results from an MRT",
      "proximal_outcome_name": "(log) Next 30 min step count",
      "study_description": "HeartSteps example",
      "study_name": "HeartSteps"
    },
    "id": 8, # project ID?
    "intervention_settings": {
      "condition_1": "Currently walking", # elilgibility/exclusion?
      "condition_2": "Currently waling",
      "decision_point_frequency": "5", # not used by algo?
      "decision_point_frequency_time": "Day", # not used by algo?
      "intervention_option_a": "send an activity suggestion", # algo only cares about # of options?
      "intervention_option_b": "Do nothing",
      "intervention_probability_lower_bound": "0.1", # found in self.other_parameters?
      "intervention_probability_upper_bound": "0.8",
      "update_day": "Daily", # used by scheduler but not algo (so not really used by pJITAI)
      "update_hour": "1:00am" # 
    },

    "model_settings": { # some if these appear in self.standalone_parameters; proximal outcome info appears nowhere
      "intercept_prior_mean": "0",
      "intercept_prior_standard_deviation": "3.16",
      "max_proximal_outcome": "8.0", # how is this used?
      "min_proximal_outcome": "-0.69",
      "noise_degree_of_freedom": "5",
      "noise_scale": "3.16",
      "proximal_outcome_type": "Continuous",
      "treatment_prior_mean": "0.13", # aka "main effect">
      "treatment_prior_standard_deviation": "0.07"
    },
    "modified_on": "Wed, 23 Oct 2024 15:24:54 GMT",
    "project_status": 1, # finalized?
    "uuid": "7a2a9edb-e150-4e08-8547-f855f2d48d4c" #project ID?
  }

  heart_steps_update_point = {  # Added by YS
    "algo_type": "algorithm_type",
    "covariates": {
      "99167b02-95c0-4ad6-a748-91c53e3fc4df": {
        "covariate_max_val": "1",
        "covariate_meaning_0": "Home or Work",
        "covariate_meaning_1": "Neither at home nor at work",
        "covariate_min_val": "0",
        "covariate_name": "Location",
        "covariate_type": "Binary",
        "interaction_coefficient_prior_mean": "-0.33",
        "interaction_coefficient_prior_standard_deviation": "1.38",
        "intervention_component_name": "activity suggestions",
        "main_effect_prior_mean": "0",
        "main_effect_prior_standard_deviation": "3.16",
        "proximal_outcome_name": "(log) Next 30 min step count",
        "tailoring_variable": "yes"
      }
    },
    "created_by": 2,
    "created_on": "Wed, 13 Nov 2024 04:58:16 GMT",
    "general_settings": {
      "intervention_component_name": "activity suggestions",
      "personalization_method": "ThompsonSampling",
      "personalized_scenario": "I am using results from an MRT",
      "proximal_outcome_name": "(log) Next 30 min step count",
      "study_description": "Update_day: weekly, Update_hour: 1AM ",
      "study_name": "HeartSteps_update_point"
    },
    "id": 11,
    "intervention_settings": {
      "condition_1": "Currently walking",
      "decision_point_frequency": "5",
      "decision_point_frequency_time": "Day",
      "intervention_option_a": "send an activity suggestion",
      "intervention_option_b": "Do nothing",
      "intervention_probability_lower_bound": "0.1",
      "intervention_probability_upper_bound": "0.8",
      "update_day": "Weekly",
      "update_hour": "1:00am"
    },
    "model_settings": {
      "intercept_prior_mean": "0",
      "intercept_prior_standard_deviation": "3.16",
      "max_proximal_outcome": "8.0",
      "min_proximal_outcome": "-0.69",
      "noise_degree_of_freedom": "5",
      "noise_scale": "3.16",
      "proximal_outcome_type": "Continuous",
      "treatment_prior_mean": "0.13",
      "treatment_prior_standard_deviation": "0.07"
    },
    "modified_on": "Wed, 13 Nov 2024 22:00:18 GMT",
    "project_status": 1,
    "uuid": "4d6f4771-ffbe-4d55-a2b9-62707a1fb264"
  }

  heart_steps_decision_freq = {  # Added by YS
    "algo_type": "algorithm_type",
    "covariates": {
      "3d8a585b-dc1c-463d-a10e-749539d5782b": {
        "covariate_max_val": "1",
        "covariate_meaning_0": "Home or Work",
        "covariate_meaning_1": "Neither at home nor at work",
        "covariate_min_val": "0",
        "covariate_name": "Location",
        "covariate_type": "Binary",
        "interaction_coefficient_prior_mean": "-0.33",
        "interaction_coefficient_prior_standard_deviation": "1.38",
        "main_effect_prior_mean": "0",
        "main_effect_prior_standard_deviation": "3.16",
        "tailoring_variable": "yes"
      }
    },
    "created_by": 2,
    "created_on": "Tue, 05 Nov 2024 18:07:10 GMT",
    "general_settings": {
      "intervention_component_name": "activity suggestions",
      "personalization_method": "ThompsonSampling",
      "personalized_scenario": "I am using results from an MRT",
      "proximal_outcome_name": "(log) Next 30 min step count",
      "study_description": "decision_point_frequency_time: Week, decision_point_frequency: 5",
      "study_name": "HeartSteps_decision_freq"
    },
    "id": 10,
    "intervention_settings": {
      "condition_1": "Currently walking",
      "decision_point_frequency": "5",
      "decision_point_frequency_time": "Week",
      "intervention_option_a": "send an activity suggestion",
      "intervention_option_b": "Do nothing",
      "intervention_probability_lower_bound": "0.1",
      "intervention_probability_upper_bound": "0.8",
      "update_day": "Daily",
      "update_hour": "1:00am"
    },
    "model_settings": {
      "intercept_prior_mean": "0",
      "intercept_prior_standard_deviation": "3.16",
      "max_proximal_outcome": "8.0",
      "min_proximal_outcome": "-0.69",
      "noise_degree_of_freedom": "5",
      "noise_scale": "3.16",
      "proximal_outcome_type": "Continuous",
      "treatment_prior_mean": "0.13",
      "treatment_prior_standard_deviation": "0.07"
    },
    "modified_on": "Tue, 12 Nov 2024 22:54:30 GMT",
    "project_status": 1,
    "uuid": "4354b8f9-b1bd-4ee9-9a29-28534598b66c"
  }

  #TODO: move all hardcoded sample values into this test case, document where they should come from in reality (i.e., which DB table)
  features = {
    '1': {
         'feature_name': 'step_count',
         'feature_parameter_alpha0_mu': 100,
         'feature_parameter_alpha0_sigma': 0.1,
         'feature_parameter_beta_selected_features': 'yes',
         'feature_parameter_beta_mu': 1.0,
         'feature_parameter_beta_sigma': 0.1,
    }
  }

  ts = ThompsonSampling(features) # TODO: initialize TS from HS config params above.

  # all initialization has been moved into __init__, disabling the later call to initialize for now
  monkeypatch.setattr(ts, 'initialize_from_defaults', lambda: None) # disable

  # DECISION PARAMS 
  user_id = 'user1'
  timestamp = '2024-10-23T16:57:39Z'

  # Create a DataFrame with the required values
  tuned_params_dict = {
      'theta_mu': [ts._theta_mu_ini], #can't figure out the dimensions of any of these
      'theta_Sigma': [ts._theta_Sigma_ini],
      'degree': [ts._degree_ini], 
      'scale': [ts._scale_ini]
  }
  tuned_params = pd.DataFrame(tuned_params_dict)

  state_data = { # state data, must match covariates?
    'step_count_validation_status_code': ['SUCCESS'],
    'step_count': [100],
  }  
  input_data =  pd.DataFrame(state_data)

  d = ts.decision(user_id, timestamp, tuned_params, input_data)
  print(d) # just to see if it works; still need to write an actual test
  # TODO: verify that the decision that's produced is correct given the input data, HS config, and provided values for tuned params
  ###########
  #  end test_decision()
  ###########


def test_upload(monkeypatch):
  # TODO: provide example data that matches what would be expected given the HeartSteps Example config
  # TODO: call ts.upload with the data (and anything else that's needed)
  # TODO: verify that "it worked"--i.e., what would be written to the DB is correct given the data
  
  
  assert False # fail
  ###########
  #  end test_upload()
  ###########

def test_update(monkeypatch):
  # TODO: provide the data that the algo would read from the DB, given the HS config and N expected uploads  
  # TODO: provide starting values for tuned params
  # TODO: test that the resulting values for tuned params are correct given the inputs

  the_data_frame = None
  monkeypatch.setattr(sql_helper, 'get_merged_data', lambda: the_data_frame) # how to use monkeypatch

  assert False # fail
  ###########
  #  end test_upload()
  ###########
