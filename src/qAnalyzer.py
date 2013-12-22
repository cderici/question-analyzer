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


    def extractFocusMod(self):
        return Distiller(self.question).distillQuestion()
        
    def showFocusMod(self):
        focus, mod = self.extractFocusMod()

        focusText = "Not Found"
        modText = "Not Found"

        if focus:
            focusText = ""
            for focusPart in focus:
                focusText += QPart.getPartField(focusPart, 'text') + " "

        if mod:
            modText = ""
            for modPart in mod:
                modText += QPart.getPartField(modPart, 'text') + " "

        print(u"Q: {} || Focus: {} || Mod: {}".format(self.question.questionText, focusText, modText))


class MassAnalyzer:
    questionSet = None

    def __init__(self, questions = None):
        self.questionSet = questions


    # filterByTagValue('depenTag', 'SENTENCE', 'text', 'nedir')
    def filterByPartValue(self, tagType, tagName, partType, partValue):
        filtered = []

        for q in self.questionSet:
            PART = QPart.getQPartWithField(q.questionParts, tagType, tagName)
            if PART:
                if QPart.getPartField(PART, partType) == partValue:
                    filtered.append(q)
                else:
                    continue
            else:
                continue

        return filtered


    @staticmethod
    def massShowFocusMod(questionSet):
        for question in questionSet:
            QuestionAnalysis(question).showFocusMod()
        

    


ourQuestions = MaltImporter().importMaltOutputs(qFilePath, qParsedFilePath)

analyzer = QuestionAnalysis(ourQuestions[0])

# QuestionAnalysis.visualizeAll(ourQuestions)

# analyzer.showFocusMod()


mass = MassAnalyzer(ourQuestions)

filteredNedir = mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'nedir')

filteredVerilir = mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'verilir')

print("\n\n -- nedir -- \n\n")

MassAnalyzer.massShowFocusMod(filteredNedir)

print("\n\n -- verilir -- \n\n")

MassAnalyzer.massShowFocusMod(filteredVerilir)
