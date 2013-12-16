from question import Question, QPart

import codecs

# Distiller is for extracting the question focus and 
# the lexical constraints, properties, classses or headwords of focus

class Distiller():

    question = None

    qFocus = None

    qFocusLexicalmods = None

    def __init__(self, question = None):
        self.question = question


    def distillQuestion(self):
        if not ruleBasedExtractor():
            goForStatistics()

    def goForStatistics(self):
        self.qFocus = 'couldnt find '
        print(self.qFocus + "Not implemented yet: Statistical Approach")


    # this should be general for all domains, maybe this whole class should be that way
    def ruleBasedExtraction(self):

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
                
                if SUBJtext == 'adı' or SUBJtext == 'ismi' or SUBJtext == "nedeni":
                    # then we know that it should have a possessor
                    POSS = QPart.getQPartWithField(qParts, 'depenTag', 'POSSESSOR')

                    if not POSS:
                        raise RuntimeError("nedir SUBJECTS should have a possessor")
                    else:
                        # TO BE CONTINUED :)
                        return False

        # verilir

        # denir

        # hangisidir

        # .... hangi ....

        # neresidir/nerede

        # ne zaman

        # kac/kaci/kacini/ne kadar
        
        return False
