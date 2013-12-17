# -*- coding: utf-8 -*-

from question import Question, QPart

import codecs

# Distiller is for extracting the question focus and 
# the lexical constraints, properties, classses or headwords of focus

class Distiller():

    question = None

    # focus is a list of ordered parts
    qFocus = None

    qFocusLexicalmods = None

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

            # we know that everyone in 'nedir' has subjects
            # but nevertheless
            if not SUBJ:
                return False
            else:
                
                SUBJtext = QPart.getPartField(SUBJ, 'text')
                
                if SUBJtext == u"adı" or SUBJtext == 'ismi' or SUBJtext == "nedeni":
                    # then we know that it should have a possessor
                    POSS = QPart.getQPartWithField(qParts, 'depenTag', 'POSSESSOR')

                    if not POSS:
                        raise RuntimeError("nedir SUBJECTS should have a possessor")
                    else:
                        focusList = [SUBJ, POSS]
                        focusList.extend(self.question.tracebackFrom(POSS))
                        self.qFocus = focusList

                        otherChildrenList = self.question.findChildren(SUBJ, POSS)

                        if otherChildrenList != []:
                            rightMost = otherChildrenList[len(otherChildrenList)-1]
                            self.qFocusLexicalmods = self.question.tracebackFrom(otherParent)

                        return self.qFocus, self.qFocusLexicalmods

        else:
            return False
        # verilir

        # denir

        # hangisidir

        # .... hangi ....

        # neresidir/nerede

        # ne zaman

        # kac/kaci/kacini/ne kadar
        
        return False
