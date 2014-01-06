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
    qFocusConfidence = 0

    qMods = []
    qModsConfidence = 0

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
        return False, False, 0, 0


    # this should be general for all domains, maybe this whole class should be that way
    def ruleBasedExtractor(self):

        qParts = self.question.questionParts

        SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')

        if not SEN:
            # raise RuntimeError("Something's REALLY wrong! Here's the question: " + self.question.questionText)
            return False, False, 0, 0

        SENtext = QPart.getPartField(SEN, 'text')

        # nedir
        if SENtext == 'nedir':

            return nedirExpert(self.question, qParts)

        # verilir
        elif SENtext == 'verilir':

            return verilirExpert(self.question, qParts)

        elif SENtext == 'denir' or SENtext == 'denilir' or SENtext == 'denilmektedir':
            
            return denirExpert(self.question, qParts)

        # hangisidir
        elif SENtext == 'hangisidir' or SENtext == 'hangileridir':

            return hangisidirExpert(self.question, qParts)

        # ... hangi ...
        elif self.checkForBetweenHangi(qParts):
            
            return hangiBtwExpert(self.question, qParts)

        else:
            return False, False, 0, 0


        # neresidir/nerede

        # ne zaman

        # kac/kaci/kacini/ne kadar
        
        return False, False, 0, 0


    def checkForBetweenHangi(self, qParts):
        hangiParts = QPart.getAllPartsWithField(qParts, 'text', 'hangi')

        hangiFiltered = [part for part in hangiParts if (QPart.getPartField(part, 'depenTag') != 'DERIV')]

        return hangiFiltered != []
