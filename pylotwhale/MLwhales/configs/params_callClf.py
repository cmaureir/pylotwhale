#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""
SETTINGS
========

Parameters to be used in classification experiment:

runExperiment_prototypeCallType-clf.py

@author: florencia
"""

##############################
########   SETTINGS   ########
##############################

#### Feature extraction 
#fs = 48000
fs = 44100 # orchive
T_settings = []

## preprocessing
filt='band_pass_filter'
filtDi={"fs":fs, "lowcut":0, "highcut":22000, "order":5}
#T_settings.append(('bandFilter', (filt, filtDi)))

prepro='maxabs_scale'
preproDict = {}
T_settings.append(('normaliseWF', (prepro, preproDict)))

#### features dictionary
auD = {}
auD["sRate"] = fs
NFFTpow = 8; auD["NFFT"] = 2**NFFTpow
overlap = 0.5; auD["overlap"] = overlap
#Nslices = 4; auD["Nslices"] = Nslices
#audioF='spectral'#; auD["featExtrFun"]= featExtract
#n_mels = 64; auD["n_mels"]= n_mels; audioF='melspectro'; 
Nceps=2**5; auD["Nceps"]= Nceps; audioF='cepstral'
T_settings.append(('Audio_features', (audioF, auD)))

summDict = {'Nslices': 4, 'normalise': True}
summType = 'splitting'
T_settings.append(('summ', (summType, summDict)))

##### clf
testFrac = 0.2
metric='accuracy'
cv = 10

## clf settings
### inicialise Clf settings
paramsDi={}
pipe_estimators=[]
from pylotwhale.MLwhales.clf_pool import svc_rbf as clf_settings
pipe_estimators.append(('clf',  clf_settings.fun))
paramsDi.update(clf_settings.grid_params_di)
gs_grid = [paramsDi] # clfSettings.grid_params #

#### Classes                
callSet = ['126i', '130', '127', '129', '128i', '131i', '093ii']

##### FILES
## INPUT -> collection files
filesDi = {}
#collFi_train 
filesDi['train'] = '/home/florencia/whales/data/orchive/flo/data/wavLabelColl-call-catalog-xsilence.txt'
#'/home/florencia/whales/MLwhales/callClassification/data/collections/Vocal-repertoire-catalogue-Pilot-whales-Norway-callsL10.txt'

## OUTPUT -> DIR
#oDir = 
import pylotwhale.MLwhales.featureExtraction as fex
settings_str = fex.makeTransformationsPipeline(T_settings).string + clf_settings.clf_name
filesDi['outDir'] = '/home/florencia/whales/data/orchive/flo/data/experiments/{}'.format(settings_str)
#'/home/florencia/whales/MLwhales/callClassification/data/experiments/fullRep-cutWavs/{}'.format(settings_str)





