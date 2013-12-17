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


    def extractFocusLAT(self):
        return Distiller(self.question).distillQuestion()
        


ourQuestions = MaltImporter().importMaltOutputs(qFilePath, qParsedFilePath)

analyzer = QuestionAnalysis(ourQuestions[0])

# analyzer.visualizeQuestion()

# QuestionAnalysis.visualizeAll(ourQuestions)

focus, mod = analyzer.extractFocusLAT()

focusText = ""

for focusPart in reversed(focus):
    focusText += QPart.getPartField(focusPart, 'text') + " "

print ourQuestions[0].questionText + "\n"
print "Focus: " + focusText
# q = ourQuestions[0]

# p = q.questionParts[4]

# print q.tracebackFrom(p)
