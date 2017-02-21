#!/usr/bin/python

from __future__ import print_function, division
#import sys
import numpy as np
#import os
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import pylotwhale.utils.dataTools as daT

#import pylotwhale.NLP.ngramO_beta as ngr


#import scikits.audiolab as au
#import warnings


"""
tools for the preparation of annotated files
"""

def y_histogram(y, range=(0,1.5), Nbins=None, oFig=None, figsize=None,
                 plTitle=None, xl=r"$\tau _{ict}$ (s)",  max_xticks = None):
    ## remove nans and infs
    y = y[~np.logical_or(np.isnan(y), np.isinf(y))]
    ## define number of bins
    if Nbins is None: Nbins = int(len(y)/10)
    ## plot
    fig, ax = plt.subplots(figsize=figsize)
    #plt.figure(figsize=figsize)
    ax.hist(y, range=range, bins=Nbins)
    ax.set_xlabel(xl)  # in ({}, {}) s".format(rg[0], rg[1]))
    if isinstance(plTitle, str): # title
        ax.set_title(plTitle)
    if isinstance(range, tuple): # delimit plot
        ax.set_xlim(range)
    
    if max_xticks > 1:    
        xloc = plt.MaxNLocator(max_xticks)
        ax.xaxis.set_major_locator(xloc)

    
    ## savefig
    if isinstance(oFig, str): fig.savefig(oFig, bbox_inches='tight')
    #print(oFig)
    return fig, ax
    
    
def pl_ic_bigram_times(df0, my_bigrams, ignoreKeys='default', label='call', oFig=None, 
                       violinInner='box', yrange='default', ylabel='time (s)',
                       minNumBigrams=5):
    '''violin plot of the ict of a my_bigrams
    Parameters:
    -----------
        df0 : pandas dataframe wirth ict column
        mu_bigrams : sequence to search for
        ignoteKeys : 'default' removes  ['_ini', '_end']
        label : type of sequence
        oFig : output figure
        violinInner : viloin lor parameter
        yrange : 'default' (0, mu*2)
    '''

    if ignoreKeys == 'default': ignoreKeys = ['_ini', '_end']

    topBigrams = daT.removeFromList(daT.returnSortingKeys(Counter(my_bigrams)), ignoreKeys)
    bigrTimes=[]
    bigrNames=[]

    for seq in topBigrams:
        df = daT.returnSequenceDf(df0, seq, label=label)
        #print(len(df))
        ict = df.ict.values
        if len(ict) > minNumBigrams:
            #bigrTimes[tuple(seq)] = ict[ ~ np.isnan(ict)]
            bigrTimes.append(ict[ ~ np.isnan(ict)])
            bigrNames.append(seq)

    kys = ["{}{}".format(a,b) for a, b in bigrNames ]
    #sns.violinplot( bigrTimes, names=kys, inner=violinInner)
    sns.boxplot( bigrTimes, names=kys)

    if yrange == 'default':
        meanVls = [np.mean(item) for item in bigrTimes if len(item) > 1]
        yrange = (0, np.mean(meanVls))
    plt.ylim(yrange)
    plt.ylabel(ylabel)
    plt.savefig(oFig, bbox_inches='tight')


def pl_calling_rate(df, t_interval=10, t0='t0', xL='time, [s]', yL=r'$\lambda$',
                    max_xticks = None, plTitle=None, oFig=None):
    """plots the calling rate: # calls/t_interval for one tape dataframe"""
    call_t = df[t0].values
    ti = 0
    ## define time bins
    times_arr = np.arange(t_interval, call_t[-1]+t_interval, t_interval)
    ## inicialise the calling rate for each time bin with zeros
    call_rate = np.zeros(len(times_arr))
    for (i, tf) in enumerate(times_arr): # count the number of calls in each timebin
        call_rate[i] = len(call_t[np.logical_and(call_t > ti, call_t < tf)])
        ti = tf

    fig, ax = plt.subplots()
    ax.plot(times_arr, call_rate, marker='x')
    ax.set_xlabel(xL)
    ax.set_ylabel(yL)
    plt.autoscale()
    
    if max_xticks > 1:
        xloc = plt.MaxNLocator(max_xticks)
        ax.xaxis.set_major_locator(xloc)

    if plTitle: 
        ax.set_title(plTitle)

    if oFig: 
        fig.savefig(oFig, bbox_inches='tight')#, bbox_inches='tight')    
                
def pl_ictHist_coloured(ict, ict_di, bigrs, Nbins, rg=None, 
                      xL=r'$\tau _{ict}, [s]$', oFig=None):
        """
        Parameters:
        -----------
        ict: array, series
            all ict values, eg. df['ict_end_start']
        ict_di: dict
            ict by bigram
        bigrs: list
            with the bigram names,
            ngr.selectBigramsAround_dt(ict_di, (ixc_min, ixc_max), minBigr)
        rg: tuple
            hitogram range rg = (ixc_min, ixc_max)

        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.hist(ict, range=rg,
                label='other', alpha=0.4, color='gray', bins=Nbins)

        cmap = plt.cm.gist_rainbow(np.linspace(0, 1, len(bigrs)))
        ax.hist([ict_di[''.join(item)] for item in bigrs[:]],
                stacked=True, range=rg, label=bigrs, rwidth='stepfilled',
                bins=Nbins, color=cmap)
        ax.set_xlabel(xL)
        plt.legend()

        if oFig: fig.savefig(oFig)

        return fig, ax










  