# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 18:56:27 2016

@author: florencia
"""

from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.svm import SVC
import numpy as np


class clfSettings():
    def __init__(self, clf_name, fun, grid_params_di):
        self.clf_name = clf_name
        self.fun = fun
        self.grid_params_di = grid_params_di


#SVC 
gamma_range = [ 0.1, 1.0]
pen_range = [ 0.1, 1.0, 10.0, 100]
param_grid_di = {'clf__C': pen_range,
                'clf__gamma': gamma_range}
                
svc_rbf =  clfSettings('svc_rbf', SVC(), param_grid_di)

#RF
ests_range = np.array([50, 100])
param_grid_di={}#"max_depth": [3, None],
              #"bootstrap": [True, False]}
#              "n_estimators": ests_range}
              
random_forest = clfSettings('rf', RandomForestClassifier(), param_grid_di)
