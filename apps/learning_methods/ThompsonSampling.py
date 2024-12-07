'''
Copyright (c) 2022 University of Memphis, mDOT Center and Harvard University. 
All rights reserved. 

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

import random

# These are libraries hsinyu include
import numpy as np
import pandas as pd
from scipy.stats import t
from scipy.linalg import block_diag

from apps.api.codes import StatusCode
from apps.api.models import Decision
from apps.api.sql_helper import get_merged_data
from apps.api.util import time_8601
from apps.learning_methods.LearningMethodBase import LearningMethodBase


class ThompsonSampling(LearningMethodBase):

    ## This code is missing standardization in several places
    ## First, when a decision needs to be made or when the posterior parameters need to be updated,
    ## the state variables need to be standardized.
    ## In addition, to initialize the prior parameters, the hyperparameters from the UI need to be transformed accordingly.

    # def __init__(self, features=[], standalone_parameters={}, other_parameters={}):
    def __init__(self, config=[]):
        super().__init__()
        self.type = "ThompsonSampling"  # this should be same as class name
        self.description = 'This is the thomson sampling algorithm definition.'
        # TODO: for all sigma range (0 to +inf) and for all mu, (-inf, +inf), Noise is same like sigma
        # technical section: param section for behav scitn.
        # help /FAQ
        # more info/tutorial
        # should have a left/right pane on the same screen
        # after run, finalize/contract (create a micro service, create a new url, where a 3rd party can accesss the finalized algo)
        
        ### Jane2: These are the default values we provide for the behavioral scientists (change these values if we decide different defaults)
        self._default_mu = 0.0
        self._default_sigma = 0.316
        self._default_sigma_2 = 0.1 #(self._default_sigma**2)
        self._default_sigma0 = 1.0
        self._default_sigma0_2 = 1.0 #(self._default_sigma0**2)
        self._default_L = 10.0
        ## The below is needed in case the standardization transformation is ill-conditioned
        self._default_alpha0_sigma0_2 = 0.1
        self._default_beta_sigma0_2 = 0.1


        # self.features = features # added by mwn
        # self.standalone_parameters = standalone_parameters
        # self.other_parameters = other_parameters

        ## YS: Move initialization from test_thompson.py to TS class
        ## create features
        features = {}
        key_init = 0
        for key, value in config["covariates"].items():
            feature = {}
            feature['feature_name']=value['covariate_name']
            feature['feature_parameter_alpha0_mu']=value['main_effect_prior_mean']
            feature['feature_parameter_alpha0_sigma']=value['main_effect_prior_standard_deviation']
            feature['feature_parameter_beta_selected_features']=value['tailoring_variable']
            if (feature['feature_parameter_beta_selected_features'] == 'yes'):
                feature['feature_parameter_beta_mu']=value['interaction_coefficient_prior_mean']
                feature['feature_parameter_beta_sigma']=value['interaction_coefficient_prior_standard_deviation']
            ### Jane2
            feature['feature_parameter_state_lower']=value['covariate_min_val']
            feature['feature_parameter_state_upper']=value['covariate_max_val']

            features[key_init]=feature
            key_init+=1

        self.features = features  ## added by YS

        ## create standalone_parameters
        standalone_parameters = {}
        standalone_parameters['alpha_0_mu_bias'] = config['model_settings']['intercept_prior_mean']
        standalone_parameters['alpha_0_sigma_bias'] = config['model_settings']['intercept_prior_standard_deviation']
        standalone_parameters['beta_mu_bias'] = config['model_settings']['treatment_prior_mean']
        standalone_parameters['beta_sigma_bias'] = config['model_settings']['treatment_prior_standard_deviation']
        standalone_parameters['noise_degree'] = config['model_settings']['noise_degree_of_freedom']
        standalone_parameters['noise_scale'] = config['model_settings']['noise_scale']
        ### Jane2
        standalone_parameters['min_proximal_outcome'] = config['model_settings']['min_proximal_outcome']
        standalone_parameters['max_proximal_outcome'] = config['model_settings']['max_proximal_outcome']

        self.standalone_parameters = standalone_parameters  ## added by YS

        ## create other_parameters
        other_parameters = {}
        other_parameters['lower_clip'] = config['intervention_settings']['intervention_probability_lower_bound']
        other_parameters['upper_clip'] = config['intervention_settings']['intervention_probability_upper_bound']
        
        self.other_parameters = other_parameters  ## added by YS

        
        ## Jane: IMPORTANT: Eligibility is currently not implemented in ThompsonSampling.py

        # self.parameters = {
        #     "alpha0_mu": {
        #         "description": "baseline prior mean",
        #         "type": "float",
        #         "lower_bound": "-inf",
        #         "upper_bound": "inf",
        #         "inclusive": [False, False],
        #         "default_value": 0
        #     },
        #     "alpha0_sigma": {
        #         "description": "baseline prior std",
        #         "type": "float",
        #         "lower_bound": 0,
        #         "upper_bound": "inf",
        #         "inclusive": [False, False],
        #         "default_value": 3.16
        #     },
        #     "beta_selected_features": {
        #         "description": "tailoring variable or not",
        #         "type": "str",
        #         "lower_bound": "no",
        #         "upper_bound": "yes",
        #         "inclusive": [True, True],
        #         "default_value": "yes"
        #     },
        #     "beta_mu": {
        #         "description": "tailored effect prior mean",
        #         "type": "float",
        #         "lower_bound": "-inf",
        #         "upper_bound": "inf",
        #         "inclusive": [False, False],
        #         "default_value": 0
        #     },
        #     "beta_sigma": {
        #         "description": "tailored effect prior std",
        #         "type": "float",
        #         "lower_bound": 0,
        #         "upper_bound": "inf",
        #         "inclusive": [False, False],
        #         "default_value": 3.16
        #     }
        # }
        
        # TODO Change to "model parameters"?
        # self.standalone_parameters = {
        #     # I may want to change the names of all of these
        #     "alpha_0_mu_bias": {
        #         "description": "intercept prior mean",
        #         "type": "float",
        #         "lower_bound": "-inf",
        #         "upper_bound": "inf",
        #         "inclusive": [False, False],
        #         "default_value": 0
        #     },
        #     "alpha_0_sigma_bias": {
        #         "description": "intercept prior std",
        #         "type": "float",
        #         "lower_bound": 0,
        #         "upper_bound": "inf",
        #         "inclusive": [False, False],
        #         "default_value": 3.16
        #     },
        #     "beta_mu_bias": {
        #         "description": "main effect prior mean",
        #         "type": "float",
        #         "lower_bound": "-inf",
        #         "upper_bound": "inf",
        #         "inclusive": [False, False],
        #         "default_value": 0
        #     },
        #     "beta_sigma_bias": {
        #         "description": "main effect prior std",
        #         "type": "float",
        #         "lower_bound": 0,
        #         "upper_bound": "inf",
        #         "inclusive": [False, False],
        #         "default_value": 3.16
        #     },
        #     "noise_scale": {
        #         "description": "scaling parameter of scaled inverse chi square",
        #         "type": "float",
        #         "lower_bound": 0,
        #         "upper_bound": "inf",
        #         "inclusive": [False, False],
        #         "default_value": 1
        #     },

        #     "noise_degree": {
        #         "description": "degree of freedom of scaled inverse chi square",
        #         "type": "float",
        #         "lower_bound": 0,
        #         "upper_bound": "inf",
        #         "inclusive": [False, False],
        #         "default_value": 0.2
        #     }

        # }
        # # For now you can change it to "intervention parameters"
        # self.other_parameters = {
        #     "lower_clip": {
        #         "description": "randomization probability lower bound",
        #         "type": "float",
        #         "lower_bound": 0,
        #         "upper_bound": 1,
        #         "inclusive": [True, True],
        #         "default_value": 0.1
        #     },
        #     "upper_clip": {
        #         "description": "randomization probability upper bound",
        #         "type": "float",
        #         "lower_bound": 0,
        #         "upper_bound": 1,
        #         "inclusive": [True, True],
        #         "default_value": 0.8
        #     },
        #     # I'm not sure what the unit should be
        #     "fixed_randomization_period": {
        #         "description": "length of the fixed randomization period",
        #         "type": "float",
        #         "lower_bound": 0,
        #         "upper_bound": "inf",
        #         "inclusive": [True, False],
        #         "default_value": 3
        #     },
        #     "fixed_randomization_probability": {
        #         "description": "fixed randomization probability",
        #         "type": "float",
        #         "lower_bound": 0,
        #         "upper_bound": 1,
        #         "inclusive": [True, True],
        #         "default_value": 0.3
        #     }
        # }
        
        # self.tuning_scheduler = {
        #     "name": "update_interval",
        #     "description": "time interval between running algorithm and update policy. Time is in seconds/minutes???",
        #     "type": "float",
        #     "lower_bound": 0,
        #     "upper_bound": "pinf",
        #     "inclusive": [True, True],
        #     "default_value": 0.39
        # }
        
        # # TODO: This needs populated via the web interface when complete.
        # self.eligibility = {
        #     "walking": False,
        #     "driving": False,
        # }
       
        ### WAS IN initialize_from_defaults()


        # Let's for now not set it as numpy array
        # We can also initialize the following as an numpy array. Not sure what we prefer. For now, I keep everything consistent.
        alpha0_mu = []
        beta_mu = []
        alpha0_std_sigma = []
        beta_std_sigma = []
        action_center_ind = []
        ### Jane2
        state_lower = []
        state_upper = []
        # This indicates whether the prior mean is the same as the default value
        default_alpha_mu_ind=[]
        default_beta_mu_ind=[]
        default_alpha_sigma_ind=[]
        default_beta_sigma_ind=[]

        feature_name_list = []

        for key, feature in self.features.items():
            #index = int(key) - 1  # TODO: Why do I have to change the type on the index? and subtract 1
            # There might be a better way to do this. Let me try to be safe to ensure the order of the features is consistent.
            feature_name = feature['feature_name']
            feature_name_list.append(feature_name)
            alpha0_mu.append(float(feature['feature_parameter_alpha0_mu']))
            alpha0_std_sigma.append(float(feature['feature_parameter_alpha0_sigma']))
            ### Jane2
            state_lower.append(float(feature['feature_parameter_state_lower']))
            state_upper.append(float(feature['feature_parameter_state_upper']))
            if(alpha0_mu[-1]==self._default_mu):
                default_alpha_mu_ind.append(1)
            else:
                default_alpha_mu_ind.append(0)
            if(alpha0_std_sigma[-1]==self._default_sigma):
                default_alpha_sigma_ind.append(1)
            else:
                default_alpha_sigma_ind.append(0)

            if (feature['feature_parameter_beta_selected_features'] == 'yes'):
                beta_mu.append(float(feature['feature_parameter_beta_mu']))
                beta_std_sigma.append(float(feature['feature_parameter_beta_sigma']))
                action_center_ind.append(1)
                ### Jane2
                if(beta_mu[-1]==self._default_mu):
                    default_beta_mu_ind.append(1)
                else:
                    default_beta_mu_ind.append(0)
                if(beta_std_sigma[-1]==self._default_sigma):
                    default_beta_sigma_ind.append(1)
                else:
                    default_beta_sigma_ind.append(0)
            else:
                action_center_ind.append(0)

        alpha0_mu.append(float(self.standalone_parameters['alpha_0_mu_bias'])) #mwn
        beta_mu.append(float(self.standalone_parameters['beta_sigma_bias']))#mwn
        alpha0_std_sigma.append(float(self.standalone_parameters['alpha_0_sigma_bias']))#mwn
        beta_std_sigma.append(float(self.standalone_parameters['beta_sigma_bias']))#mwn
        ## Jane2
        if(alpha0_mu[-1]==self._default_mu):
            default_alpha_mu_ind.append(1)
        else:
            default_alpha_mu_ind.append(0)
        if(alpha0_std_sigma[-1]==self._default_sigma):
            default_alpha_sigma_ind.append(1)
        else:
            default_alpha_sigma_ind.append(0)
        if(beta_mu[-1]==self._default_mu):
            default_beta_mu_ind.append(1)
        else:
            default_beta_mu_ind.append(0)
        if(beta_std_sigma[-1]==self._default_sigma):
            default_beta_sigma_ind.append(1)
        else:
            default_beta_sigma_ind.append(0)

        # self._degree_ini = float(self.standalone_parameters['noise_degree']) 
        # self._scale_ini = float(self.standalone_parameters['noise_scale']) 
        ## Jane2
        L= float(self.standalone_parameters['noise_degree']) 
        std_noise = float(self.standalone_parameters['noise_scale']) 

        self._lower_clip = float(self.other_parameters['lower_clip']) 
        self._upper_clip = float(self.other_parameters['upper_clip']) 

        ### Jane2
        reward_lower = float(self.standalone_parameters['min_proximal_outcome'])
        reward_upper = float(self.standalone_parameters['max_proximal_outcome'])
        state_lower = np.array(state_lower)
        state_upper = np.array(state_upper)
        self.min_max_states_reward(state_lower, state_upper, reward_lower, reward_upper)
        alpha0_mu = np.array([alpha0_mu]).T
        beta_mu = np.array([beta_mu]).T
        alpha0_std_sigma = np.array(alpha0_std_sigma)
        beta_std_sigma = np.array(beta_std_sigma)
        default_alpha_mu_ind = np.array([default_alpha_mu_ind]).T
        default_beta_mu_ind = np.array([default_beta_mu_ind]).T
        default_alpha_sigma_ind = np.array([default_alpha_sigma_ind]).T
        default_beta_sigma_ind = np.array([default_beta_sigma_ind]).T

        self._state_dim = len(self.features.items())  # Number of states
        self._action_center_ind = np.array([action_center_ind]).T  # Which of these states are tailoring variables
        self._alpha_len = len(alpha0_mu) + len(beta_mu)
        # This is for reading through the values of each feature and the validation code
        self._feature_name_list = feature_name_list

        # We can initialize theta_mu and theta_sigma here
        # Eventually the standardization would need to happen here

        ### Jane2
        self.init_theta(default_alpha_mu_ind, alpha0_mu, default_alpha_sigma_ind, alpha0_std_sigma, default_beta_mu_ind, beta_mu, default_beta_sigma_ind, beta_std_sigma, L, std_noise)

        ### Jane2: Comment this out
        # # Right now we haven't changed theta_Sigma with respect to the scaling parameter of the noise
        # theta_mu_ini = np.array([alpha0_mu + beta_mu + beta_mu]).T
        # theta_sigma_list = alpha0_std_sigma + beta_std_sigma + beta_std_sigma
        # theta_Sigma_ini = np.diag(np.array(theta_sigma_list) ** 2 / (self._scale_ini**2))
        # self._theta_mu_ini = theta_mu_ini
        # self._theta_Sigma_ini = theta_Sigma_ini


    # TODO: Add a variable for elibibility based on a computation on self.eligibility in the calling method (TWH)
    def decision(self,  user_id: str, timestamp: str, tuned_params=None, input_data=None): #-> pd.DataFrame: (Jane: IMPORTANT: Need to be implemented))

        # These need to be read from the web user interface
        # I added "value" to represent what each option means in the linear regression. It's super important.
        ### Jane: The below isn't used at all... It shouldn't be set up here.
        # decision_options = [
        #     {  # Index 0
        #         'name': 'Do Nothing',
        #         'value': 0.7,
        #     },
        #     {  # Index 1
        #         'name': 'Send an Intervention',
        #         'value': 0.3,
        #     }
        # ]

        # Initialize all the global parameters appropriately
        # Jane: IMPORTANT: I assume that the initialization is done in the __init__ function
        # self.initialize_from_defaults()


        # Accessing tuned parameters
        # Parameters are access by column name and first row

        try:
            theta_mu = np.array(tuned_params.iloc[0]['theta_mu'])
            theta_Sigma = np.array(tuned_params.iloc[0]['theta_Sigma'])
            degree = tuned_params.iloc[0]['degree']
            noise = np.array(tuned_params.iloc[0]['scale'])

        except Exception as e:  # Something is wrong or data is missing, assuming defaults
            theta_mu = self._theta_mu_ini
            theta_Sigma = self._theta_Sigma_ini
            degree = self._L_ini
            noise = self._noise_ini

        # Setup the state
        state = []
        i = 0
        for feature_name in self._feature_name_list:
            # We will need to check the eligibility as well!
            # Jane: IMPORTANT: Here we only consider valid state values
            if (input_data.iloc[0][feature_name + '_validation_status_code'] == 'SUCCESS'):
                ### Jane2: We need to stanadardize the state
                unstand_state = input_data.iloc[0][feature_name]
                state.append((unstand_state - self._state_med[i,0]) / self._state_half_range[i,0])
            i += 1
        state = np.array([state]).T

        # Check whether it's eligible # Jane: IMPORTANT: Eligibility is currently not implemented in ThompsonSampling.py
        if (False):
            pi = 0

        # Check whether all the covariates are valid => If not, what should we do?
        elif (len(state) != self._state_dim):
            pi = self._lower_clip

        # # Check whether it's fixed randomization period
        # elif (False):
        #     # There is a missing parameter from the web interface as well
        #     print("To-Do")

        # Personalization (Thompson Sampling)
        else:
            beta_mu = theta_mu[self._alpha_len:]
            beta_Sigma = theta_Sigma[self._alpha_len:, :][:, self._alpha_len:]
            
            # mu_t and Sigma_t are associated with the f(S)*beta
            mu_t = np.matmul(np.transpose(self.action_center(state)), beta_mu)
            Sigma_t = np.matmul(np.transpose(self.action_center(state)), beta_Sigma)

            # Notice that the posterior variance of f(S)*beta is scaled by the scale of the inverse chi-square distribution
            Sigma_t = noise * np.matmul(Sigma_t, self.action_center(state))

            # f(S)*beta is a multivariate t distribution with mean mu_t, variance Sigma_t, and degree of freedom L
            scale_t=np.sqrt(Sigma_t[0,0])
            pi = 1 - t.cdf(0, degree, loc=mu_t[0,0], scale=scale_t)
            pi = max(self._lower_clip, pi)
            pi = min(self._upper_clip, pi)

        random_number = random.uniform(0, 1)
        if (pi > random_number):
            my_decision = 1  # decision_options[1]['name']
        else:
            my_decision = 0  # decision_options[0]['name']

        status=StatusCode.SUCCESS.value

        # Jane: IMPORTANT: We need to record pi as well

        # decision = Decision(user_id=user_id,
        #                     algo_uuid=self.uuid,
        #                     decision=my_decision,
        #                     decision_options=decision_options,
        #                     status_code=StatusCode.SUCCESS.value,
        #                     status_message="Decision made successfully")

        return my_decision, pi, status

    def update(self, data) -> dict: # Jane: IMPORTANT: previously, data isn't part of the input
        #data = get_merged_data(algo_id=self.uuid)

        columns = ['timestamp', 'user_id']

        # Create column names for the datafram        

        columns.append('theta_mu')
        columns.append('theta_Sigma')
        columns.append('degree')
        columns.append('scale')

        result = pd.DataFrame([], columns=columns)

        # I move the initialization out because it only needs to be done once for everyone
        # self.initialize_from_defaults()

        for u in data.user_id.unique():
            result_data = [time_8601(), u]

            theta_mu, theta_Sigma, degree, noise = self.update_parameters(data[data.user_id == u])

            result_data.append(theta_mu.tolist())
            result_data.append(theta_Sigma.tolist())
            result_data.append(degree)
            result_data.append(noise.tolist())
            temp = pd.DataFrame([result_data], columns=columns)
            result = pd.concat([result, temp], ignore_index=True)

        return result



    # This function should match with the "update" function here: https://github.com/StatisticalReinforcementLearningLab/mDOT_toolbox/blob/master/TS_Toolbox_inverse_gamma_v1.py
    def update_parameters(self, data):
        # I want to select all the data with valid validation status code (ask Tim) and concatenate the data into a matrix of ...
        # I'll use a for loop for now 
        # (This is a lame implementation but is the most careful one)
        # state_list=[]
        Phi_all = np.array([], dtype=float).reshape(len(self._theta_mu_ini), 0)
        reward_all = []
        for row in data.itertuples():
            state = []
            i = 0
            for feature_name in self._feature_name_list:
                # We will need to check the eligibility as well!
                if (getattr(row, feature_name + '_validation_status_code') == 'SUCCESS'):
                    ### Jane2: We need to stanadardize the state
                    unstand_state = getattr(row, feature_name)
                    state.append((unstand_state - self._state_med[i,0]) / self._state_half_range[i,0])
            # If all the states are "valid"
            if (len(state) == self._state_dim):
                state = np.array([state]).T
                # Check how to grab the decision and how the decision is coded in numerical values

                # Jane: I edited the below because I don't think we need the exact same format as the original code
                # action = getattr(row, 'decision__decision')  # index of the action chosen
                action = getattr(row, 'decision')
                
                # we will need to grab the intervention probability as well
                # Jane: I edited the below because I don't think we need the exact same format as the original code
                # pi = getattr(row, 'decision__decision_options')[getattr(row, 'decision__decision')]['value']
                pi = getattr(row, 'decision_probability')

                Phi = self.reward_model(state, action, pi)
                Phi_all = np.hstack((Phi_all, Phi))

                ### Jane2: We need to standardize the reward
                unstand_reward = getattr(row, 'proximal_outcome')
                reward = (unstand_reward - self._reward_med) / self._reward_half_range
                reward_all.append(reward)

        reward_all = np.array([reward_all]).T

        # Now we are ready to update theta
        # Right now I did not handle ill-conditioned matrix
        theta_Sigma = np.linalg.inv(np.linalg.inv(self._theta_Sigma_ini) + np.matmul(Phi_all, np.transpose(Phi_all)))
        theta_mu = np.matmul(np.linalg.inv(self._theta_Sigma_ini), self._theta_mu_ini) + np.matmul(Phi_all, reward_all)
        theta_mu = np.matmul(theta_Sigma, theta_mu)

        # Now we update the noise
        degree = self._L_ini + len(reward_all)
        tmp0 = reward_all - np.matmul(np.transpose(Phi_all), self._theta_mu_ini)
        tmp = np.linalg.solve(
            np.matmul(np.matmul(np.transpose(Phi_all), self._theta_Sigma_ini), Phi_all) + np.identity(len(reward_all)),
            tmp0)
        noise = 1 / degree * (len(reward_all) * self._noise_ini + np.matmul(np.transpose(tmp0), tmp))

        return theta_mu, theta_Sigma, degree, noise

    # The follows are helper functions for Thompson sampling

    ### Jane2
    def min_max_states_reward(self, state_lower, state_upper, reward_lower, reward_upper):
        state_med = 0.5* (state_lower + state_upper)
        state_half_range = 0.5* (state_upper - state_lower)
        reward_med = 0.5* (reward_lower + reward_upper)
        reward_half_range = 0.5* (reward_upper - reward_lower)
        
        self._state_med = np.expand_dims(state_med,axis=1)
        self._state_half_range = np.expand_dims(state_half_range,axis=1)
        self._reward_med = reward_med
        self._reward_half_range = reward_half_range
        
    ### Jane2
    def init_theta(self, default_alpha_mu_ind, alpha0_mu, default_alpha_sigma_ind, alpha0_std_Sigma, default_beta_mu_ind, beta_mu, default_beta_sigma_ind, beta_std_Sigma, L, std_noise):
        if(L < 3):
            L = self._default_L
        
        # stand_noise is the noise variance applied to the standardized model
        if(std_noise == self._default_sigma0):
            var_noise = self._default_sigma0_2 * self._reward_half_range**2
            stand_noise = self._default_sigma0_2
        else:
            var_noise = std_noise**2
            stand_noise = self._default_sigma0_2 / (self._reward_half_range**2)

        default_alpha_mu_ind_no_intercept = np.copy(default_alpha_mu_ind)
        default_alpha_sigma_ind_no_intercept = np.copy(default_alpha_sigma_ind)
        default_beta_mu_ind_no_intercept = np.copy(default_beta_mu_ind)
        default_beta_sigma_ind_no_intercept = np.copy(default_beta_sigma_ind)

        # First, transform the standard deviation of alpha0 and beta to a scale of the noise variance (Eq. A.7)
        alpha0_sigma_2 = (alpha0_std_Sigma**2)/var_noise*(L-2)/L
        beta_sigma_2 = (beta_std_Sigma**2)/var_noise*(L-2)/L

        # Setup the unstandardized alpha prior means with the default (without the intercept)
        default_alpha_mu_ind_no_intercept[-1] = 0
        idx=(default_alpha_mu_ind_no_intercept>0.5)
        if(idx.sum()>0):
            idx_no_intercept=idx[:-1,:]
            alpha0_mu[idx.flatten(),:] = self._default_mu*\
                self._reward_half_range*np.ones((idx.sum(),1))/self._state_half_range[idx_no_intercept.flatten(),:]
            
        # Setup the unstandardized alpha prior variances with the default (without the intercept)
        default_alpha_sigma_ind_no_intercept[-1] = 0
        idx=(default_alpha_sigma_ind_no_intercept>0.5)
        if(idx.sum()>0):
            idx_no_intercept=idx[:-1,:]
            alpha0_sigma_2[idx.flatten()] = self._default_sigma_2*\
                np.ones((idx.sum()))/(self._state_half_range[idx_no_intercept.flatten(),0]**2) 
            
        # Setup the unstandardized beta prior means with the default (without the intercept)
        default_beta_mu_ind_no_intercept[-1] = 0
        idx_beta=(self._action_center_ind==1)
        beta_state_half_range=self._state_half_range[idx_beta.flatten(),:]
        idx=(default_beta_mu_ind_no_intercept==1)
        
        if(idx.sum()>0):
            idx_no_intercept=idx[:-1,:]
            beta_mu[idx.flatten(),:] = self._default_mu*\
                self._reward_half_range*np.ones((idx.sum(),1))/beta_state_half_range[idx_no_intercept.flatten(),:]
        
        # Setup the unstandardized beta prior variances with the default (without the intercept)
        default_beta_sigma_ind_no_intercept[-1] = 0
        idx_beta=(self._action_center_ind>0.5)
        beta_state_half_range=self._state_half_range[idx_beta.flatten(),:]
        idx=(default_beta_sigma_ind_no_intercept==1)
        
        if(idx.sum()>0):
            idx_no_intercept=idx[:-1,:]
            beta_mu[idx.flatten(),:] = self._default_mu*\
                self._reward_half_range*np.ones((idx.sum(),1))/beta_state_half_range[idx_no_intercept.flatten(),:]
            beta_sigma_2[idx.flatten()] = self._default_sigma_2*\
                np.ones((idx.sum()))/(beta_state_half_range[idx_no_intercept.flatten(),0]**2)
            
        # Setup the unstandardized alpha prior mean for the intercept
        if(default_alpha_mu_ind[-1]>0.5):
            alpha0_mu[-1,:] = self._default_mu*self._reward_half_range+self._reward_med-sum(alpha0_mu[:-1,:]*self._state_med)
        # Setup the unstandardized alpha prior variance for the intercept
        if(default_alpha_sigma_ind[-1]>0.5):
            tmp_sigma_2 = alpha0_sigma_2[:-1]*(self._state_med[:,0]**2)
            tmp = self._default_sigma_2-tmp_sigma_2.sum()
            if(tmp<0):
                alpha0_sigma_2[-1]=self._default_alpha0_sigma0_2
            else:
                alpha0_sigma_2[-1]=tmp

        idx_beta=(self._action_center_ind>0.5)
        beta_state_med=self._state_med[idx_beta.flatten(),:]

        # Setup the unstandardized beta prior mean for the intercept
        if(default_beta_mu_ind[-1]>0.5):
            beta_mu[-1,:] = self._default_mu*self._reward_half_range-sum(beta_mu[:-1,:]*beta_state_med)
        # Setup the unstandardized beta prior variance for the intercept
        if(default_beta_sigma_ind[-1]>0.5):
            tmp_sigma_2 = beta_sigma_2[:-1]*(beta_state_med[:,0]**2)
            tmp = self._default_sigma_2-tmp_sigma_2.sum()
            if(tmp<0):
                beta_sigma_2[-1]=self._default_beta_sigma0_2
            else:
                beta_sigma_2[-1]=tmp

        # Setup the transformation matrix for alpha0
        tmp = np.append(self._state_half_range[:,0],1)
        B_alpha = np.diag(tmp)
        B_alpha[-1,:-1] = self._state_med[:,0]
        Sigma_alpha = np.diag(alpha0_sigma_2)
        C_alpha = np.zeros(np.shape(alpha0_mu))
        C_alpha[-1] = -self._reward_med/self._reward_half_range
        
        # Setup the transformation matrix for alpha0
        idx_beta=(self._action_center_ind==1)
        beta_state_half_range=self._state_half_range[idx_beta.flatten(),:]
        tmp = np.append(beta_state_half_range[:,0],1)
        B_beta = np.diag(tmp)
        beta_state_med=self._state_med[idx_beta.flatten(),:]
        B_beta[-1,:-1] = beta_state_med[:,0]
        Sigma_beta = np.diag(beta_sigma_2)
        
        # Transform the mean and the variance
        stand_alpha0_mu=1/self._reward_half_range*np.matmul(B_alpha,alpha0_mu)+C_alpha
        stand_alpha0_Sigma=np.matmul(np.matmul(B_alpha,Sigma_alpha),np.transpose(B_alpha))
        stand_beta_mu=1/self._reward_half_range*np.matmul(B_beta,beta_mu)
        stand_beta_Sigma=np.matmul(np.matmul(B_beta,Sigma_beta),np.transpose(B_beta))
        

        # Now, we can setup the theta prior for the action-center version of Thompson sampling
        theta_mu=np.concatenate((stand_alpha0_mu,stand_beta_mu),axis=0)
        # the dimension of _theta_mu_ini is ( len(alpha0_mu)+2*len(beta_mu) )x1
        self._theta_mu_ini=np.concatenate((theta_mu,stand_beta_mu),axis=0)
            
        # This is where we consider the Sigma's as a scale of the noice variance
        theta_Sigma=block_diag(stand_alpha0_Sigma,stand_beta_Sigma)
        # the dimension of _theta_Sigma_ini is ( len(alpha0_mu)+2*len(beta_mu) ) x ( len(alpha0_mu)+2*len(beta_mu) )
        self._theta_Sigma_ini=block_diag(theta_Sigma,stand_beta_Sigma)

        
        self._L_ini = L
        self._noise_ini = stand_noise
        

        


    # g(S) in Peng's paper
    def baseline(self, state):
        return np.concatenate((state, np.ones((1, 1))), axis=0)

    # f(S) in Peng's paper
    def action_center(self, state):
        idx = (self._action_center_ind == 1)
        tmp = state[idx.flatten(), :]
        tmp = np.concatenate((tmp, np.ones((1, 1))), axis=0)
        return tmp

    # This is the model for generating Phi(State,Action)
    def reward_model(self, state, action, pi):
        Phi = np.concatenate((self.baseline(state), pi * self.action_center(state)), axis=0)
        Phi = np.concatenate((Phi, (action - pi) * self.action_center(state)), axis=0)
        return Phi


    # Jane: (I didn't update the below anymore... this is for initializing the parameters. If you think a new TS function will be initialized each time a decision/update is called, this can be deleted. Otherwise, please let me know.)
    # # Create all the tuned parameters from the parameters read from the web user interface
    # # This should match the "parameter_initialization" here: https://github.com/StatisticalReinforcementLearningLab/mDOT_toolbox/blob/master/TS_Toolbox_inverse_gamma_v1.py
    # def initialize_from_defaults(self):
    #     # Let's for now not set it as numpy array
    #     # We can also initialize the following as an numpy array. Not sure what we prefer. For now, I keep everything consistent.
    #     alpha0_mu = []
    #     beta_mu = []
    #     alpha0_std_sigma = []
    #     beta_std_sigma = []
    #     action_center_ind = []

    #     feature_name_list = []

    #     for key, feature in self.features.items():
    #         #index = int(key) - 1  # TODO: Why do I have to change the type on the index? and subtract 1
    #         # There might be a better way to do this. Let me try to be safe to ensure the order of the features is consistent.
    #         feature_name = feature['feature_name']
    #         feature_name_list.append(feature_name)
    #         alpha0_mu.append(float(feature['feature_parameter_alpha0_mu']))
    #         alpha0_std_sigma.append(float(feature['feature_parameter_alpha0_sigma']))
    #         if (feature['feature_parameter_beta_selected_features'] == 'yes'):
    #             beta_mu.append(float(feature['feature_parameter_beta_mu']))
    #             beta_std_sigma.append(float(feature['feature_parameter_beta_sigma']))
    #             action_center_ind.append(1)
    #         else:
    #             action_center_ind.append(0)

    #     alpha0_mu.append(float(self.standalone_parameters['alpha_0_mu_bias']))
    #     beta_mu.append(float(self.standalone_parameters['beta_sigma_bias']))
    #     alpha0_std_sigma.append(float(self.standalone_parameters['alpha_0_sigma_bias']))
    #     beta_std_sigma.append(float(self.standalone_parameters['beta_sigma_bias']))

    #     # Let's setup all the global parameters
    #     self._degree_ini = float(self.standalone_parameters['noise_degree'])
    #     self._scale_ini = float(self.standalone_parameters['noise_scale'])
    #     self._lower_clip = float(self.other_parameters['lower_clip'])
    #     self._upper_clip = float(self.other_parameters['upper_clip'])
    #     self._state_dim = len(self.features.items())  # Number of states
    #     self._action_center_ind = np.array([action_center_ind]).T  # Which of these states are tailoring variables
    #     self._alpha_len = len(alpha0_mu) + len(beta_mu)
    #     # This is for reading through the values of each feature and the validation code
    #     self._feature_name_list = feature_name_list

    #     # We can initialize theta_mu and theta_sigma here
    #     # Eventually the standardization would need to happen here
    #     # Right now we haven't changed theta_Sigma with respect to the scaling parameter of the noise
    #     theta_mu_ini = np.array([alpha0_mu + beta_mu + beta_mu]).T
    #     theta_sigma_list = alpha0_std_sigma + beta_std_sigma + beta_std_sigma
    #     theta_Sigma_ini = np.diag(np.array(theta_sigma_list) ** 2 / self._scale_ini)

    #     self._theta_mu_ini = theta_mu_ini
    #     self._theta_Sigma_ini = theta_Sigma_ini