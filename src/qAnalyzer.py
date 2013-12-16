import qVisualizer
from maltImporter import MaltImporter
from question import Question
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


    def extractFocusLAT(self):
        return Distiller(self.question).distillQuestion()
        


ourQuestions = MaltImporter().importMaltOutputs(qFilePath, qParsedFilePath)

analyzer = QuestionAnalysis(ourQuestions[0])

# analyzer.visualizeQuestion()

QuestionAnalysis.visualizeAll(ourQuestions)
