# -*- coding: utf-8 -*-

from question import Question, QPart

import codecs

# Distiller is for extracting the question focus and 
# the lexical constraints, properties, classses or headwords of focus

class Distiller():

    question = None

    # focus is a list of ordered parts
    qFocus = None

    qMods = None

    def __init__(self, question = None):
        self.question = question


    def distillQuestion(self):
        ruleBased = self.ruleBasedExtractor()

        if not ruleBased:
            return self.goForStatistics()
        else:
            return ruleBased

    def goForStatistics(self):
        self.qFocus = 'couldnt find '
        print(self.qFocus + "Not implemented yet: Statistical Approach")
        return False


    # this should be general for all domains, maybe this whole class should be that way
    def ruleBasedExtractor(self):

        qParts = self.question.questionParts

        SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')

        SENtext = QPart.getPartField(SEN, 'text')

        # nedir
        if SENtext == 'nedir':

            SUBJ = QPart.getQPartWithField(qParts, 'depenTag', 'SUBJECT')
            """
            we know that everyone in 'nedir' has subjects
            but nevertheless
            """
            if not SUBJ:
                return False, False
            else:
                
                SUBJtext = QPart.getPartField(SUBJ, 'text')
                
                if SUBJtext == u"adı" or SUBJtext == 'ismi' or SUBJtext == "nedeni":
                    """
                    then we know that it should have a possessor
                    TODO : find the CORRECT POSSESSOR 
                    """
                    POSS = QPart.getQPartWithField(qParts, 'depenTag', 'POSSESSOR')

                    if not POSS:
                        raise RuntimeError("nedir SUBJECTS should have a possessor")
                    else:
                        focusList = [SUBJ, POSS]
                        posRest, lastTamlayan = self.question.tracebackFromFoldTamlama(POSS)
                        focusList.extend(posRest)
                        
                        self.qFocus = focusList

                        """
                        adding to mods the additional parts starting from the last possessor
                        """
                        self.qMods = self.question.tracebackFrom(lastTamlayan)

                        """
                        checking if the subject has children other than POSS
                        """
                        otherChildrenList = self.question.findChildren(SUBJ, POSS)

                        if otherChildrenList != []:
                            rightMost = otherChildrenList[len(otherChildrenList)-1]
                            self.qMods.append(rightMost)
                            self.qMods.extend(self.question.tracebackFrom(rightMost))

                        return self.qFocus, self.qMods

        else:
            return False, False
        # verilir

        # denir

        # hangisidir

        # .... hangi ....

        # neresidir/nerede

        # ne zaman

        # kac/kaci/kacini/ne kadar
        
        return False, False
