# -*- coding: utf-8 -*-

from question import Question, QPart
from deepDistiller import *
import codecs

# Distiller is for extracting the question focus and 
# the lexical constraints, properties, classses or headwords of focus

class Distiller():

    question = None
    genericEnable = None

    # focus is a list of ordered parts
    qFocus = []
    qFocusConfidence = 0

    qMods = []
    qModsConfidence = 0

    def __init__(self, question, genericEnable):
        self.question = question
        self.genericEnable = genericEnable
        self.qFocus = []
        self.qMods = []

    # this should be general for all domains, maybe this whole class should be that way
    def FM_Distiller(self):

        qParts = self.question.questionParts

        SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')

        if not SEN:
            # raise RuntimeError("Something's REALLY wrong! Here's the question: " + self.question.questionText)
            #print("ATTENTION: A question *without* a sentence has just been detected! -> " + self.question.questionText)
            return [], [], 0, 0

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
        
        # ne kadardır
        elif SENtext == 'kadardır'.decode('utf-8') and self.checkForNeKadardir(qParts, SEN):
            
            return neKadardirExpert(self.question, qParts)

        else:
            if self.genericEnable:
                return genericExpert(self.question, qParts)
            else:
                return [],[],0,0


        # neresidir/nerede

        # ne zaman

        # kac/kaci/kacini/ne kadar
        
        # dummy return, should never reach here
        return [], [], 0, 0


    def checkForBetweenHangi(self, qParts):
        hangiParts = QPart.getAllPartsWithField(qParts, 'text', 'hangi')

        hangiFiltered = [part for part in hangiParts if (QPart.getPartField(part, 'depenTag') != 'DERIV')]

        return hangiFiltered != []


    def checkForNeKadardir(self, qParts, SEN):
        
        # we know that SEN is 'kadardır', 
        # so its DERIV child should have a MODIFIER child texted 'ne'

        derivChildren = self.question.findChildrenDepenTag(SEN, 'DERIV')

        derivChild = False
        for child in derivChildren:
            if QPart.getPartField(child, 'morphRoot') == 'kadar':
                derivChild = child
                break
        
        if not derivChild:
            return False
        
        neChildren = self.question.findChildrenDepenTag(derivChild, 'OBJECT')

        for child in neChildren:
            if QPart.getPartField(child, 'text') == 'ne':
                return child

        return False
