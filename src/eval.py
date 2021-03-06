# -*- coding: utf-8 -*-

import sys

sys.path.append('querier')

from qAnalyzer import *
from maltImporter import MaltImporter
from hmmGlasses import *
from featureBasedClassifier import *
from hybridClassifier import *

from random import shuffle

import pickle, os, copy

from indriHandler import *
from indriDocFetch import *

ourQuestions = MaltImporter().importMaltOutputs(qFilePath, qParsedFilePath)

analyzer = QuestionAnalysis(ourQuestions[0])
mass = MassAnalyzer(ourQuestions)

normalGlass = Glass(ourQuestions, backwards=False)
reverseGlass = Glass(ourQuestions, backwards=True)


# computePerClassCounts:
# given the gold standard parts and computed parts, 
# it computes simply the TruePositive, FalsePositive and FalseNegative counts
#
def computePerClassCounts(goldParts, resultParts, resultsDict):

    for truePart in goldParts:
        if truePart in resultParts:
            resultsDict['TP'] += 1
        else:
            resultsDict['FN'] += 1

    for distPart in resultParts:
        if distPart not in goldParts:
            resultsDict['FP'] += 1
    
    return resultsDict


# displayResults: 
# just creates the display and prints it to stdout
#
def displayResults(modelName, results, fullInfo, individual=False):
    print("\nResults for : " + modelName + "\n\n")
        
    if not individual:
        total = str(results['totalFParts'])
    tp = results['TP']*1.0
    fn = results['FN']*1.0
    fp = results['FP']*1.0
    
    if fullInfo:
        if not individual:
            print("Total Focus # : " + total)
    
        print("-- TP : " + str(int(tp)))
        print("-- FN : " + str(int(fn)))
        print("-- FP : " + str(int(fp)))
    
    precision = tp/(tp+fp)
    
    print("-- Precision : " + str(precision))
    
    recall = tp/(tp+fn)

    print("-- Recall : " + str(recall))
    
    fScore = (2*precision*recall)/(precision+recall)
    
    print("-- F-Score : " + str(fScore))



def prepareTenFoldIndexes(questions):
    indexes = []
    
    setLength = len(questions)

    chunkSize = setLength/10

    cIndexStart = 0

    for i in range(1, setLength+1):
        if (i % chunkSize) == 0:
            if ((setLength-i) < chunkSize): # very last chunk
                indexes.append([cIndexStart, setLength])
                break
            else:
                indexes.append([cIndexStart, i])
                cIndexStart = i

    return indexes


# evaluateDistiller
# only evaluates the distiller, 
# produces 1) Proper model name 2) results
#
def evaluateDistiller(questionSet, genericEnable=False):

    results = {'TP':0, 'FP':0, 'TN':0, 'FN':0, 'totalFParts':0}
    counts = {'nodist':0,
              'nosen':0,
              'nogen':0,
              'kac':0,
              'nedir':0,
              'verilir':0,
              'denir':0,
              'hangisidir':0,
              'hangi':0,
              'kadar':0,
              'generic':0}

    indResults = {'nedir': {'TP':0, 'FP':0, 'FN':0},
                  'verilir': {'TP':0, 'FP':0, 'FN':0},
                  'denir': {'TP':0, 'FP':0, 'FN':0}}

    for question in questionSet:

        results['totalFParts'] += len(question.trueFocus)

        # actual focus detection starts to work
        ruleFocus, hmmResults, focusCombined, focusConfidences, whichDist = QuestionAnalysis(question).extractFocusMod(None, None, True, False, genericEnable, whichDistEnable=True)

        counts[whichDist] += 1

        oldRes = results.copy()

        # computing tp, fp and fn
        results = computePerClassCounts(question.trueFocus, ruleFocus, results)

        # HACK
        if whichDist == 'nedir' or whichDist == 'denir' or whichDist == 'verilir':
            indResults[whichDist]['TP'] += (results['TP']-oldRes['TP'])
            indResults[whichDist]['FP'] += (results['FP']-oldRes['FP'])
            indResults[whichDist]['FN'] += (results['FN']-oldRes['FN'])
            

    genStatus = "Disabled"
    if genericEnable:
        genStatus = "Enabled"
    
    mName = 'FM-Distiller Alone - generic expert ' + genStatus 
    return mName, results, counts, indResults

# evaluateGlasses
# only evaluates the HMM-Glasses, 
# produces 1) Proper model name 2) results
#
def evaluateGlasses(learnQuestions, testQuestions, backwards, twoDirections=False):
    
    # REFACTOR
    reverse = backwards
    
    results = {'TP':0, 'FP':0, 'TN':0, 'FN':0, 'totalFParts':0}

    if twoDirections:
        glassNormal = Glass(learnQuestions, False)
        glassRev = Glass(learnQuestions, True)
    else:
        glass = Glass(learnQuestions, reverse)

    for question in testQuestions:

        results['totalFParts'] += len(question.trueFocus)

        if twoDirections:
            tripletsNormal = glassNormal.computeFocusProbs(question)
            tripletsReverse = glassRev.computeFocusProbs(question)

            hmmTripletAllResults = QuestionAnalysis.combineGlasses(tripletsNormal, tripletsReverse)

        else:
            hmmTripletAllResults = glass.computeFocusProbs(question)

        # extracting focus parts from hmm results to evaluate
        hmmTripletFocusResults = [trplt for trplt in hmmTripletAllResults if (trplt[0] == 'FOC')]

        # converting triplets to listof parts
        resultParts = Glass.hmmResultsToParts(hmmTripletFocusResults)

        # computing the eval metrics
        results = computePerClassCounts(question.trueFocus, resultParts, results)
        

    revStr = "Forward"
    if reverse:
        revStr = "Backward"
    
    if twoDirections:
        revStr = "Forward & Backward"
    return 'HMM-Glasses Alone ('+revStr+' mode)', results

# evaluateFull
# given the question set, it evaluates the combination of 
# both the FM-Distiller and HMM-Glasses
#
def evaluateFull(learnQuestions, testQuestions, onlyForward=True, genericEnable=False):
    forwGlass = Glass(learnQuestions, backwards=False)
    backGlass = Glass(learnQuestions, backwards=True)

    results = {'TP':0, 'FP':0, 'TN':0, 'FN':0, 'totalFParts':0}

    for question in testQuestions:

        results['totalFParts'] += len(question.trueFocus)

        rF, hR, focusCombined, confidences = QuestionAnalysis(question).extractFocusMod(backGlass, forwGlass, False, onlyForward, genericEnable)

        # computing tp, fp and fn
        results = computePerClassCounts(question.trueFocus, focusCombined, results)

    backStatus = 'Disabled'
    if not onlyForward:
        backStatus = 'Enabled'

    genStat = 'Disabled'
    if genericEnable:
        genStat = 'Enabled'

    modelName = '******** Final Results  (Full Model)  ********\n'
    modelName += ' - Distiller : generic expert ' + genStat + '\n'
    modelName += ' - HMM : Backward Sweep ' + backStatus + '\n'
    return modelName, results

def crossValidate(questions, fullInfo = False):
    print("\n ==== Preparing 10-fold Cross-Validation ==== \n\n")

    if fullInfo:
        print("Shuffling the question set...")

    if not os.path.isfile('shuffled.questions'):
        
        shuffledQuestions = copy.deepcopy(questions)

        shuffle(shuffledQuestions)

        pickle.dump(shuffledQuestions, open('shuffled.questions', 'w'))

    else:
        shuffledQuestions = pickle.load(open('shuffled.questions', 'r'))


    indexes = prepareTenFoldIndexes(shuffledQuestions)

    if fullInfo:
        print("Fold Indexes : " + str(indexes))

    foldNum = 1
    setSize = len(shuffledQuestions)

    results = {'TP':0, 'FP':0, 'TN':0, 'FN':0, 'totalFParts':0}

    # Distiller ALONE
    distGenResults = results.copy()
    distResults = results.copy()

    # HMM ALONE
    backResults = results.copy()
    forwResults = results.copy()
    bothResults = results.copy()

    # HMM with Distiller (yes generic)
    backDistGenRes = results.copy()
    forwDistGenRes = results.copy()
    bothDistGenRes = results.copy()
    
    # HMM with Distiller (no generic)
    backDistRes = results.copy()
    forwDistRes = results.copy()
    bothDistRes = results.copy()

    print("\n ==== Preparation Complete - Folding Begins! ==== \n\n")

    for indexRange in indexes:

        if fullInfo:
            print("\n -- Fold # " + str(foldNum))
            print(" -- Learning set indexes : " + str(indexRange))
            foldNum += 1
        
        start = indexRange[0]
        end = indexRange[1]
        
        # grabbing questions using pre-prepared indexes
        testSet = shuffledQuestions[start:end]
        learnSet = shuffledQuestions[0:start]+shuffledQuestions[end:setSize]
        
        if fullInfo:
            print("Just to be sure:")
            print("Learn Set Size : " + str(len(learnSet)))
            print("Test Set Size : " + str(len(testSet)))

        gBackAlone = Glass(learnSet, backwards=True)
        gForwAlone = Glass(learnSet, backwards=False)

        if fullInfo:
            print("-- Evaluation Begins... ")
        for question in testSet:

            backResults['totalFParts'] += len(question.trueFocus)
            forwResults['totalFParts'] += len(question.trueFocus)
            bothResults['totalFParts'] += len(question.trueFocus)

            backDistGenRes['totalFParts'] += len(question.trueFocus)
            forwDistGenRes['totalFParts'] += len(question.trueFocus)
            bothDistGenRes['totalFParts'] += len(question.trueFocus)

            backDistRes['totalFParts'] += len(question.trueFocus)
            forwDistRes['totalFParts'] += len(question.trueFocus)
            bothDistRes['totalFParts'] += len(question.trueFocus)

            distGenResults['totalFParts'] += len(question.trueFocus)
            distResults['totalFParts'] += len(question.trueFocus)


            backTriplets = gBackAlone.computeFocusProbs(question)
            forwTriplets = gForwAlone.computeFocusProbs(question)
            bothTriplets = QuestionAnalysis.combineGlasses(forwTriplets, backTriplets)

            backFtriplets = [trplt for trplt in backTriplets if (trplt[0]=='FOC')]
            forwFtriplets = [trplt for trplt in forwTriplets if (trplt[0]=='FOC')]
            bothFtriplets = [trplt for trplt in bothTriplets if (trplt[0]=='FOC')]

            # HMM results
            backFparts = Glass.hmmResultsToParts(backFtriplets)
            forwFparts = Glass.hmmResultsToParts(forwFtriplets)
            bothFparts = Glass.hmmResultsToParts(bothFtriplets)

            ana = QuestionAnalysis(question)

            # Distiller alone, generic enabled results
            ruleFocusGen, dummy, distGenResult, distGenConf = ana.extractFocusMod(reverseGlass='dummy', normalGlass='dummy', onlyDistiller=True, onlyForward='dummy', genericEnable=True)

            # Distiller alone, generic disabled results
            ruleFocus, dummy, distResult, distConf = ana.extractFocusMod(reverseGlass='dummy', normalGlass='dummy', onlyDistiller=True, onlyForward='dummy', genericEnable=False)
            # HMM + Dist -> nogen
            backDistComb, conf = ana.combineDistillerGlasses(distResult, distConf, backTriplets)
            forwDistComb, conf = ana.combineDistillerGlasses(distResult, distConf, forwTriplets)
            bothDistComb, conf = ana.combineDistillerGlasses(distResult, distConf, bothTriplets)

            # HMM + Dist -> yesgen
            backDistGenComb, conf = ana.combineDistillerGlasses(distGenResult, distGenConf, backTriplets)
            forwDistGenComb, conf = ana.combineDistillerGlasses(distGenResult, distGenConf, forwTriplets)
            bothDistGenComb, conf = ana.combineDistillerGlasses(distGenResult, distGenConf, bothTriplets)


            distGenResults = computePerClassCounts(question.trueFocus, distGenResult, distGenResults)
            distResults = computePerClassCounts(question.trueFocus, distResult, distResults)

            backResults = computePerClassCounts(question.trueFocus, backFparts, backResults)
            forwResults = computePerClassCounts(question.trueFocus, forwFparts, forwResults)
            bothResults = computePerClassCounts(question.trueFocus, bothFparts, bothResults)

            # with Distiller (yes generic)
            backDistGenRes = computePerClassCounts(question.trueFocus, backDistGenComb, backDistGenRes)
            forwDistGenRes = computePerClassCounts(question.trueFocus, forwDistGenComb, forwDistGenRes)
            bothDistGenRes = computePerClassCounts(question.trueFocus, bothDistGenComb, bothDistGenRes)
    
            # with Distiller (no generic)
            backDistRes = computePerClassCounts(question.trueFocus, backDistComb, backDistRes)
            forwDistRes = computePerClassCounts(question.trueFocus, forwDistComb, forwDistRes)
            bothDistRes = computePerClassCounts(question.trueFocus, bothDistComb, bothDistRes)


    distMname = "Distiller Alone w/ Generic Disabled"
    distGenMname = "Distiller Alone w/ Generic Enabled"
        
    backMname = "HMM-Glasses Alone w/ Backwards Mode"
    forwMname = "HMM-Glasses Alone w/ Forwards Mode"
    bothMname = "HMM-Glasses Alone w/ Forwards & Backwards Mode"

    backDistGenName = "HMM-Glasses (Backwards) With Distiller (Generic Enabled)"
    forwDistGenName = "HMM-Glasses (Forwards) With Distiller (Generic Enabled)"
    bothDistGenName = "HMM-Glasses (Forw & Back) With Distiller (Generic Enabled)"

    backDistName = "HMM-Glasses (Backwards) With Distiller (Generic Disabled)"
    forwDistName = "HMM-Glasses (Forwwards) With Distiller (Generic Disabled)"
    bothDistName = "HMM-Glasses (Forw & Back) With Distiller (Generic Disabled)"


    displayResults(distMname, distResults, fullInfo)
    displayResults(distGenMname, distGenResults, fullInfo)

    displayResults(backMname, backResults, fullInfo)
    displayResults(forwMname, forwResults, fullInfo)
    displayResults(bothMname, bothResults, fullInfo)

    displayResults(backDistName, backDistRes, fullInfo)
    displayResults(forwDistName, forwDistRes, fullInfo)
    displayResults(bothDistName, bothDistRes, fullInfo)

    displayResults(backDistGenName, backDistGenRes, fullInfo)
    displayResults(forwDistGenName, forwDistGenRes, fullInfo)
    displayResults(bothDistGenName, bothDistGenRes, fullInfo)

# evaluate:
# this is just an interface to the specialized evaluation functions
# 
def evaluate(questions, model, fullInfo=True):

    if fullInfo:
        print("\n\n ==== Evaluation BEGIN ==== \n")

    if model=='distiller':
        # GE : generic expert enabled & GD : generic expert disabled
        mNameGE, resultsGE, counts, indCounts = evaluateDistiller(questions, genericEnable=True)
        mNameGD, resultsGD, counts, indCounts = evaluateDistiller(questions, genericEnable=False)
        

        displayResults(mNameGE, resultsGE, fullInfo)
        displayResults(mNameGD, resultsGD, fullInfo)

        # HACK
        print("\n-- Individual Class Scores --\n")

        displayResults("nedir", indCounts['nedir'], fullInfo, True)
        displayResults("verilir", indCounts['verilir'], fullInfo, True)
        displayResults("denir", indCounts['denir'], fullInfo, True)


        print(counts)

        total = sum(counts.values())
        print(total)
        print(total==len(questions))

        totalPercent = 0

        for countKey in counts:
            print(countKey + " - " + str(counts[countKey]) + " - % " + str(counts[countKey]*100.0/total))
            totalPercent += counts[countKey]*100.0/total

        print("total percent check : " + str(totalPercent))
        

    elif model=="glasses":
        bModelName, backResults = evaluateGlasses(questions, questions, backwards=True)
        fModelName, forwResults = evaluateGlasses(questions, questions, backwards=False)
        twoMN, twoResults = evaluateGlasses(questions, questions, 'dummy', twoDirections=True)

        displayResults(bModelName, backResults, fullInfo)
        displayResults(fModelName, forwResults, fullInfo)
        displayResults(twoMN, twoResults, fullInfo)

    elif model=="combined":
        # FB : forward backward
        # GE : generic expert enabled
        modelDisplayFBGE, combinedResultsFBGE = evaluateFull(questions, questions, False, True)
        modelDisplayFGE, combinedResultsFGE = evaluateFull(questions, questions, True, True)

        modelDisplayFBGD, combinedResultsFBGD = evaluateFull(questions, questions, False, False)
        modelDisplayFGD, combinedResultsFGD = evaluateFull(questions, questions, True, False)


        displayResults(modelDisplayFBGE, combinedResultsFBGE, fullInfo)
        displayResults(modelDisplayFGE, combinedResultsFGE, fullInfo)
        displayResults(modelDisplayFBGD, combinedResultsFBGD, fullInfo)
        displayResults(modelDisplayFGD, combinedResultsFGD, fullInfo)

    if fullInfo:
        print("\n\n ==== Evaluation END ==== \n\n")

def evaluateClass(questions):
    rule = RuleBasedQuestionClassification(ourQuestions);
    rule.doClassification();
# MAIN CONSOLE #
    


fullInfo = False

all = 'all' in sys.argv

if all or 'distiller' in sys.argv:
    evaluate(ourQuestions, 'distiller', fullInfo)

if all or 'glass' in sys.argv:
    evaluate(ourQuestions, 'glasses', fullInfo)

if all or 'combined' in sys.argv:
    evaluate(ourQuestions, 'combined', fullInfo)
    
if all or 'class' in sys.argv:
    evaluateClass(ourQuestions)

if all or 'cross' in sys.argv:
    crossValidate(ourQuestions, True)

if 'pick' in sys.argv:
    sq = copy.deepcopy(ourQuestions)

    shuffle(sq)

    sq = sq[0:10]

    terms = []

    for q in sq:
        terms.append(q.questionText.split())

    for t in terms:
        print(t)

if 'newclass' in sys.argv:

    classes = ['DESCRIPTION', 'TEMPORAL', 'NUMERIC', 'ENTITY', 
               'ABBREVIATION', 'LOCATION', 'HUMAN']

    clsResults = {'DESCRIPTION': {'P':0, 'R':0, 'F':0},
                  'TEMPORAL': {'P':0, 'R':0, 'F':0},
                  'NUMERIC': {'P':0, 'R':0, 'F':0},
                  'ENTITY': {'P':0, 'R':0, 'F':0},
                  'ABBREVIATION': {'P':0, 'R':0, 'F':0},
                  'LOCATION': {'P':0, 'R':0, 'F':0},
                  'HUMAN': {'P':0, 'R':0, 'F':0}}

    for cls in classes:

        print("\n === " + cls + " === \n")

        results = {'TP':0, 'FP':0, 'TN':0, 'FN':0}

        for q in ourQuestions:

            foundCls = coarseFinder(q)

            qCls = q.coarseClass

            if foundCls != cls and qCls == cls:
                results['FN'] += 1
            elif foundCls == cls and qCls != cls:
                results['FP'] += 1
            elif foundCls != cls and qCls != cls:
                results['TN'] += 1
            elif foundCls == cls and qCls == cls:
                results['TP'] += 1
            else:
                raise RuntimeError("BIG SHIT!")

        tp = results['TP']
        fp = results['FP']
        fn = results['FN']

        if (tp+fp) == 0:
            P = 0
        else:
            P = (tp*1.0)/(tp+fp)

        if (tp+fn) == 0:
            R = 0
        else:
            R = (tp*1.0)/(tp+fn)

        if (P+R) == 0:
            F = 0
        else:
            F = (2*P*R)/(P+R)

        clsResults[cls]['P'] = P
        clsResults[cls]['R'] = R
        clsResults[cls]['F'] = F

        print("Precision : " + str(P))
        print("Recall : " + str(R))
        print("F-Score : " + str(F))

    k = len(classes)

    precTotal = 0
    recTotal = 0
    fTotal = 0

    for cls in classes:
        precTotal += clsResults[cls]['P']
        recTotal += clsResults[cls]['R']
        fTotal += clsResults[cls]['F']

    print("\n\n ======= OVERALL ======= \n")
    print("Precision : " + str((precTotal/k)))
    print("Recall : " + str((recTotal/k)))
    print("F-Score : " + str((fTotal/k)))
                

if 'baseline' in sys.argv:


    results = {'TP':0, 'FP':0, 'TN':0, 'FN':0, 'totalFParts':0}

    for question in ourQuestions:

        try:
            baseFocus = QuestionAnalysis.baselineFocusExtract(question, 4)
        except:
            print(question.questionText)
            raise

        goldResults = question.trueFocus
        goldFocus = []
        for resultPart in goldResults:
            goldFocus.append(resultPart[1])
        
        results = computePerClassCounts(goldFocus, baseFocus, results)
        results['totalFParts'] += len(goldFocus)

    displayResults("Baseline ", results, True)

        

if 'IR' in sys.argv:
    
    totalFound = 0

    for i in range(len(ourQuestions)):
        #sys.stdout.write('|')
        queryID = i+1

        docs = singleIndriQuery(queryID)

        docsContainAnswer = 0

        found=False

        for docID in docs:
            doc = getDoc(docID)
            answerText = ourQuestions[i].answer.encode('utf8')

            answers = answerText.split('/')

            for answer in answers:
                if (answer in doc) or (answer.lower() in doc) or (answer.upper() in doc):
                    docsContainAnswer += 1
                    print(answer)
                    found=True
                    break

            if found:
                break

        if docsContainAnswer != 0:
            totalFound += 1

    print("IR Take I Results : ")
    print("Indri (first 5 guess)")
    print(str(totalFound) + " / 1000")

    print("\nCorrectly found documents containing answers for " + str(totalFound/10.0) + "% questions... END")
