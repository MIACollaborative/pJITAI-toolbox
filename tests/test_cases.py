### YS: This file has the test cases used for testing in test_thompson.py
### Jane: IMPORTANT: The covariates need to follow a fixed order. This needs to match with the order of the states. We need this to be done outside of ThompsonSampling.py


# One Covariate, binary, tailoring
hs1 = { 
  "algo_type": "algorithm_type",
  "covariates": {
    "4b9f1794-b29f-4f5e-9895-1ef12e904370": { 
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

hs1_state_data = { # state data, must match covariates? # Jane: Yes
  'Location_validation_status_code': ['SUCCESS'],
  'Location': 1,
}  

# Create fake data
# Currently extract from this: https://github.com/mDOT-Center/pJITAI/wiki/pJITAI-Interfaces
# Jane: Currently I only take the ones that are needed for the Thompson Sampling
# Jane: IMPORTANT: algo_uuid needs to be checked!!! << where and how?
hs1_update_rows = [
  {
    "id": 537, # Jane: This is the ID that can match with each decision
    "user_id": "user1",
    "algo_uuid": "697e03e8-2065-4050-9c07-2ef87f2f39ce",
    "decision_timestamp": "2024-10-23T16:57:39Z",
    "decision": 1,
    "decision_probability": 0.6,
    "proximal_outcome": 0.5,
    "Location": 1,
    "Location_validation_status_code": "SUCCESS",
  },
  {
    "id": 538, 
    "user_id": "user1",
    "algo_uuid": "697e03e8-2065-4050-9c07-2ef87f2f39ce",
    "decision_timestamp": "2024-10-23T16:57:39Z",
    "decision": 0,
    "decision_probability": 0.2,
    "proximal_outcome": 0.1,
    "Location": 1,
    "Location_validation_status_code": "SUCCESS",
  },
  {
    "id": 539, 
    "user_id": "user1",
    "algo_uuid": "697e03e8-2065-4050-9c07-2ef87f2f39ce",
    "decision_timestamp": "2024-10-23T16:57:39Z",
    "decision": 0,
    "decision_probability": 0.3,
    "proximal_outcome": 0.7,
    "Location": 0,
    "Location_validation_status_code": "SUCCESS",
  },
  {
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
]

heart_steps_covariate_not_tailoring = { # one_cv_continuous_not_tailoring
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

heart_steps_two_covariates = {  # two_cv_binary_tailoring_continuous_not_tailoring
  "algo_type": "algorithm_type",
  "covariates": {
    "39365837-e898-448d-9dfc-9367413c5add": {
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
    },
    "3d93e188-ce85-4db6-9d5d-9e3a23069d18": {
      "covariate_max_val": "8.0",
      "covariate_min_val": "-0.69",
      "covariate_name": "(log) Prior 30 minute step count",
      "covariate_type": "Continuous",
      "main_effect_prior_mean": "0",
      "main_effect_prior_standard_deviation": "3.16",
      "tailoring_variable": "no"
    }
  },
  "created_by": 2,
  "created_on": "Wed, 20 Nov 2024 16:30:54 GMT",
  "general_settings": {
    "intervention_component_name": "activity suggestions",
    "personalization_method": "ThompsonSampling",
    "personalized_scenario": "I am using results from an MRT",
    "proximal_outcome_name": "(log) Next 30 min step count",
    "study_description": "two covariates: 1 tailoring, 1 not tailoring",
    "study_name": "HeartSteps_two_covariates"
  },
  "id": 13,
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
    "max_proximal_outcome": "8.0",
    "min_proximal_outcome": "-0.69",
    "noise_degree_of_freedom": "5",
    "noise_scale": "3.16",
    "proximal_outcome_type": "Continuous",
    "treatment_prior_mean": "0.13",
    "treatment_prior_standard_deviation": "0.07"
  },
  "modified_on": "Wed, 20 Nov 2024 16:34:18 GMT",
  "project_status": 1,
  "uuid": "56e6a124-9b2d-46bc-b131-29c68710078a"
}

heart_steps_covariate_int = {
  "algo_type": "algorithm_type",
  "covariates": {
    "e20a934b-8514-44e3-8845-185b62cb3460": {
      "covariate_max_val": "6",
      "covariate_min_val": "0",
      "covariate_name": "Day of the week",
      "covariate_type": "Integer",
      "interaction_coefficient_prior_mean": "-0.33",
      "interaction_coefficient_prior_standard_deviation": "1.38",
      "main_effect_prior_mean": "0",
      "main_effect_prior_standard_deviation": "3.16",
      "tailoring_variable": "yes"
    }
  },
  "created_by": 2,
  "created_on": "Wed, 20 Nov 2024 17:27:29 GMT",
  "general_settings": {
    "intervention_component_name": "activity suggestions",
    "personalization_method": "ThompsonSampling",
    "personalized_scenario": "I am using results from an MRT",
    "proximal_outcome_name": "(log) Next 30 min step count",
    "study_description": "covariate: tailoring, type: integer",
    "study_name": "HeartSteps_covariate_integer"
  },
  "id": 14,
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
    "max_proximal_outcome": "8.0",
    "min_proximal_outcome": "-0.69",
    "noise_degree_of_freedom": "5",
    "noise_scale": "3.16",
    "proximal_outcome_type": "Continuous",
    "treatment_prior_mean": "0.13",
    "treatment_prior_standard_deviation": "0.07"
  },
  "modified_on": "Wed, 20 Nov 2024 17:56:11 GMT",
  "project_status": 1,
  "uuid": "7a1ca672-a502-4d4f-a315-edbe0de0c68a"
}

heart_steps_covariate_continuous = {
  "algo_type": "algorithm_type",
  "covariates": {
    "672a206d-69cb-4171-91b8-1e69040f5ad4": {
      "covariate_max_val": "122",
      "covariate_min_val": "-58",
      "covariate_name": "Temperature",
      "covariate_type": "Continuous",
      "interaction_coefficient_prior_mean": "-0.33",
      "interaction_coefficient_prior_standard_deviation": "1.38",
      "main_effect_prior_mean": "0",
      "main_effect_prior_standard_deviation": "3.16",
      "tailoring_variable": "yes"
    }
  },
  "created_by": 2,
  "created_on": "Wed, 20 Nov 2024 18:04:49 GMT",
  "general_settings": {
    "intervention_component_name": "activity suggestions",
    "personalization_method": "ThompsonSampling",
    "personalized_scenario": "I am using results from an MRT",
    "proximal_outcome_name": "(log) Next 30 min step count",
    "study_description": "Covariate: tailoring, type: continuous",
    "study_name": "HeartSteps_covariate_continuous"
  },
  "id": 15,
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
    "max_proximal_outcome": "8.0",
    "min_proximal_outcome": "-0.69",
    "noise_degree_of_freedom": "5",
    "noise_scale": "3.16",
    "proximal_outcome_type": "Continuous",
    "treatment_prior_mean": "0.13",
    "treatment_prior_standard_deviation": "0.07"
  },
  "modified_on": "Wed, 20 Nov 2024 18:07:37 GMT",
  "project_status": 1,
  "uuid": "36041837-0be3-49a6-bffd-e4d5b2d2f264"
}

heart_steps_covariate_not_tailoring_binary = {
  "algo_type": "algorithm_type",
  "covariates": {
    "14783889-476a-4d9e-9cac-7e739e1dd197": {
      "covariate_max_val": "1",
      "covariate_meaning_0": "Employed",
      "covariate_meaning_1": "Unemployed",
      "covariate_min_val": "0",
      "covariate_name": "Employment status",
      "covariate_type": "Binary",
      "main_effect_prior_mean": "0",
      "main_effect_prior_standard_deviation": "3.16",
      "tailoring_variable": "no"
    }
  },
  "created_by": 2,
  "created_on": "Wed, 20 Nov 2024 18:08:54 GMT",
  "general_settings": {
    "intervention_component_name": "activity suggestions",
    "personalization_method": "ThompsonSampling",
    "personalized_scenario": "I am using results from an MRT",
    "proximal_outcome_name": "(log) Next 30 min step count",
    "study_description": "Covariate: not tailoring, type: binary",
    "study_name": "HeartSteps_covariate_not_tailoring_binary"
  },
  "id": 16,
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
    "max_proximal_outcome": "8.0",
    "min_proximal_outcome": "-0.69",
    "noise_degree_of_freedom": "5",
    "noise_scale": "3.16",
    "proximal_outcome_type": "Continuous",
    "treatment_prior_mean": "0.13",
    "treatment_prior_standard_deviation": "0.07"
  },
  "modified_on": "Wed, 20 Nov 2024 18:11:11 GMT",
  "project_status": 1,
  "uuid": "a91565e5-eb84-40a9-8c20-16cd9ed6f48a"
}

heart_steps_covariate_not_tailoring_int = {
  "algo_type": "algorithm_type",
  "covariates": {
    "ec7cc548-fc74-46ec-b233-42912f446448": {
      "covariate_max_val": "100",
      "covariate_min_val": "0",
      "covariate_name": "Age",
      "covariate_type": "Integer",
      "main_effect_prior_mean": "0",
      "main_effect_prior_standard_deviation": "3.16",
      "tailoring_variable": "no"
    }
  },
  "created_by": 2,
  "created_on": "Wed, 20 Nov 2024 18:12:53 GMT",
  "general_settings": {
    "intervention_component_name": "activity suggestions",
    "personalization_method": "ThompsonSampling",
    "personalized_scenario": "I am using results from an MRT",
    "proximal_outcome_name": "(log) Next 30 min step count",
    "study_description": "Covariate: not tailoring, type: integer",
    "study_name": "HeartSteps_covariate_not_tailoring_int"
  },
  "id": 17,
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
    "max_proximal_outcome": "8.0",
    "min_proximal_outcome": "-0.69",
    "noise_degree_of_freedom": "5",
    "noise_scale": "3.16",
    "proximal_outcome_type": "Continuous",
    "treatment_prior_mean": "0.13",
    "treatment_prior_standard_deviation": "0.07"
  },
  "modified_on": "Wed, 20 Nov 2024 18:15:00 GMT",
  "project_status": 1,
  "uuid": "744185a1-8494-4f19-b9cb-f92fd1a6472c"
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