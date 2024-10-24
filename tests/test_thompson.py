import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))

from apps.learning_methods.ThompsonSampling import ThompsonSampling
import pytest

def test_thompson(monkeypatch):

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

  ts = ThompsonSampling(features)

  monkeypatch.setattr(ts, 'initialize_from_defaults', lambda: None) # disable

  # DECISION PARAMS
  user_id = 'user1'
  timestamp = '2024-10-23T16:57:39Z'

  # Create a DataFrame with the required values
  t_params = {
      'theta_mu': [ts._theta_mu_ini], #can't figure out the dimensions of any of these
      'theta_Sigma': [ts._theta_Sigma_ini],
      'degree': [ts._degree_ini], 
      'scale': [ts._scale_ini]
  }
  tuned_params = pd.DataFrame(t_params)

  data = {
    'step_count_validation_status_code': ['SUCCESS'],
    'step_count': [100],
  }
  
  input_data =  pd.DataFrame(data)

  d = ts.decision(user_id, timestamp, tuned_params, input_data)
  print(d)

