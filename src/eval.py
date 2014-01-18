# -*- coding: utf-8 -*-

from qAnalyzer import *
from maltImporter import MaltImporter
from hmmGlasses import *
from featureBasedClassifier import *

ourQuestions = MaltImporter().importMaltOutputs(qFilePath, qParsedFilePath)

analyzer = QuestionAnalysis(ourQuestions[0])
mass = MassAnalyzer(ourQuestions)

normalGlass = Glass(ourQuestions, reverse=False)
reverseGlass = Glass(ourQuestions, reverse=True)

#########################################################################
""" partial questions """
filteredNedir = mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'nedir')

filteredVerilir = mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'verilir')

filteredHangisidir = mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'hangisidir')

filteredHangisidir.extend(mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'hangileridir'))

filteredHangiBetween = mass.filterByPartValue('depenTag', '*', 'text', 'hangi')

filteredDenir = mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'denir')

filteredDenir.extend(mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'denilir'))
filteredDenir.extend(mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'denilmektedir'))
#########################################################################

# computePerClassCounts:
# given the gold standard parts and computed parts, 
# it computes simply the TruePositive, FalsePositive and FalseNegative counts
#
def computePerClassCounts(goldParts, resultParts, resultsArr):

    for truePart in goldParts:
        if truePart in resultParts:
            resultsArr['TP'] += 1
        else:
            resultsArr['FN'] += 1

    for distPart in resultParts:
        if distPart not in goldParts:
            resultsArr['FP'] += 1
    
    return resultsArr


# displayResults: 
# just creates the display and prints it to stdout
#
def displayResults(modelName, results, fullInfo):
    print("\nResults for : " + modelName + "\n\n")
        
    total = str(results['totalFParts'])
    tp = results['TP']*1.0
    fn = results['FN']*1.0
    fp = results['FP']*1.0
    
    if fullInfo:
        print("Total Focus # : " + total)
    
        print("-- TP : " + str(int(tp)))
        print("-- FN : " + str(int(fn)))
        print("-- FP : " + str(int(fp)))
    
    precision = tp/(tp+fp)
    
    print("\n-- Precision : " + str(precision))
    
    recall = tp/(tp+fn)
    
    print("-- Recall : " + str(recall))
    
    fScore = (2*precision*recall)/(precision+recall)
    
    print("-- F-Score : " + str(fScore))


# evaluateDistiller
# only evaluates the distiller, 
# produces 1) Proper model name 2) results
#
def evaluateDistiller(questionSet):

    results = {'TP':0, 'FP':0, 'TN':0, 'FN':0, 'totalFParts':0}

    for question in questionSet:

        results['totalFParts'] += len(question.trueFocus)

        # actual focus detection starts to work
        ruleFocus, hmmResults, focusCombined, focusConfidences = QuestionAnalysis(question).extractFocusMod(None, None, True)

        # computing tp, fp and fn
        results = computePerClassCounts(question.trueFocus, ruleFocus, results)

    return 'FM-Distiller Single', results

# evaluateGlasses
# only evaluates the HMM-Glasses, 
# produces 1) Proper model name 2) results
#
def evaluateGlasses(questionSet, reverse):
    glass = Glass(questionSet, reverse)

    results = {'TP':0, 'FP':0, 'TN':0, 'FN':0, 'totalFParts':0}
    
    for question in questionSet:

        results['totalFParts'] += len(question.trueFocus)

        hmmTripletAllResults = glass.computeFocusProbs(question)

        hmmTripletFocusResults = [trplt for trplt in hmmTripletAllResults if (trplt[0] == 'FOC')]

        resultParts = Glass.hmmResultsToParts(hmmTripletFocusResults)

        results = computePerClassCounts(question.trueFocus, resultParts, results)
        

    revStr = "Forward"
    if reverse:
        revStr = "Backward"
    return 'HMM-Glasses Single ('+revStr+' mode)', results

# evaluateBoth
# given the question set, it evaluates the combination of 
# both the FM-Distiller and HMM-Glasses
#
def evaluateBoth(questionSet):
    forwGlass = Glass(questionSet, reverse=False)
    backGlass = Glass(questionSet, reverse=True)

    results = {'TP':0, 'FP':0, 'TN':0, 'FN':0, 'totalFParts':0}

    for question in questionSet:

        results['totalFParts'] += len(question.trueFocus)

        rF, hR, focusCombined, confidences = QuestionAnalysis(question).extractFocusMod(backGlass, forwGlass, False)

        # computing tp, fp and fn
        results = computePerClassCounts(question.trueFocus, focusCombined, results)

    return '******** Final Results (Full Model) ******** ', results

# evaluate:
# this is just an interface to the specialized evaluation functions
# 
def evaluate(questions, model, fullInfo=True):

    if fullInfo:
        print("\n\n ==== Evaluation BEGIN ==== \n")

    if model=='distiller':
        modelName, results = evaluateDistiller(questions)

        displayResults(modelName, results, fullInfo)

    elif model=="glasses":
        bModelName, backResults = evaluateGlasses(questions, reverse=True)
        fModelName, forwResults = evaluateGlasses(questions, reverse=False)

        displayResults(bModelName, backResults, fullInfo)
        displayResults(fModelName, forwResults, fullInfo)

    elif model=="combined":
        modelDisplay, combinedResults = evaluateBoth(questions)

        displayResults(modelDisplay, combinedResults, fullInfo)

    if fullInfo:
        print("\n\n ==== Evaluation END ==== \n\n")

def evaluateClass(questions):
    rule = RuleBasedQuestionClassification(ourQuestions, classPath, classQuestionWordsPath, classQuestionKeywordsPath);
    rule.doClassification();
# MAIN CONSOLE #

fullInfo = False

if 'distiller' in sys.argv:
    evaluate(ourQuestions, 'distiller', fullInfo)

if 'glass' in sys.argv:
    evaluate(ourQuestions, 'glasses', fullInfo)

if 'combined' in sys.argv:
    evaluate(ourQuestions, 'combined', fullInfo)
    
if 'class' in sys.argv:
    evaluateClass(ourQuestions)

