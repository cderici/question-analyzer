# -*- coding: utf-8 -*-

import qVisualizer
from maltImporter import MaltImporter
from question import Question, QPart
from distiller import Distiller

import codecs;

qFilePath = 'q.q';
qParsedFilePath = 'q_parsed.qp';


class QuestionAnalysis:
    question = None;

    def __init__(self, question = None):
        self.question = question;

    def visualizeQuestion(self):
        qVisualizer.produceVisualPage(self.question.questionParts)

    @staticmethod
    def visualizeAll(questions):
        qVisualizer.visualizeAllQuestions(questions)


    def extractFocusMod(self):
        dist = Distiller(self.question)


        """ TODO : fConf and mConf are total confidences (e.g. fConf is equal for each part of the focus), but """
        ruleFocus, ruleMod, fRuleConf, mRuleConf = dist.FM_Distiller()

        glassFocus, glassMod, fGlassConf, mGlassConf = dist.HMM_Glasses()

        self.question.focus = ruleFocus
        self.question.mod = ruleMod

        self.question.focusConfidence = fRuleConf
        self.question.focusConfidence = mRuleConf

        return ruleFocus, ruleMod
        
    def showFocusMod(self):
        focus, mod = self.extractFocusMod()

        focusText = "Not Found"
        modText = "Not Found"

        if focus:
            focusText = ""
            for focusPart in focus:
                focusText += QPart.getPartField(focusPart, 'text') + " "

        if mod:
            modText = ""
            for modPart in mod:
                modText += QPart.getPartField(modPart, 'text') + " "

        print(u"Q: {} || Focus: {} || Mod: {}".format(self.question.questionText, focusText, modText))


class MassAnalyzer:
    questionSet = None

    def __init__(self, questions = None):
        self.questionSet = questions


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

    @staticmethod
    def massShowFocusMod(questionSet):
        for question in questionSet:
            QuestionAnalysis(question).showFocusMod()
