# -*- coding: utf-8 -*-

from question import Question, QPart
from ruler import *
import codecs

# Distiller is for extracting the question focus and 
# the lexical constraints, properties, classses or headwords of focus

class Distiller():

    question = None

    # focus is a list of ordered parts
    qFocus = []

    qMods = []

    def __init__(self, question = None):
        self.question = question
        self.qFocus = []
        self.qMods = []


    def distillQuestion(self):
        ruleBased = self.ruleBasedExtractor()

        if not ruleBased:
            return self.goForStatistics()
        else:
            return ruleBased

    def goForStatistics(self):
        print(self.question.questionText + " -> Statistical Approach")
        return False, False


    # this should be general for all domains, maybe this whole class should be that way
    def ruleBasedExtractor(self):

        qParts = self.question.questionParts

        SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')

        SENtext = QPart.getPartField(SEN, 'text')

        # nedir
        if SENtext == 'nedir':

            return handleNedir(self.question, qParts)

        # verilir
        elif SENtext == 'verilir':

            return handleVerilir(self.question, qParts)

        # hangisidir
        elif SENtext == 'hangisidir' or SENtext == 'hangileridir':

            return handleHangiHangileri(self.question, qParts)

        else:
            return False, False





        # denir
        # .... hangi ....

        # neresidir/nerede

        # ne zaman

        # kac/kaci/kacini/ne kadar
        
        return False, False
