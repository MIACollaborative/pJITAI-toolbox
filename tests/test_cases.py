### YS: This file has the test cases used for testing in test_thompson.py
### Jane: IMPORTANT: The covariates need to follow a fixed order. This needs to match with the order of the states. We need this to be done outside of ThompsonSampling.py
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

heart_steps_covariate_not_tailoring = {  # YS
  "algo_type": "algorithm_type",
  "covariates": {
    "dc1732cf-10a9-460f-a2d7-6554778cd686": {
      "covariate_max_val": "8.0",
      "covariate_min_val": "-0.69",
      "covariate_name": "(log) Prior 30 minute step count",
      "covariate_type": "Continuous",
      "intervention_component_name": "activity suggestions",
      "main_effect_prior_mean": "0",
      "main_effect_prior_standard_deviation": "3.16",
      "proximal_outcome_name": "(log) Next 30 min step count",
      "tailoring_variable": "no"
    }
  },
  "created_by": 2,
  "created_on": "Wed, 13 Nov 2024 22:01:55 GMT",
  "general_settings": {
    "intervention_component_name": "activity suggestions",
    "personalization_method": "ThompsonSampling",
    "personalized_scenario": "I am using results from an MRT",
    "proximal_outcome_name": "(log) Next 30 min step count",
    "study_description": "One covariate, not a tailoring variable (continuous type)",
    "study_name": "HeartSteps_covariate_not_tailoring"
  },
  "id": 12,
  "intervention_settings": {
    "condition_1": "Currently walking",
    "decision_point_frequency": "5",
    "decision_point_frequency_time": "Day",
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
    "max_proximal_outcome": "7.99",
    "min_proximal_outcome": "-0.69",
    "noise_degree_of_freedom": "5",
    "noise_scale": "3.16",
    "proximal_outcome_type": "Continuous",
    "treatment_prior_mean": "0.13",
    "treatment_prior_standard_deviation": "0.07"
  },
  "modified_on": "Wed, 20 Nov 2024 13:56:51 GMT",
  "project_status": 1,
  "uuid": "2203d770-1336-4bc8-86c2-fed2238e3529"
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