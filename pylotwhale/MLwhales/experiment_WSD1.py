# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 18:05:03 2015
#!/usr/bin/python
@author: florencia

Runs call classification experiments generating artificial data and trying
different parameters
"""
from __future__ import print_function
import os
import argparse
import sys
import numpy as np
import time
import pdb
from collections import Counter

#from sklearn.svc import SVC
import sklearn.base as skb
import sklearn.metrics as mt
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib

import pylotwhale.MLwhales.featureExtraction as fex
import pylotwhale.MLwhales.MLtools_beta as myML
import pylotwhale.MLwhales.predictionTools as pT

#import pylotwhale.MLwhales.experimentTools as exT
from pylotwhale.MLwhales import MLEvalTools as MLvl
### load parameters
from pylotwhale.MLwhales.configs.params_WSD1 import *

###################  ASSIGNMENTS  ####################
##### OUTPUT FILES
"""
try:
    os.makedirs(oDir)
except OSError:
    pass
out_fN = os.path.join(oDir, "scores.txt")


if isinstance(predictionsDir, str):
    predictionsDir = os.path.join(oDir, "predictions")
    try:
        os.makedirs(predictionsDir)
    except OSError:
        pass


Tpipe = fex.makeTransformationsPipeline(T_settings)

## clf settings
clfStr = 'cv{}-'.format(cv)
settingsStr = "{}-{}".format(Tpipe.string, clfStr)
settingsStr += '-labsHierarchy_' + '_'.join(labsHierarchy)

## write in out file
out_file = open(out_fN, 'a')
out_file.write("#WSD1\n###---------   {}   ---------###\n".format(time.strftime("%Y.%m.%d\t\t%H:%M:%S")))
out_file.write("#" + settingsStr+'\n')
out_file.close()

## load collections
train_coll = fex.readCols(collFi_train, colIndexes=(0,1))
test_coll = np.genfromtxt(collFi_test, dtype=object)

lt = myML.labelTransformer(clf_labs)
"""


def runExperiment(train_coll, test_coll, lt, T_settings, labsHierarchy, out_fN,
                  cv, pipe_estimators, gs_grid, scoring=None,
                  param=None, predictionsDir=None):
    """Runs clf experiments
    Parameters
    ----------
        train_coll: list
        test_coll: list
        lt: ML.labelTransformer
        T_settings: list of tuples
        labelsHierachy: list of strings
        cv: cv folds
        extimators: list
            for pipline
        gs_grid: list
                    
        out_fN: str
        returnClfs: dict, Flase => clfs are not stored
        predictionsDir: str
        scoring: string or sklearn.metrics.scorer
    """

    Tpipe = fex.makeTransformationsPipeline(T_settings)
    feExFun = Tpipe.fun
    #### prepare DATA: collections --> X y
    ## compute features
    dataO = fex.wavAnnCollection2datXy(train_coll, feExFun, labsHierarchy)
    ## prepare X y data
    X0, y0_names = dataO.filterInstances(lt.classes_)  # filter for clf_labs
    X, y_names = X0, y0_names #myML.balanceToClass(X0, y0_names, 'c')  # balance classes X0, y0_names#
    y = lt.nom2num(y_names)
    labsD = lt.targetNumNomDict()
    with open(out_fN, 'a') as out_file: # print details about the dataset into status file
        out_file.write("# {} ({})\n".format( collFi_train, len(train_coll)))
        out_file.write("#label_transformer {} {}\t data {}\n".format(lt.targetNumNomDict(), 
                                                               lt.classes_, Counter(y_names)))

    X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                        test_size=testFrac,
                                                        random_state=0)

    with open(out_fN, 'a') as out_file: # print details to status file
        out_file.write("#TRAIN, shape {}\n".format(np.shape(X_train)))
        out_file.write("#TEST, shape {}\n".format(np.shape(X_test)))

    #### CLF
    pipe = Pipeline(pipe_estimators)
    gs = GridSearchCV(estimator=pipe,
                      param_grid=gs_grid,
                      scoring=scoring,
                      cv=cv,
                      n_jobs=-1)

    gs = gs.fit(X_train, y_train)
    ## best clf scores
    with open(out_fN, 'a') as out_file:
        out_file.write("#CLF\t{}\tbest score {:.3f}\n".format(str(gs.best_params_).replace('\n', ''), 
                                                              gs.best_score_))
    clf_best = gs.best_estimator_

    ## clf scores over test set
    with open(out_fN, 'a') as out_file:
        ### cv score
        cv_sc = cross_val_score(clf_best, X_test, y_test, scoring=scoring)
        out_file.write("{:2.2f}, {:2.2f}, {:.2f}, ".format(param, 100*np.mean(cv_sc),
                                                            100*2*np.std(cv_sc)))
        ### cv accuracy
        cv_acc = cross_val_score(clf_best, X_test, y_test)
        out_file.write( "{:2.2f}, {:.2f}, ".format(100*np.mean(cv_acc),
                                                   100*2*np.std(cv_acc)))
    ## print R, P an f1 for each class
    y_true, y_pred = y_test, clf_best.predict(X_test)                                                         
    MLvl.print_precision_recall_fscore_support(y_true, y_pred, out_fN)

    #### TEST collection
    ### train classifier with whole dataset
    clf = skb.clone(gs.best_estimator_) # clone to create a new classifier with the same parameters
    clf.fit(X,y)
    ### print scores
    callIx = lt.nom2num('c')
    for wavF, annF in test_coll[:]:
        A, a_names = fex.getXy_fromWavFAnnF(wavF, annF, feExFun, labsHierarchy,
                                            filter_classes=lt.classes_)
        a_true = lt.nom2num(a_names)
        a_pred = clf.predict(A)
        P = mt.precision_score(a_true, a_pred, average=None)[callIx]
        R = mt.recall_score(a_true, a_pred, average=None)[callIx]
        f1 = mt.f1_score(a_true, a_pred, average=None)[callIx]
        with open(out_fN, 'a') as out_file:
            out_file.write(", {:2.2f}, {:2.2f}, {:2.2f}".format(100*f1,
                                                                100*P, 100*R))
        if predictionsDir:
            bN = os.path.basename(annF)
            annFile_predict = os.path.join(predictionsDir,
                                           "{}_{}_{}".format(int(f1*100),
                                                             int(param), bN))
            pT.predictSoundSections(wavF, clf,  lt, feExFun, annSections=labsHierarchy, 
                                    outF=annFile_predict)


    with open(out_fN, 'a') as out_file:
            out_file.write("\n")
               
    return clf































if False:
    #### feature extraction object
    feExOb = fex.wavFeatureExtraction(featConstD) # feature extraction settings
    feature_str = feExOb.feature_str
    feExFun = feExOb.featExtrFun()
    
    #### clf settings
    clfStr = 'cv{}-{}'.format(cv, metric)
    settingsStr = "{}-{}".format(feature_str, clfStr)
    
    #### write in out file
    out_file = open(out_file_scores, 'a')
    out_file.write("\n###---------   {}   ---------###\n".format(time.strftime("%Y.%m.%d\t\t%H:%M:%S")))
    out_file.write("#" + settingsStr)
    out_file.close()
    
    #### load collection
    WavAnnCollection = fex.readCols(collFi_train, colIndexes = (0,1))
    print("\ncollection:", len(WavAnnCollection),
          "\nlast file:", WavAnnCollection[-1])
    
    #### compute features
    trainDat = fex.wavAnnCollection2datXy(WavAnnCollection, feExFun) #, wavPreprocesingT=wavPreprocessingFun)
    ## y_names train and test data
    X, y_names = trainDat.filterInstances(labs) # train
    lt = myML.labelTransformer(labs)
    y = lt.nom2num(y_names)
    labsD = lt.targetNumNomDict()
    #### train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                      test_size=testFrac, 
                                                      random_state=0)
    
    with open(out_file_scores, 'a') as out_file: # print details to status file
        out_file.write("\n#TRAIN, shape {}\n".format(np.shape(X_train)))
        out_file.write("#TEST, shape {}\n".format(np.shape(X_test))) 
    
        ## more info
        #out_file.write("#X {}, y {}\n".format( np.shape(X), np.shape(y)))
        out_file.write("#Target dict {}\t{}\n".format(labsD, trainDat.targetFrequencies()))
    
    
    ### grid search
    
    gs = GridSearchCV(estimator=pipe_estimators,
                      param_grid=gs_grid,
                      scoring=metric,
                      cv=cv,
                      n_jobs=-1)
    
    gs = gs.fit(X_train, y_train)
    
    with open(out_file_scores, 'a') as out_file:
        out_file.write(MLvl.gridSearchresults(gs))
    
    
    print(out_file_scores)
    
