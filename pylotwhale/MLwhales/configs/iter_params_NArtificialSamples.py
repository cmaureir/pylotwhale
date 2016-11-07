#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 18:05:03 2015
#!/usr/bin/python
@author: florencia
"""
#####
import numpy as np 
import os
import pylotwhale.MLwhales.experimentTools as exT

####### Iter parameters
parameter = 'NArtificialSamples' # any name does to job
paramKey = 'ensembleSettings'

a = 10
controlParams = np.arange(4, a)  # less than 5 doesn't work with CV=10

def updateParamInDict(paramDict, paramKey, param):

    paramDict[paramKey] = exT.generateData_ensembleSettings(
                                                n_artificial_samples=param)
    return paramDict

updateTestSet = False

preproStr = "{}_{}".format(parameter, a)
