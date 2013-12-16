from question import Question, QPart

import codecs

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
        qFocus = 'couldnt find'
        print("Not implemented yet")


    # this should be general for all domains, maybe this whole class should be that way
    def ruleBasedExtraction(self):

        qParts = self.question.questionParts

        # nedir


        # verilir

        # denir

        # hangisidir

        # .... hangi ....

        # neresidir/nerede

        # ne zaman

        # kac/kaci/kacini/ne kadar
        
        return True
