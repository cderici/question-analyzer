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

def evaluateDistiller(questionSet):

    results = {'TP':0, 'FP':0, 'TN':0, 'FN':0, 'totalFParts':0}

    for question in questionSet:
        serialParts = serializeDepTree(question.questionParts)

        results['totalFParts'] += len(question.trueFocus)

        ruleFocus, hmmResults, focusCombined, focusConfidences = QuestionAnalysis(question).extractFocusMod(None, None, True)

        for truePart in question.trueFocus:
            if truePart in ruleFocus:
                results['TP'] += 1
            else:
                results['FN'] += 1

        for distPart in ruleFocus:
            if distPart not in question.trueFocus:
                results['FP'] += 1

    return 'FM-Distiller Single', results

def evalDisplay(questions, model):

    print("\n\n ==== Evaluation Begins ==== \n\n")

    if model=='distiller':
        modelName, results = evaluateDistiller(questions)

        print("\n Results for : " + modelName + "\n\n")
        
        total = str(results['totalFParts'])
        tp = results['TP']*1.0
        fn = results['FN']*1.0
        fp = results['FP']*1.0

        print("Total Focus Parts : " + total)

        print("-- TP : " + str(tp))
        print("-- FN : " + str(fn))
        print("-- FP : " + str(fp))

        precision = tp/(tp+fp)

        print("\n-- Precision : " + str(precision))

        recall = tp/(tp+fn)

        print("-- Recall : " + str(recall))

        fScore = (2*precision*recall)/(precision+recall)

        print("-- F-Score : " + str(fScore))
        

if 'distiller' in sys.argv:
    evalDisplay(ourQuestions, 'distiller')
