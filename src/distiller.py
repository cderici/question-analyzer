# -*- coding: utf-8 -*-

from question import Question, QPart
from deepDistiller import *
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

        if not SEN:
            # raise RuntimeError("Something's REALLY wrong! Here's the question: " + self.question.questionText)
            return False, False

        SENtext = QPart.getPartField(SEN, 'text')

        # nedir
        if SENtext == 'nedir':

            return handleNedir(self.question, qParts)

        # verilir
        elif SENtext == 'verilir':

            return handleVerilir(self.question, qParts)

        elif SENtext == 'denir' or SENtext == 'denilir' or SENtext == 'denilmektedir':
            
            return handleDenir(self.question, qParts)

        # hangisidir
        elif SENtext == 'hangisidir' or SENtext == 'hangileridir':

            return handleHangiHangileri(self.question, qParts)

        # ... hangi ...
        elif self.checkForBetweenHangi(qParts):
            
            return handleBetweenHangi(self.question, qParts)

        else:
            return False, False





        # denir
        # .... hangi ....

        # neresidir/nerede

        # ne zaman

        # kac/kaci/kacini/ne kadar
        
        return False, False


    def checkForBetweenHangi(self, qParts):
        hangiParts = QPart.getAllPartsWithField(qParts, 'text', 'hangi')

        hangiFiltered = [part for part in hangiParts if (QPart.getPartField(part, 'depenTag') != 'DERIV')]

        return hangiFiltered != []
