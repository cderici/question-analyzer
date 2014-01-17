# -*- coding: utf-8 -*-

import sys

sys.path.append('fm-distiller')
sys.path.append('data')
sys.path.append('visualizer')
sys.path.append('glasses')

import qVisualizer
from question import Question, QPart
from distiller import Distiller
from hmmLearner import *
from hmmGlasses import *

import codecs;

qFilePath = 'data/q.q';
qParsedFilePath = 'data/q_parsed.qp';


class QuestionAnalysis:
    question = None;

    def __init__(self, question = None):
        self.question = question;

    def visualizeQuestion(self):
        qVisualizer.produceVisualPage(self.question.questionParts)

    @staticmethod
    def visualizeAll(questions):
        qVisualizer.visualizeAllQuestions(questions)
        
    @staticmethod
    def combineGlasses(glassResult1, glassResult2):
        result = []
        for i in range(0, len(glassResult1)):
            fmnConfPart1 = glassResult1[i]
            fmnConfPart2 = glassResult2[i]

            if fmnConfPart1[0] ==  fmnConfPart2[0]:
                if fmnConfPart1[1] >= fmnConfPart2[1]:
                    result.append(fmnConfPart1)
                else:
                    result.append(fmnConfPart2)
            else:
                if fmnConfPart1[0] == 'FOC':
                    result.append(fmnConfPart1)
                elif fmnConfPart2[0] == 'FOC':
                    result.append(fmnConfPart2)
                else:
                    if fmnConfPart1[1] >= fmnConfPart2[1]:
                        result.append(fmnConfPart1)
                    else:
                        result.append(fmnConfPart2)

        return result
            

    def extractFocusMod(self, reverseGlass, normalGlass):
        dist = Distiller(self.question)

        ruleFocus, ruleMod, fRuleConf, mRuleConf = dist.FM_Distiller()

        mostProbRevSeq = reverseGlass.computeFocusProbs(self.question)
        mostProbSeq = normalGlass.computeFocusProbs(self.question)

        hmmResults = QuestionAnalysis.combineGlasses(mostProbRevSeq, mostProbSeq)

        """ Combining Focus Parts of both distiller and hmm-glasses"""
        focusCombined = []
        focusConfidences = []
        # note : order in serialization doesn't matter at this point
        for part in serializeDepTree(self.question.questionParts):
            # checking first what does hmm-glasses thinks about this part
            inHmmFoc = False
            for hmmRes in hmmResults:
                if part == hmmRes[2] and hmmRes[0] == 'FOC':
                    inHmmFoc = hmmRes
                    break

            if part in ruleFocus:
                if inHmmFoc: # both distiller and hmm thinks it should be focus
                    focusCombined.append(part)
                    focusConfidences.append(max(fRuleConf, inHmmFoc[1]))
                else: # hmm doesn't think it's a focus, but distiller does
                    focusCombined.append(part)
                    focusConfidences.append(fRuleConf)

            elif inHmmFoc: 
                # hmm-glasses thinks this part is focus, 
                # but distiller doesn't agree
                
                # in hmm-glasses we trust!
                focusCombined.append(part)
                focusConfidences.append(inHmmFoc[1])
            # we don't do anything for the part for which both distiller and hmm-glasses think that it doesn't belong to focus
                
        focusCombined.reverse()
        focusConfidences.reverse()

        self.question.focus = focusCombined

        self.question.mod = ruleMod # out of question at this point

        self.question.focusConfidence = focusConfidences

        self.question.focusConfidence = mRuleConf # out of question at this point

        return focusCombined, focusConfidences

    def showFocusMod(self):
        focusCombined, focusConfidences = self.extractFocusMod()

        focusText, modText = self.question.extract_FM_Text()

        print(u"Q: {} || Focus: {}".format(self.question.questionText, focusText))


class MassAnalyzer:
    questionSet = None

    normalGlass = None
    reverseGlass = None

    def __init__(self, questions = None):
        self.questionSet = questions
        self.normalGlass = Glass(questions, reverse=False)
        self.reverseGlass = Glass(questions, reverse=True)

    # filterByTagValue('depenTag', 'SENTENCE', 'text', 'nedir')
    def filterByPartValue(self, tagType, tagName, partType, partValue):
        filtered = []

        for q in self.questionSet:
            if tagName == '*':
                for part in q.questionParts:
                    isDeriv = (QPart.getPartField(part, 'depenTag') != 'DERIV')

                    if isDeriv and QPart.getPartField(part, partType) == partValue:
                        filtered.append(q)
                    else:
                        #print(q.questionText)
                        continue
            else:
                PART = QPart.getQPartWithField(q.questionParts, tagType, tagName)
                if PART:
                    if QPart.getPartField(PART, partType) == partValue:
                        filtered.append(q)
                    else:
                        #print(q.questionText)
                        continue
                else:
                    #print(q.questionText)
                    continue

        return filtered


    """ 
    filters questions that can't be handled by our current experts
    """
    def filterOthers(self, currentExpertQuestions):

        filtered = []

        for q in self.questionSet:
            if q not in currentExpertQuestions:
                filtered.append(q)

        return filtered

    def massAnalyze(self):
        for question in self.questionSet:
            QuestionAnalysis(question).extractFocusMod(self.normalGlass, self.reverseGlass)
            focusText, modText = question.extract_FM_Text()

            print(u"Q: {} || Focus: {}".format(question.questionText, focusText))

    @staticmethod
    def massShowFocusMod(questionSet):
        for question in questionSet:
            QuestionAnalysis(question).showFocusMod()
