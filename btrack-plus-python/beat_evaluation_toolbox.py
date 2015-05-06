#! /usr/bin/env python

# Implementations various beat tracking evaluation methods
# All methods were derived from Matlab implementations by Matthew Davies
# Python versions by Adam Stark, 2011-2012
# adamstark.uk@gmail.com

import numpy as np
import os, os.path


#######################################################################################
######################## Beat Tracking Evaluation Paramaters ##########################
#
# Description:
# Specify parameters for different beat evaluation methods.
#       
# (c) 2009 Matthew Davies
#
# (Python implementation by Adam Stark 2011-2012)
#
#######################################################################################

# ignore all beats up to this point in seconds
minBeatTime = 5;
# size of tolerance window for fmeasure
fMeasure_thresh = 0.07;
# standard deviation of gaussian error function
cemgilAcc_sigma = 0.04;
# range of time-limited cross-correlation for pscore
pScore_thresh = 0.2;
# maximum allowed relative beat error
gotoAcc_thresh = 0.35;
# maximum allowed mean beat error
gotoAcc_mu = 0.2;
# maximum allowed standard deviation of beat error
gotoAcc_sigma = 0.2;
# size of tolerance window for beat phase in continuity based evaluation
continuityBased_phaseThresh = 0.175;
# size of tolerance window for beat period in continuity based evaluation
continuityBased_periodThresh = 0.175;
# number of histogram bins for information gain method
informationGain_numBins = 40;
# range of fixed time offsets over which to test beat tracking algorithms  
generateResults_offsetRange = np.array(range(-6,7),'float64')*0.01161
# number of per file evaluation scores to find
generateResults_numMethods = 9;
# flag to indicate whether to truncate beats to range of annotations
generateResults_truncate = 0;
# flag to indicate whether to show plots or not
generateResults_plotting = 1;
# number of bootstrap samples to take
confidenceInterval_numSamples = 1000;
# confidence interval
confidenceInterval_interval = 0.95;


#######################################################################################
################################# Evaluate On A Database ##############################
#   
#  Description:
#  Evaluate beats on a whole database
#   
#  Inputs: 
#  annsList - a list of numpy arrays containing ground truth annotations (in seconds)
#  beatsList - a list of numpy arrays containing estimated beat locations (in seconds)
#  offset - a fixed time offset that can be added to each beat
#  truncate - flag to indicate whether to remove all beats outside of the range of annotations
#     
#  (c) 2009 Matthew Davies
#
# (Python implementation by Adam Stark 2011-2012)
#
#######################################################################################

def evaluate_db(annsList,beatsList,measures = 'all',doCI = False):   
        
    # if annotations and beats are not lists of the same length
    if (len(annsList) < len(beatsList)):
        print "Error: not enough annotations for beat sequences"
        return 0
    
    # get the number of files
    numFiles = len(beatsList)

    scores_fMeasure = []
    scores_cemgilAcc = []
    scores_gotoAcc = []  
    scores_pScore = []            
    scores_cmlC = []   
    scores_cmlT = []   
    scores_amlC = []   
    scores_amlT = []   
    scores_infoGain = []              
    scores_amlCem = []


    # for each file 
    for i in range(numFiles):
        print "Evaluating file ",(i+1)
            
        ################### if we are calculating all measures #################
        if ('all' in measures):
            # get all scores
            all_scores_single = evaluate(annsList[i],beatsList[i])
            
            # if it is the first file
            if i == 0:
                scores = all_scores_single     
            else:
                scores = np.vstack([scores,all_scores_single]) 
    
        ###################### if we are calculating fMeasure ####################        
        if ('fMeasure' in measures):
            [f,p,r,a] = fMeasure(annsList[i],beatsList[i])
            scores_fMeasure.append(f)

        ###################### if we are calculating cemgilAcc ####################        
        if ('cemgilAcc' in measures):
            scores_cemgilAcc.append(cemgilAcc(annsList[i],beatsList[i]))

        ###################### if we are calculating gotoAcc ####################        
        if ('gotoAcc' in measures):
            scores_gotoAcc.append(gotoAcc(annsList[i],beatsList[i]))

        ###################### if we are calculating pScore ####################        
        if ('pScore' in measures):
            scores_pScore.append(pScore(annsList[i],beatsList[i]))

        ########## if we are calculating continuity based measures #############        
        if ('continuity' in measures):
            [s_cmlC,s_cmlT,s_amlC,s_amlT] = continuityBased(annsList[i],beatsList[i])
            scores_cmlC.append(s_cmlC)
            scores_cmlT.append(s_cmlT)
            scores_amlC.append(s_amlC)
            scores_amlT.append(s_amlT)

        ###################### if we are calculating information gain ####################        
        if ('infoGain' in measures):
            [I,bins] = informationGain(annsList[i],beatsList[i])
            scores_infoGain.append(I)

        ###################### if we are calculating amlCem ####################        
        if ('amlCem' in measures):
            scores_amlCem.append(amlCem(annsList[i],beatsList[i]))

        
    if ('all' in measures):
            # get the average scores across files            
            scores_mean = np.average(scores,axis=0)
                

    print " "
    print "--------------- Results ------------------"                
    if ('all' in measures):
        # print out all scores

        print "fMeasure:  %.2f" % scores_mean[0]
        print "cemgilAcc:  %.2f" % scores_mean[1]
        print "gotoAcc:  %.2f" % scores_mean[2]
        print "pScore:  %.2f" % scores_mean[3]
        print "cmlC:  %.2f   cmlT:  %.2f   amlC:  %.2f   amlT:  %.2f" % (scores_mean[4],scores_mean[5],scores_mean[6],scores_mean[7])
        print "infoGain:  %.2f" % scores_mean[8]
        print "amlCem:  %.2f" % scores_mean[9]

    if ('fMeasure' in measures):
        # print out fMeasure
        print "fMeasure:  %.2f" % np.array(scores_fMeasure).mean()

    if ('cemgilAcc' in measures):
        # print out cemgilAcc
        print "cemgilAcc:  %.2f" % np.array(scores_cemgilAcc).mean()

    if ('gotoAcc' in measures):
        # print out gotoAcc
        print "gotoAcc:  %.2f" % np.array(scores_gotoAcc).mean()
    
    if ('pScore' in measures):
        # print out pScore
        print "pScore:  %.2f" % np.array(scores_pScore).mean()

    if ('continuity' in measures):
        # print out continuity based measures
        r_cmlC = np.array(scores_cmlC).mean()
        r_cmlT = np.array(scores_cmlT).mean()
        r_amlC = np.array(scores_amlC).mean()
        r_amlT = np.array(scores_amlT).mean()        
        print "cmlC:  %.2f   cmlT:  %.2f   amlC:  %.2f   amlT:  %.2f" % (r_cmlC,r_cmlT,r_amlC,r_amlT)

    if ('infoGain' in measures):
        # print out infoGain
        print "infoGain:  %.2f" % np.array(scores_infoGain).mean()                    
                
    if ('amlCem' in measures):
        # print out amlCem
        print "amlCem:  %.2f" % np.array(scores_amlCem).mean()
    
    print "------------------------------------------"
    print " "



    # print confifence intervals
    if (doCI):
        
        print " "
        print "---------- Confidence Intervals ----------" 
        
        if ('all' in measures):
            [lci,uci] = confidenceIntervals(np.array(scores.transpose()[0]))
            print "fMeasure: [%.2f,%.2f]" % (lci,uci) 

            [lci,uci] = confidenceIntervals(np.array(scores.transpose()[1]))
            print "cemgilAcc: [%.2f,%.2f]" % (lci,uci) 

            [lci,uci] = confidenceIntervals(np.array(scores.transpose()[2]))
            print "gotoAcc: [%.2f,%.2f]" % (lci,uci) 


            [lci,uci] = confidenceIntervals(np.array(scores.transpose()[3]))
            print "pScore: [%.2f,%.2f]" % (lci,uci) 

            [l_cmlC,u_cmlC] = confidenceIntervals(np.array(scores.transpose()[4]))
            [l_cmlT,u_cmlT] = confidenceIntervals(np.array(scores.transpose()[5]))
            [l_amlC,u_amlC] = confidenceIntervals(np.array(scores.transpose()[6]))
            [l_amlT,u_amlT] = confidenceIntervals(np.array(scores.transpose()[7]))            
            print "cmlC: [%.2f,%.2f] cmlT: [%.2f,%.2f] amlC: [%.2f,%.2f] amlT: [%.2f,%.2f]" % (l_cmlC,u_cmlC,l_cmlT,u_cmlT,l_amlC,u_amlC,l_amlT,u_amlT)

            [lci,uci] = confidenceIntervals(np.array(scores.transpose()[8]))
            print "infoGain: [%.2f,%.2f]" % (lci,uci)                    

            [lci,uci] = confidenceIntervals(np.array(scores.transpose()[9]))
            print "amlCem: [%.2f,%.2f]" % (lci,uci)


        if ('fMeasure' in measures):
            [lci,uci] = confidenceIntervals(np.array(scores_fMeasure))
            print "fMeasure: [%.2f,%.2f]" % (lci,uci) 

        if ('cemgilAcc' in measures):
            [lci,uci] = confidenceIntervals(np.array(scores_cemgilAcc))
            print "cemgilAcc: [%.2f,%.2f]" % (lci,uci) 

        if ('gotoAcc' in measures):
            [lci,uci] = confidenceIntervals(np.array(scores_gotoAcc))
            print "gotoAcc: [%.2f,%.2f]" % (lci,uci) 

        if ('pScore' in measures):
            [lci,uci] = confidenceIntervals(np.array(scores_pScore))
            print "pScore: [%.2f,%.2f]" % (lci,uci) 

        if ('continuity' in measures):      
            [l_cmlC,u_cmlC] = confidenceIntervals(np.array(scores_cmlC))
            [l_cmlT,u_cmlT] = confidenceIntervals(np.array(scores_cmlT))
            [l_amlC,u_amlC] = confidenceIntervals(np.array(scores_amlC))
            [l_amlT,u_amlT] = confidenceIntervals(np.array(scores_amlT))            
            print "cmlC: [%.2f,%.2f] cmlT: [%.2f,%.2f] amlC: [%.2f,%.2f] amlT: [%.2f,%.2f]" % (l_cmlC,u_cmlC,l_cmlT,u_cmlT,l_amlC,u_amlC,l_amlT,u_amlT)

        if ('infoGain' in measures):
            [lci,uci] = confidenceIntervals(np.array(scores_infoGain))
            print "infoGain: [%.2f,%.2f]" % (lci,uci)                    

        if ('amlCem' in measures):
            [lci,uci] = confidenceIntervals(np.array(scores_amlCem))
            print "amlCem: [%.2f,%.2f]" % (lci,uci)

        print "------------------------------------------"
        print " "

#######################################################################################
################################# Evaluation Wrapper ##################################
#   
#  Description:
#  Evaluation wrapper function to get scores for all evaluation methods
#   
#  Inputs: 
#  anns - ground truth annotations (in seconds)
#  beats - estimated beat locations (in seconds)
#  offset - a fixed time offset that can be added to each beat
#  truncate - flag to indicate whether to remove all beats outside of the range of annotations
#
#  Ouputs: 
#  scores - beat tracking scores for each evaluation method 
#  binVals - beat error histogram bin values 
#     
#  (c) 2009 Matthew Davies
#
# (Python implementation by Adam Stark 2011-2012)
#
#######################################################################################

#def evaluate(anns,beats,params,offset,truncate):
def evaluate(anns,beats):   
    
    scores = np.zeros(10)

    [scores[0],p,r,a] = fMeasure(anns,beats)
    scores[1] = cemgilAcc(anns,beats)
    scores[2] = gotoAcc(anns,beats)
    scores[3] = pScore(anns,beats)
    [scores[4],scores[5],scores[6],scores[7]] = continuityBased(anns,beats)
    [scores[8],binVals] = informationGain(anns,beats)
    scores[9] = amlCem(anns,beats)

    return scores




#######################################################################################
############################# Continuity Based Evaluation #############################
#
#  Description:
#  Calculate the continuity based accuracy values as used in (Hainsworth, 2004) and (Klapuri et al, 2006)
#   
#  Inputs: 
#  anns - sequence of ground truth beat annotations (in seconds)
#  beats - sequence of estimated beat times (in seconds)
#   
#  Ouputs: 
#  cmlC - beat tracking accuracy, continuity required at the correct metrical level 
#  cmlT - beat tracking accuracy, continuity not required at the correct metrical level
#  amlC - beat tracking accuracy, continuity required at allowed metrical levels 
#  amlT - beat tracking accuracy, continuity not required at allowed metrical levels
#   
#  References:
#  S. Hainsworth, "Techniques for the automated analysis of musical audio," Ph.D. dissertation, Department of Engineering, Cambridge University, 2004.
#  A. P. Klapuri, A. Eronen, and J. Astola, "Analysis of the meter of acoustic musical signals," IEEE Transactions on Audio, Speech and Language Processing, vol. 14, no. 1, pp. 342-355, 2006.
#
# (c) 2009 Matthew Davies
#
# (Python implementation by Adam Stark 2011-2012)
#
#######################################################################################


def continuityBased(anns,beats):
    
    # remove beats and annotations that are within the first 5 seconds
    anns = anns[np.where(anns >= minBeatTime)]
    beats = beats[np.where(beats >= minBeatTime)]
            
    # Check if there are any beats, if not then exit
    if beats.size < 2:
        print "beat sequence is empty or too short, assigning zero to all outputs [cmlC,cmlT,amlC,amlT]"
        cmlC = 0;
        cmlT = 0;
        amlC = 0;
        amlT = 0;
        return [cmlC,cmlT,amlC,amlT]

    # also check that the beat times are in seconds and not any other time units
    if (max(beats) > 1000) or (max(anns) > 1000):
        print "either beats or annotations are not in seconds, please rectify. for now assigning zero to all outputs [cmlC,cmlT,amlC,amlT]"
        cmlC = 0;
        cmlT = 0;
        amlC = 0;
        amlT = 0;
        return [cmlC,cmlT,amlC,amlT]
            
    # make shorthand variables to hold thresholds
    p = continuityBased_phaseThresh;
    t = continuityBased_periodThresh;

    # create a set of annotations at double the tempo
    xi = np.array(range(1,len(anns)+1))
    yi = np.array(range(2,(len(anns)*2)+1),'float64')/2
    doubleAnns = np.interp(yi,xi,anns) 
    
    # make different variants of annotations
    
    testAnns = []
    
    # normal annotations
    testAnns.append(anns)
    # off-beats 
    testAnns.append(doubleAnns[1::2])
    # double tempo
    testAnns.append(doubleAnns)
    # half tempo odd-beats (i.e. 1,3,1,3)
    testAnns.append(anns[0::2])
    # half tempo even-beat (i.e. 2,4,2,4)
    testAnns.append(anns[1::2])
    
    totAcc = np.zeros(len(testAnns))
    contAcc = np.zeros(len(testAnns))
        
    # loop analysis over number of variants on annotations
    for j in range(len(testAnns)):
        [totAcc[j],contAcc[j]] = ContinuityEval(testAnns[j],beats,t,p);

    # assign the accuracy scores
    cmlC = contAcc[0];
    cmlT = totAcc[0];
    amlC = max(contAcc);
    amlT = max(totAcc);


    return [cmlC,cmlT,amlC,amlT]



# sub-function for calculating continuity-based accuracy
def ContinuityEval(anns,beats,t,p):
        
    checkanns = np.zeros(max(anns.size,beats.size))
    checkbeats = np.zeros(max(anns.size,beats.size))
    
    cond = 0.
    
    for i in range(beats.size):
        cond = 0
        # look for nearest annotation to current beat
        diff = abs(beats[i]-anns)  
        a = diff.min()                  # get distance to nearest annotation
        b = diff.argmin()               # get index of nearest annotation
        
        if (checkanns[b] == 1):         # if we've already used this annotation..
            cond = 0
        else:
            if (i==0) or (b==0): # either first beat or first annotation, look forward on both
                if (abs(a/(anns[b+1]-anns[b])) < p) and (abs(1.-((beats[i+1]-beats[i])/(anns[b+1]-anns[b]))) < t):
                    checkanns[b] = 1
                    cond = 1
            else:                # not first beat or first annotation, so can look backwards
                if (abs(a/(anns[b]-anns[b-1])) < p) and (abs(1.-((beats[i]-beats[i-1])/(anns[b]-anns[b-1]))) < t):
                    checkanns[b] = 1
                    cond = 1
         
                        
        # for i^th beat what is the condition
        checkbeats[i] = np.float(cond)
    
    counts = [] # to hold length of continuously correct segments
    ct=0 # counter
                
    for i in range(checkbeats.size):                # loop over the number of beats
        if (checkbeats[i] == 1):                    # verify if beat 'i' was correct
            ct=ct+1                                 # if so, increment the counter
        else:                                       # if not, then store the result and reset the counter
            counts.append(ct)                       # store number of correct beats
            ct=0                                    # reset counter    
    
    # in case every beat was correct, append the last value of the count
    counts.append(ct)
                
    totAcc = 100.0*(np.sum(checkbeats)/np.float(checkbeats.size));
    contAcc = 100.0*(np.float(max(counts))/np.float(checkbeats.size));
    return [totAcc,contAcc]




#######################################################################################
############################# Cemgil et al. Accuracy Value ############################
#   
#  Description:
#  Calculate the Cemgil et al's accuracy value as used in (Cemgil et al, 2001).
#   
#  Inputs: 
#  anns - sequence of ground truth beat annotations (in seconds)
#  beats - sequence of estimated beat times (in seconds)
#   
#  Ouputs: 
#  a - beat tracking accuracy 
#   
#  References:
#  A. T. Cemgil, B. Kappen, P. Desain, and H. Honing, "On tempo tracking: Tempogram representation and Kalman filtering," Journal Of New Music Research, vol. 28, no. 4, pp. 259-273, 2001
#   
# (c) 2009 Matthew Davies
#
# (Python implementation by Adam Stark 2011-2012)
#
#######################################################################################

def cemgilAcc(anns,beats):
    
    # remove beats and annotations that are within the first 5 seconds
    anns = anns[np.where(anns >= minBeatTime)]
    beats = beats[np.where(beats >= minBeatTime)]
    
    # Check if there are any beats, if not then exit
    if beats.size == 0:
        print "beat sequence is empty, assigning zero to all outputs [a]"
        a = 0
        return a
    
    # also check that the beat times are in seconds and not any other time units
    if (max(beats) > 1000) or (max(anns) > 1000):
        print "either beats or annotations are not in seconds, please rectify."
        a = 0
        return a

    # get standard deviation for Gaussian error function
    sigma = cemgilAcc_sigma

    # beat accuracy initially zero
    a = 0;

    
    for i in range(anns.size):
        # find the closest beat to each annotation
        beatDiffAll = abs(anns[i] - beats)          # get the distance of the annotation to all beats
        beatDiff = beatDiffAll.min()                # get time difference with the closest beat
        
        # work out the value on the gaussian error function and add to the cumulative sum
        #a = a + exp(-(beatDiff.^2)/(2*(sigma^2)));
        a = a + np.exp(-np.power(beatDiff,2.0) / (2.0*np.power(sigma,2.0)))

    # normalise by the mean of the number of annotations and beats
    a = a/(0.5*(np.float(beats.size) + np.float(anns.size)))

    # put into the range 0 to 100%
    a = a*100.0;

    return a




#######################################################################################
################ Cemgil Accuracy with Allowed Metrical Levels #########################
#   
#  Description:
#  Calculate Cemgil accuracy but allowing for continuity-based allowed metrical levels
#   
#  Inputs: 
#  anns - sequence of ground truth beat annotations (in seconds)
#  beats - sequence of estimated beat times (in seconds)
#   
#  Ouputs: 
#  amlCem - beat tracking accuracy at allowed metrical levels
#   
# (c) 2009 Matthew Davies
#
# (Python implementation by Adam Stark 2011-2012)
#
#######################################################################################

def amlCem(anns,beats):

    # remove beats and annotations that are within the first 5 seconds
    anns = anns[np.where(anns >= minBeatTime)]
    beats = beats[np.where(beats >= minBeatTime)]

    # Check if there are any beats, if not then exit
    if beats.size == 0:
        print "beat sequence is empty, assigning zero to all outputs [amlCem]"
        amlCem = 0
        return amlCem

    # also check that the beat times are in seconds and not any other time units
    if (max(beats) > 1000) or (max(anns) > 1000):
        print "either beats or annotations are not in seconds, please rectify."
        amlCem = 0
        return amlCem


    # create a set of annotations at double the tempo
    xi = np.array(range(1,len(anns)+1))
    yi = np.array(range(2,(len(anns)*2)+1),'float64')/2
    doubleAnns = np.interp(yi,xi,anns) 

    # make different variants of annotations

    testAnns = []

    # normal annotations
    testAnns.append(anns)
    # off-beats 
    testAnns.append(doubleAnns[1::2])
    # double tempo
    testAnns.append(doubleAnns)
    # half tempo odd-beats (i.e. 1,3,1,3)
    testAnns.append(anns[0::2])
    # half tempo even-beat (i.e. 2,4,2,4)
    testAnns.append(anns[1::2])

    amlCemAcc = np.zeros(len(testAnns))

    # loop analysis over number of variants on annotations
    for j in range(len(testAnns)):
        amlCemAcc[j] = cemgilAcc(testAnns[j],beats);

    # score is maximum across all annotations
    amlCem = max(amlCemAcc)

    return amlCem





#######################################################################################
################################## F-MEASURE ##########################################
#
#  Description:
#  Calculate the F-measure as used in (Dixon, 2006) and (Dixon, 2007).
#   
#  Inputs: 
#  anns - sequence of ground truth beat annotations (in seconds)
#  beats - sequence of estimated beat times (in seconds)
#  params - structure of beat evaluation parameters
#   
#  Ouputs: 
#  f - the F-measure
#  p - precision
#  r - recall
#  a - Dixon's related accuracy measure from (Dixon, 2001)
#   
#  References:
#  S. Dixon, "Automatic extraction of tempo and beat from expressive performances," Journal of New Music Research, vol. 30, pp. 39-58, 2001.
#  S. Dixon, "Onset detection revisited," in Proceedings of 9th International Conference on Digital Audio Effects (DAFx), Montreal, Canada, pp. 133-137, 2006.
#  S. Dixon, "Evaluation of audio beat tracking system beatroot," Journal of New Music Research, vol. 36, no. 1, pp. 39-51, 2007.
#   
# (c) 2009 Matthew Davies
#
# (Python implementation by Adam Stark 2011-2012)
#
#######################################################################################

def fMeasure(anns,beats):
    
    # remove beats and annotations that are within the first 5 seconds
    anns = anns[np.where(anns >= minBeatTime)]
    beats = beats[np.where(beats >= minBeatTime)]
    
    # Check if there are any beats, if not then exit
    if beats.size == 0:
        print "beat sequence is empty, assigning zero to all outputs [f,p,r,a]"
        f = 0
        p = 0
        r = 0
        a = 0
        return [f,p,r,a]
    
    # also check that the beat times are in seconds and not any other time units
    if (max(beats) > 1000) or (max(anns) > 1000):
        print "either beats or annotations are not in seconds, please rectify."
        f = 0
        p = 0
        r = 0
        a = 0
        return [f,p,r,a]


    # get the threshold parameter for the tolerance window
    delta = fMeasure_thresh;

    # number of false positives
    fp = 0;

    # number of false negatives
    fn = 0;

    # number of correct detections
    hits= 0;

    for i in range(anns.size):
        # set up range of tolerance window 
        windowMin = anns[i] - delta;
        windowMax = anns[i] + delta;

        # find those beats which are in the range of the tolerance window
        #[a1,a2,a3] = find(and(beats>=windowMin, beats<=windowMax));
        beatsinwindow = []
        beatstoadd = []
        for j in range(beats.size):
            if (beats[j] >= windowMin) and (beats[j] <= windowMax):
                beatstoadd.append(j)
        

        # now remove these beats so it can't be counted again
        for k in range(len(beatstoadd)):
            beatsinwindow.append(beatstoadd[k])
            beats = np.delete(beats,beatstoadd[k])

        if (len(beatsinwindow) == 0):      # no beats in window, therefore it's a false negative
            fn = fn +1;
        elif(len(beatsinwindow) > 1):       # false positive case, more than one beat in a tolerance window
            hits = hits+1;
            fp  = fp+ 1;
        else:                               # only one beat in the tolerance window therefore a correct detection
            hits = hits+1;
    
    # add any remaining beats to the number of false positives
    fp = fp + beats.size

    
                
    # calculate precision, p
    if ((hits+fp) > 0):
        p = 100*(np.float(hits)/np.float(hits+fp))
    else:
        p = 0


    # calculate recall, r
    if ((hits+fn) > 0):
        r = 100*(np.float(hits)/np.float(hits+fn))
    else:
        r = 0

    # now calculate the f-measure
    if ((p+r) > 0):
        f = 2.0*np.float(p)*np.float(r)/np.float(p+r)
    else:
        f = 0


    # this is Dixon's related accuracy measure from (Dixon, 2001)
    if ((hits+fp+fn) > 0):
        a = 100.0*np.float(hits)/np.float(hits+fp+fn)
    else:
        a = 0


    return [f,p,r,a]




#######################################################################################
################################### P-SCORE ###########################################
#   
#  Description:
#  Calculate the McKinney et al's PScore accuracy value as used in (McKinney et al, 2007).
#   
#  Inputs: 
#  anns - sequence of ground truth beat annotations (in seconds)
#  beats - sequence of estimated beat times (in seconds)
#   
#  Ouputs: 
#  p - beat tracking accuracy 
#   
#  References:
#  
#  M. F. McKinney, D. Moelants, M. E. P. Davies, and A. Klapuri, "Evaluation of audio beat tracking and music tempo extraction algorithms," Journal of New Music Research, vol. 36, no. 1, pp. 1-16, 2007.
#   
# (c) 2009 Matthew Davies
#
# (Python implementation by Adam Stark 2011-2012)
#
#######################################################################################

def pScore(anns,beats):
    
    # remove beats and annotations that are within the first 5 seconds
    anns = anns[np.where(anns >= minBeatTime)]
    beats = beats[np.where(beats >= minBeatTime)]
    
    # Check if there are any beats, if not then exit
    if beats.size == 0:
        print "beat sequence is empty, assigning zero to all outputs [p]"
        p = 0
        return p
    
    # also check that the beat times are in seconds and not any other time units
    if (max(beats) > 1000) or (max(anns) > 1000):
        print "either beats or annotations are not in seconds, please rectify."
        p = 0
        return p

    # set threshold
    thresh = pScore_thresh
    
    # quantize beats to 10ms resolution
    fs = 100

    endPoint = np.int(np.ceil(max(anns.max(),beats.max())))

    # make impulse trains from beat times, take those beats only greater than 5 seconds
    annsTrain = np.zeros(endPoint*fs)
    beatsTrain = np.zeros(endPoint*fs)

    for i in range(anns.size):
        index = np.int(np.ceil(anns[i]*fs))-1
        annsTrain[index] = 1.0


    for i in range(beats.size):
        index = np.int(np.ceil(beats[i]*fs))-1
        beatsTrain[index] = 1.0

    
    W = np.round(thresh*np.median(np.diff(np.nonzero(annsTrain)[0])))
            
    W = np.int(W)

    p = be_xcorr(beatsTrain,annsTrain,W).sum() /   max(np.nonzero(beatsTrain)[0].size,np.nonzero(annsTrain)[0].size)
    
    p = 100.0*p

    return p

# be_xcorr: computes the cross-correlation between x1 and x2, using lags in the range -maxlags and +maxlags
def be_xcorr(x1,x2,maxlags):

    ar_size = x1.size
    x1 = np.append(x1,np.zeros(maxlags))
    x1 = np.append(np.zeros(maxlags),x1)
    
    x2 = np.append(x2,np.zeros(maxlags))
    x2 = np.append(np.zeros(maxlags),x2)

    x_corr = np.zeros(len(range(-maxlags,maxlags+1)))
    i = 0;
    for lag in range(-maxlags,maxlags+1):      
        sum = 0.
        for n in range(maxlags,maxlags+ar_size):        
            sum = sum + (x1[n]*x2[n+lag])
            
        x_corr[i] = sum
        i = i+1
    
    return x_corr

#######################################################################################
################################### GOTO ACC ##########################################
#    
#  Description:
#  Calculate the Goto and Muraoka's accuracy value as used in (Goto and Muraoka, 1997).
#   
#  Inputs: 
#  anns - sequence of ground truth beat annotations (in seconds)
#  beats - sequence of estimated beat times (in seconds)
#   
#  Ouputs: 
#  a - beat tracking accuracy 
#   
#  References:
#  M. Goto and Y. Muraoka, "Issues in evaluating beat tracking systems," in Working Notes of the IJCAI-97 Workshop on Issues in AI and Music - Evaluation and Assessment, 1997, pp. 9-16.
#   
# (c) 2009 Matthew Davies
#
# (Python implementation by Adam Stark 2011-2012)
#
#######################################################################################

def gotoAcc(anns,beats):

    # remove beats and annotations that are within the first 5 seconds
    anns = anns[np.where(anns >= minBeatTime)]
    beats = beats[np.where(beats >= minBeatTime)]
    
    # Check if there are any beats, if not then exit
    if beats.size == 0:
        print "beat sequence is empty or too short, assigning zero to all outputs [a]"
        a = 0
        return a
    
    # also check that the beat times are in seconds and not any other time units
    if (max(beats) > 1000) or (max(anns) > 1000):
        print "either beats or annotations are not in seconds, please rectify."
        a = 0
        return a

    thresh = gotoAcc_thresh
    mu = gotoAcc_mu
    sigma = gotoAcc_sigma

    beatError = np.ones(anns.size)

    paired = np.zeros(anns.size)

    hit = 0

    
    for k in range(1,anns.size-1):
        # previous inter annotation interval
        preInterval = 0.5*(anns[k]-anns[k-1])
        # beginning of half i-a-i
        windowMin = anns[k] - preInterval

        # next inter annotation interval
        postInterval = 0.5*(anns[k+1]-anns[k]);
        # end of half i-a-i
        windowMax = anns[k] + postInterval


        # find those beats which are in the range of windowMin to windoMax
        #        a1 = beats[(beats >= windowMin) & (beats < windowMax)]
        a1 = np.where((beats >= windowMin) & (beats < windowMax))[0]
        
        if(a1.size == 0):
            # false negative case 
            paired[k] = 0
            beatError[k] = 1
        elif(a1.size>1):
            # false positive case.
            paired[k] = 0
            beatError[k] = 1
        else:
            # it's paired beat, so measure beat error
            paired[k] = 1

            newError = np.float(beats[a1[0]] - anns[k])

            if (newError<0): # if negative use pre_interval
                beatError[k] = np.float(newError)/np.float(preInterval)
            else: # else positive so use subsequent inter annotation interval
                beatError[k] = np.float(newError)/np.float(postInterval)


    b1 = np.where(np.abs(beatError) > thresh)[0]

    if (b1.size<3): # i.e. if only first and last
        # extract track
        track = beatError[(b1[0]+1):(b1[b1.size-1]-1)]
        hit = hit+1; # have shown good until the end

    else:
        tmp = np.diff(b1)
        trackLen = tmp.max()
        ind = tmp.argmax()
        
        if ((trackLen-1) > 0.25*(anns.size-2)):
            # i.e. we have more than 25% correct tracking.. somewhere
            hit = hit+1
            track = beatError[b1[ind]:(b1[ind+1]+1)]

    # if have found a hit so far
    if (hit):
        # now test mean and standard deviation
        if (np.abs(track).mean()<mu) and (track.std(ddof = 1) < sigma):
            hit = hit+2;


    
    if (hit==3):
        a = 100
    else:
        a = 0


    return a

                
#######################################################################################
############################### INFORMATION GAIN ######################################
#   
#  Description:
#  Calculate the information gain as used in (Davies et al, 2010).
#   
#  Inputs: 
#  anns - sequence of ground truth beat annotations (in seconds)
#  beats - sequence of estimated beat times (in seconds)
#   
#  Ouputs: 
#  I - beat tracking information gain 
#  binVals - beat error histogram bin values 
# 
#  References:
#  
#  M. E. P. Davies, N. Degara and M. D. Plumbley, "Measuring the performance of beat tracking algorithms algorithms using a beat error histogram,"  accepted to IEE Signal Processing Letters.
#   
# (c) 2010 Matthew Davies, Norberto Degara
#
# (Python implementation by Adam Stark 2011-2012)
#
#######################################################################################
                    
def informationGain(anns,beats):
    
    # remove beats and annotations that are within the first 5 seconds
    anns = anns[np.where(anns >= minBeatTime)]
    beats = beats[np.where(beats >= minBeatTime)]

    numBins = informationGain_numBins
    
    # Check if there are any beats, if not then exit
    if (beats.size < 2) or (anns.size < 2):
        print "beat or annotation sequence is empty or too short, assigning zero to information gain [D] and a uniform beat error histogram"
        I = 0
        # slight stretch here, to get totally uniform, use non-integer bin heights
        binVals = np.zeros(numBins) + np.float(anns.size)/np.float(numBins)
        return [I,binVals]


    # also check that the beat times are in seconds and not any other time units
    if (max(beats) > 1000) or (max(anns) > 1000):
        print "either beats or annotations are not in seconds, please rectify."
        I = 0
        # slight stretch here, to get totally uniform, use non-integer bin heights
        binVals = np.zeros(numBins) + np.float(anns.size)/np.float(numBins)
        return [I,binVals]

    b_start = (-0.5+0.5*(1./(np.float(numBins)-1.)))
    b_end = (0.5-0.5*(1./(np.float(numBins)-1.)))
    b_step = 1./(np.float(numBins)-1.)

    histBins = np.arange(b_start,b_end+b_step,b_step)
    histBins = np.append(histBins,0.5)
    histBins = np.append(-0.5,histBins)
    # actually gives numbins+1 bins..
    
    # beats compared to annotations
    fwdError = FindBeatError_nor2(anns,beats)
    [fwdEntropy,fwdBinVals] = FindEntropy(fwdError,histBins)
    
    # annotations compared to beats
    bwdError = FindBeatError_nor2(beats,anns);
    [bwdEntropy,bwdBinVals] = FindEntropy(bwdError,histBins);

    # find higher entropy value (i.e. which is worst)
    if (fwdEntropy > bwdEntropy):
        maxEntropy = fwdEntropy
        binVals = fwdBinVals
    else:
        maxEntropy = bwdEntropy
        binVals = bwdBinVals
    
    histBins = histBins[0:histBins.size-1]

    I = np.log2(np.float(numBins)) - maxEntropy

    return [I,binVals]





def FindBeatError_nor2(anns,beats):
    
    beatError = np.zeros(beats.size)

    anns.sort()
    beats.sort()

    # Calculate relative error for each beat sample
    for i in range(beats.size):
        
        tmp = abs(beats[i] - anns).min()        # find closest annotation to beats[i]
        i_e = abs(beats[i] - anns).argmin()     # find index of closest annotation to beats[i]

        e_absolute = beats[i]-anns[i_e]

        # test on i_e now..
        if (i_e == 0): # if first annotation is nearest
            interval = 0.5*(anns[i_e+1] - anns[i_e])
            e_relative = 0.5* e_absolute / interval
        elif (i_e == (anns.size-1)): # if last annotation is nearest
            interval = 0.5*(anns[i_e] - anns[i_e-1])
            e_relative = 0.5* e_absolute / interval
        else:       # normal case - need to test whether e_absolute is positive or negative.. and chose interval accordingly
            if (e_absolute > 0): # nearest annotation is BEFORE the current beat - so look at the previous interval
                interval = 0.5*(anns[i_e] - anns[i_e-1])
                e_relative = 0.5* e_absolute / interval
            else:                # nearest annotation is AFTER the current beat - so look at the next interval
                interval = 0.5*(anns[i_e+1] - anns[i_e])
                e_relative = 0.5* e_absolute / interval
                
    
        beatError[i] = e_relative
    
    
    
    # trick to deal with bin boundaries
    beatError = ((10000.0*beatError).round())/10000.0
            
    return beatError



def FindEntropy(beatError,histBins):
    
    # fix the beat errors which are out of range
    beatError = np.mod(beatError+0.5,-1.0)+0.5 # like doing princarg... but for [-0.5, 0.5];
    
    # we have to calculate the bin edges because python uses bin edges for histogram calculation rather than bin centers
    histBinsEdges = np.zeros(histBins.size)
    histBinsEdges[0] = histBins[0] - (abs(histBins[0])-abs(histBins[1]))
    
    for h in range(1,histBins.size):
        histBinsEdges[h] = np.array([histBins[h-1],histBins[h]]).mean()
    
    # add final histogram bin edge
    histBinsEdges = np.append(histBinsEdges,(histBinsEdges[histBinsEdges.size-1] + (histBinsEdges[histBinsEdges.size-1]-histBinsEdges[histBinsEdges.size-2])))
        
    # get bin heights
    rawBinVals = np.histogram(beatError,bins=histBinsEdges)[0]
    
    # want to add the last bin height to the first bin.
    rawBinVals[0] = rawBinVals[0]+rawBinVals[rawBinVals.size-1];
    rawBinVals = rawBinVals[0:rawBinVals.size-1]

    binVals = rawBinVals;
    
    # convert array from int to float
    binVals = binVals.astype(np.float)
    
    # make sure the bins heights sum to unity
    binVals = binVals/binVals.sum()
    
    

    # set zero valued binvals to 1, but don't want to output these...
    binValsTmp = binVals
    # this makes the entropy calculation well-behaved.
    for b in range(binValsTmp.size):
        if (binValsTmp[b] == 0):
            binValsTmp[b] = 1.


    

    # now calculate the entropy
    sum = 0.
    for b in range(binValsTmp.size):
        sum = sum + (binValsTmp[b]*np.log2(binValsTmp[b]))
    entropy = -sum

    return [entropy,rawBinVals]

    


#######################################################################################
############################# CONFIDENCE INTERVALS ####################################
#   
#  Description:
#  Work out bootstrapping confidence interval
#   
#  Inputs: 
#  beat tracking scores 
#   
#  Ouputs: 
#  lci - lower confidence interval
#  uci - upper confidence interval
#     
# (c) 2009 Matthew Davies
#
# (Python implementation by Adam Stark 2011-2012)
#
#######################################################################################

def confidenceIntervals(scores):

    # number of bootstrap samples
    numSamples = confidenceInterval_numSamples

    # confidence interval
    interval = confidenceInterval_interval

    numScores = scores.size

    meanVals = np.zeros(numSamples)
    
    for sample in range(numSamples):
        # get random sampling from scores
        randomSamples = np.ceil(np.random.random(numScores)*np.float(numScores))-1
        randomSamples.sort()
        
        tmp = np.zeros(randomSamples.size)        
        
        for r in range(randomSamples.size):
            tmp[r] = scores[randomSamples[r]]

        meanVals[sample] = tmp.mean()


    # sort the meanVals
    meanVals.sort()

    # get first and last point of confidence interval
    first = np.ceil(numSamples*(1.-interval)/2.)
    last = np.ceil(numSamples*interval + numSamples*(1.-interval)/2.)

    lci = meanVals[first]
    uci = meanVals[last]

    return [lci,uci]



##################################################################################################
##################################################################################################
##################################### Other Useful Functions #####################################
##################################################################################################
##################################################################################################




#######################################################################################
################################# Print Beats to a Text File ##########################
#   
#  Description:
#  Print out a beat sequence to a text file
#   
#  Inputs: 
#  beats - sequence of beats
#  path - file path
#  filename - file name
#     
#  (c) 2012 Adam Stark
#
#######################################################################################


# write beats out to a text file
def beats_to_text_file(beats,filename,path = "beats_out/"):
    
    # if the directory doesn't exist then create it
    if not os.path.exists(path):
        os.makedirs(path)
    
    # open the file
    file = open(path + filename, "w")
    
    # write beats out line by line
    for i in range(beats.size):
        file.write(str(beats[i]))
        file.write("\n")
    
    # close the file
    file.close()


