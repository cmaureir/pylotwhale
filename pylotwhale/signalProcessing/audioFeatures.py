# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 12:44:09 2016

@author: florencia
"""
import pylotwhale.signalProcessing.signalTools_beta as sT
import functools
import numpy as np



######     ANNOTATIONS     #########

def getAnnWavSec(wavFi, annFi, t0Label='startTime', tfLabel='endTime', 
                 label='label'):
    '''
    read annotated sections from a waveform
    Parameters:
    ----------
    wavFi : wav file name
    annFi : annotations file (*.txt)
            if None => the whole waveform is returned
    t0Label : name of the label for the start time (used by annT.parseAupFile)
    tfLabel : name of the label for the end time (used by annT.parseAupFile)
    label : name of the label with the annotation label (used by annT.parseAupFile)
    Returns:
    -------
    sectionsLi : a list with dictionaries with the label and waveform information
        { <label>, <waveFormSection (np.array)> }
        [ { <label>, <waveFormSection> }, ... , { <label>, <waveFormSection> }]
    '''

    waveform, fs = sT.wav2waveform(wavFi) # read wav

    if annFi is None: # no annotations given
        return([{label : os.path.basename(wavFi), 'waveform' : waveform}], fs)
    else:
        sectionsLi=[]
        annLi = annT.parseAupFile(annFi) # read annotations
    for annDi in annLi:
        t0 = annDi[t0Label]
        tf = annDi[tfLabel]
        l = annDi[label]
        item = {label: l, 'waveform' : getWavSec(waveform, fs, t0, tf)}
        sectionsLi.append(item)

    return(sectionsLi, fs)

def getWavSec(waveform, fs, t0, tf):
    '''
    get wav section
    Parameters:
    ----------<
        waveform : waveform
        fs : sampling rate
        t0 : initial time
        tf : final time
    Returns:
    ------->
        waveform segment
    '''
    n0 = int(np.floor(fs * float(t0)))
    nf = int(np.ceil(fs * float(tf)))
    return(waveform[n0:nf])


def flatPartition(nSlices, vec_size):
    '''
    returns the indexes that slice an array of size vec_size into nSlices
    Parameters:
    ---------->
        nSlices : number of slices
        vec_size : size of the vector to slice
    '''
    idx = np.linspace(0, np.arange(vec_size)[-1], nSlices)
    return np.array([int(item) for item in idx])


def aupTxt2annTu(txtFi, gap='b', filterLabSet=None, l_ix=2 ):
    '''
    extracts the labels from an annotations file and retuns a list filling all time gaps
    with 'b' (backgroun noise)
    < txtFi : annotations file name (t0 \t tf \t label)
    < gap : name of the filling gap label
    < filterLabset :  list with the names of the labels to filter out
    < l_ix : index of the label to filter (2 --> sound_label)
    ------>
    > annTu : list of (sample, label) pairs
                    where sample is the first sample with the given label

    >>> WARNING!: ASSUMES NO OVERLAP BETWEEN THE LABELES <<<
    >>> ACHTUNG!: NEVER FILTER ANNOTATIONS AFTER THIS STEP <<<
    '''
    t0 = 0
    annTu=[(t0, gap)]
    with open(txtFi, 'r') as f:
        lines = f.read().splitlines()

    if filterLabSet: # filterout unwanted labels (still in the aup txt format)
            lines = [li for li in lines if li.split('\t')[l_ix] not in filterLabSet]

    for li in lines: # transform annotations into the tu-li format (for later processing)
        t0, tf, label = li.split('\t')
        annTu.append(( float(t0.replace(',','.')), label))
        annTu.append(( float(tf.replace(',','.')), gap))
    return annTu


def findLabel( stamp, stampLabelTu, i=0):
    '''
    Returns the label asociated with the given (time)stamp
    searching in the stampLabelTu
    Parameters:
    -----------
    < stamp : stamp we are interested on
                can be specified either in seconds or in frame index
                depending on the units of the stampLabelTu
    < stampLabelTu : list of (stamp, label) pairs
                first stamp with the label "label"
                the stamps are sorted
    < i : index from which we start searching
    Returns:
    --------
    > label, label of the "stamp"
    > i, index of the label
    '''
    s, l = zip(*stampLabelTu)

    ## to big stamp
    if stamp >= s[-1]:
        return l[-1], None

    ## search stamp
    while s[i] < stamp:
        i+=1

    ## first stamp with the wanted label
    if s[i] > stamp: i-=1
    return l[i], i

def setLabel(idx, annotTu):
    s, l = zip(*annotTu)
    i=0
    while s[i] < idx and i < len(s)-1 :
        i+=1

    return l[i-1], i#annoTu[]

def tuLi2frameAnnotations(tuLiAnn, m_instances, tf):
    '''
    transforms annotations
        list of tuples into --> instances annotations
    Parameters:
    tLiAnn : list of tuples (<start_time/start_frame_index>, <label>)
    m_instances : number of instances to annotate
    tf : final time/index of the file being annotated
    '''
    tstamps = np.linspace(0, tf, m_instances + 2 )[1:-1] # generate the time stamps of the instances
    targetArr = np.zeros(m_instances, dtype=object) # inicialize the target array
    i=0
    for ix in np.arange(m_instances):
        l, i = findLabel(tstamps[ix], tuLiAnn, i)
        targetArr[ix] = l
    return targetArr


#### FEATURE EXTRACTION and processing #####

def featureExtractionFun(funName=None):
    '''
    Dictionary of feature extracting functions
    that return a dictionary of features
    ------
    > feature names (if None)
    > feature function
        this functions take the waveform and return an instancited feature matrix
        m (instances) - rows
        n (features) - columns
    '''
    D = {#'welch' : welchD,
        #'bandEnergy' : bandEnergy, ## sum of the powerspectrum within a band
        'spectral' : sT.spectralRep,
        'spectralDelta' : functools.partial(sT.spectralDspecRep, order=1),
        'cepstral' : sT.cepstralRep,
        'cepsDelta' : functools.partial(sT.cepstralDcepRep, order=1), # MFCC and delta-MFCC
        'cepsDeltaDelta' : functools.partial(sT.cepstralDcepRep, order=2),
        'chroma' : sT.chromaRep,
        'melspectroDelta' : sT.melSpecDRep,
        'melspectro' : functools.partial(sT.melSpecDRep, order=0)
        }

    if funName == None: # retuns a list of posible feature names
        return D.keys()
    else:
        return D[funName] # returns function name of the asked feature


def featMatrixAnnotations(waveform, fs, annotations=None, NanInfWarning=True,
                          featExtrFun = sT.cepstralFeatures, **featExArgs):
    '''
    Combines feature extraction with annotations
        --->>> No explicit texturiztion <<<--- (see waveform2featMatrix)

    Params
    ------
    < waveform :  waveform array
    < fs :  sampling rate of the waveform
    < annotations : list with the time stamp, label pairs. The stamp must have
                second units, and this indicates the firt sample with the
                given label (stamp, label) list
    < featExtract : feature extractor function
                        {cepstralFeatures, logfbankFeatures }
    < **featArgs : arguments for estimating the features (see featExtract)
    Return
    ------
    > M : feature matrix ( n (features) x m (insatances) )
    > targetArr : target vector
    > featNames : array with the names of the features

    Example
    ----------

    NFFTexp = 9
    NFFT = 2**NFFTexp
    lFreq=0 #1000
    analysisWS=0.025
    analysisWStep=0.01
    numcep=13
    NFilt=26
    preemph=0.97
    ceplifter=22
    featConstD = { "analysisWS": analysisWS, "analysisWStep" : analysisWStep,
                "NFilt" : NFilt, "NFFT" : NFFT, "lFreq" : lFreq,
                "preemph" : preemph,
                "ceplifter" : ceplifter, "numcep" : numcep }

    featExtract = cepstralRep
    featConstD["featExtract"] = featExtract

    M0, y0_names, featN =  featMatrixAnnotations(waveForm, fs,
                                                 annotations=annotLi_t,
                                                 **featConstD)

    '''
    ## feature extraction
    if isinstance(featExtrFun, str): featExtrFun = featureExtractionFun(featExtrFun)
    M, featNames, tf, featStr = featExtrFun(waveform, fs, **featExArgs)

    m_instances, n_features = np.shape(M)
    print("m", m_instances, "n", n_features, tf)

    ## ANNOTATIONS
    ## estimate the time stamps from the instances
    tstamps = np.linspace(0, tf, m_instances + 2 )[1:-1]
    ## inicialize the labels (target array)
    targetArr = np.zeros(m_instances, dtype=object)
    print("target array", np.shape(targetArr))
    ## determine the annotAtions of the extracted instances
    if annotations:
        i=0
        for ix in np.arange(m_instances):
            l, i = findLabel(tstamps[ix], annotations, i)
            targetArr[ix] = l
    # Pxx, s2fr, s2time, im = plt.specgram(waveform, NFFT=2**8, Fs = fs)#, detrend=plt.mlab.detrend)#, pad_to=50 )

    if NanInfWarning:
        print("buggi instances:", np.max(M), np.min(M))

    return M, targetArr, featNames, featStr





def texturizeFeatures(M, nTextWS=100, normalize=True):
    '''
    computes the mean and the std over the features of M over a texture window of size nTextWS
    M : feature matrix (n_features x instances)
    tf : length of the recording in seconds
    nTextWS :   int - size of the texture window in number of samples (walk)
                array - or vector with the index values (split)
    normalize : if True, normalizes the instances
    ------>
    fM : texturized feature matrix
    t : time array
    '''

    mt, nf = np.shape(M)

    if isinstance(nTextWS, int): # walk
        ind = np.arange(0, mt - nTextWS + 1, nTextWS)
        m_instances = len(ind)
        fM = np.zeros((m_instances, 2*nf))

        for i in np.arange(m_instances):
            thisX = np.array(M[ind[i] : ind[i] + nTextWS, : ])
            if normalize : thisX /= np.max(np.abs(thisX)) #normalize each instance
            fM[i,:] = np.hstack( ( np.mean(thisX, axis=0), np.std(thisX, axis=0) ) )
        return fM

    elif isinstance(nTextWS, np.ndarray): # spliting indexes

        ind = nTextWS # slicing indexes array
        #print(ind)
        m_instances = len(ind) - 1 # #(instances) = #(slicing indexes) - 1
        fM = np.zeros((m_instances, 2*nf))

        if normalize : M /= np.max(np.abs(M), axis=0) # the whole matrix

        for i in np.arange(m_instances):
            thisX = np.array(M[ind[i] : ind[i+1]+1, : ])
            
            fM[i,:] = np.hstack( ( np.mean(thisX, axis=0), np.std(thisX, axis=0) ) )

        return fM

    #print(np.shape(fM))


    #t = np.linspace(0, tf, n)



def waveform2featMatrix(waveform, fs, textWS=0.2, normalize=True, Nslices=False,
                        annotations=None, nTextWS=False,
                        featExtrFun='cepsDelta', **featExArgs):
    '''
    1. extract audio features
    2. texturizes them
        (computing the mean and std over a texture window, see texturizeFeatures)
    3. handle annotations
    Parameters
    ----------<
    < waveform :  waveform array
    < fs :  sampling rate of the waveform
    < textWS : size of the texture window
        nTextWs is assigned here from this value.
        instead on can set Nslices
    < annotations : list with the time stamp, label pairs. The stamp can be in
                samples or time units, and this indicates the first sample with the
                given label (stamp, label) list
    < featExtrFun : feature extraction function or name (see FeatureExtractionFun)
    < **featExArgss : arguments to be used on the feature extraction
                        e.g. - NFFT, overlap, etc.
                            -- Nceps
    < Nslices : sets textWS so that the waveform is sliced in Nslices equal length segments
    Returns
    --------->
    > M : feature matrix ( m x n )
    > targetArr : target vector
    > featNames : feature names
    > featStr : string with feature extraction settings
    '''
    ## feature extraction
    if isinstance(featExtrFun, str): featExtrFun = featureExtractionFun(featExtrFun)
    M0, featNames0, tf, featStr  = featExtrFun(waveform, fs, **featExArgs)
    m0 = np.shape(M0)[0] ## number of frames

    ## set the textWS
    if Nslices is False and nTextWS is False: ### WALKING - texture window size given
        nTextWS_0 = 1.0*m0*float(textWS)/tf
        nTextWS = int(nTextWS_0) ###
        assert nTextWS >= 1, 'the texture window is too small {:.2f}'.format(nTextWS_0)
        slicingIdx = nTextWS # integer
    elif isinstance(Nslices, int) : # SPLITTING - slice the featMtx into Nslices!
        slicingIdx = flatPartition(Nslices+1, m0) # numpy array
        #print("TEST",slicingIdx)
        assert slicingIdx[-1] > 1, 'the texture window is too small %d'%slicingIdx[-1]
        textWS = slicingIdx[1] - slicingIdx[0]
        nTextWS = int(1.0*m0*float(textWS)/tf) ###
    elif isinstance(nTextWS, int): # walk!, number of frames given
        slicingIdx = nTextWS # integer
        textWS = 1.0*nTextWS*tf/m0
    else:
        assert False, 'you must give a valid summarization parameter'

    featStr+='-txWin%dms%d'%(textWS*1000, nTextWS)
    if normalize: featStr+='-TxWinNormalized'

    ## texturize features
    M = texturizeFeatures(M0, nTextWS=slicingIdx, normalize=normalize)
    featNames = [str(fn) + 'mu' for fn in featNames0] + [str(fn) + 'std' for fn in featNames0]
    m_instances, n_features = np.shape(M)

    if annotations: ## generate the targets for the instances
        targetArr = tuLi2frameAnnotations(annotations, m_instances, tf)
    else:
        targetArr = np.zeros(m_instances, dtype=object)

    return M, targetArr, featNames, featStr


def waveform2comboFeatMatrix(waveform, fs, textWS=0.2, normalize=True,
                        annotations=None,
                        featExtrFunLi=None):
    '''
    Combined feature extraction
    like waveform2featMatri() but combining different feature extraction methods
    Parameters
    ---------------
    < waveform :  waveform array
    < fs :  sampling rate of the waveform
    < textWS : size of the texture window [ms]
        nTextWs is assigned here from this value.
    < annotations : list with the time stamp
    < featExtrFun : list of features to be used
                e.g. ['spectral', 'cepstral', 'chroma']
    Returns
    --------->
    > M : feature matrix ( m_instances x n_features )
    > targetArr : target vector
    > featNames : feature names
    > featStr : string with feature extraction settings
    ----
    '''

    if featExtrFunLi == None: #use all the posible features
        featExtrFunLi = featureExtractionFun(None)

    feat = featExtrFunLi[0]
    print(feat)
    X, tArr, fNs, fStr = waveform2featMatrix(waveform, fs, textWS=textWS,
                                normalize=normalize, annotations=annotations,
                                featExtrFun=featureExtractionFun(feat))

    for feat in featExtrFunLi[1:]:
        print(feat)
        M, targetArr, featNames, featStr = waveform2featMatrix(waveform, fs, textWS=textWS,
                                normalize=normalize, annotations=annotations,
                                featExtrFun=featureExtractionFun(feat))
        X = np.hstack((X, M))
        #tArr = np.hstack((tArr, featNames))
        fNs = np.hstack((fNs, featNames))
        fStr += featStr

    return X, tArr, fNs, fStr



def tsFeatureExtraction(y, fs, annotations=None, textureWS=0.1, textureWSsamps=0,
                        overlap=0, normalize=True, featExtr='welch', **kwargs):
    '''
    returns  a time series with the spectral energy every textureWS (seconds)
    overlap [0,1)
    < y : signal (waveform)
    < fs : sampling rate
    < annotations : annotations tuple
    * optional
    < textureWS : texture window in seconds
    < textureWSsamps : texture window in number of samples (This has priority over textureWS)
    < normalize : --- not working ---
    < overlap : [0,1)
    < **kwargs : of the featExtract metod
    -->
    > feat_df : time series of the powerspectral density
    > targetArr : time interval of the texture window
    '''

    ## set set (size of the texture window in samples)
    if textureWS: step = 2**np.max((2, int(np.log(fs*textureWS)/np.log(2)))) # as a power of 2
    if textureWSsamps: step = textureWSsamps

    featExtrFun = featureExtractionFun(featExtr)

    overl = int(step*overlap)
    feat_df = pd.DataFrame()
    targetArr=[]
    ix0 = 0
    ix = step

    print("step:", step, "overlap", overl, "len signal", len(y),
          "step (s)", 1.0*step/fs)
    while ix < len(y):
        yi = y[ix0:ix] # signal section
        ix0 = ix - overl
        ix = ix0 + step
        di = featExtrFun(yi, fs)
        feat_df = feat_df.append(di, ignore_index=True)  # append the energy
        if annotations : targetArr.append(setLabel(ix0 + step/2, annotations))

    return(feat_df, targetArr)


#####   FILE CONVERSIONS   #####

def mf2wavLi(mf_file):
    '''
    marsyas collection (mf) --> list of waves
    reads the list of wav files in a marsyas collecion file and returns them
    in a list
    '''
    wF_li = []

    with open(mf_file) as f:
        for line in f:
             wavF = line.split('.wav')[0]+'.wav' # parse wav file name
             wF_li.append(wavF)

    return wF_li


    
 ##  summarise