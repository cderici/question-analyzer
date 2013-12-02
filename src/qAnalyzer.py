import qVisualizer

import codecs;

qFilePath = 'q.q';
qParsedFilePath = 'q_parsed.qp';

class Parser:

    questions = [];

    def getRawQuestionTexts(self, qFilePath):
        qFile = codecs.open(qFilePath, 'r', 'utf-8');##utf-8 file
        qTexts = qFile.readlines();
        qTexts = [text.strip() for text in qTexts];

        return qTexts; ## list of raw questions

    def getParsedQuestionTexts(self, qParsedFilePath):
        qFile = codecs.open(qParsedFilePath, 'r', 'utf-8');
        qTexts = qFile.readlines();
        qTexts = [text.strip().split('\t') for text in qTexts];

        questions = [];
        qParts = [];

        for text in qTexts:
            if(len(text) > 1):
                if(text[1] == "."):
                    
                    qParts.append(text);
                    questions.append(qParts);
                    qParts = [];
                else:
                    qParts.append([t.replace('\ufeff', '') for t in text]);
        
        return questions;##Question parts -> list of list
    
    def parseFile(self, qFilePath, qParsedFilePath):
        self.questions = [];

        qTexts = self.getRawQuestionTexts(qFilePath);
        qTextParts = self.getParsedQuestionTexts(qParsedFilePath);

        length = len(qTexts);

        for i in range(0, length):
            self.questions.append(Question(qTexts[i], qTextParts[i]))            

        return self.questions;

class QPart:
    depID = '';
    partText = '';
    depTag = '';


    morphRoot = '';
    POStag = '';
    POSextra = '';
    morphDetail = '';
    rootID = '';
    
    children = [];

    ##Test
    
class Question:
    ##Raw question text
    questionText = '';

    ##Dependency parsed question parts
    questionParts = [];

    ##Root of the parts -- Always (.) period
    root = None;

    ##Focus of the question
    focus = '';

    ##LAT of the question
    lat = '';

    def __init__(self, qText= '', qParts = []):
        self.questionText = qText;
        self.questionParts = qParts;

        self.findRoot();

    def findRoot(self):
        temp = [a for a in self.questionParts if a[1] == '.'];

        if(len(temp) == 1):
            self.root = temp[0];
        else:
            self.root = None;

    def findChildren(self, node):
        return [part for part in self.questionParts if part[6] == node[0]];

    def findParent(self, node):
        temp = [part for part in self.questionParts if part[0] == node[6]];

        if(len(temp) == 1):
            return temp[0];
        else:
            return None;

    def findRelations(self, relationText):
        return [part for part in self.questionParts if part[7] == relationText];

class QuestionAnalysis:
    question = None;

    def __init__(self, question = None):
        self.question = question;

    def visualizeQuestion(self):
        qVisualizer.produceVisualPage(self.question.questionParts)

    @staticmethod
    def visualizeAll(questions):
        qVisualizer.visualizeAllQuestions(questions)


ourQuestions = Parser().parseFile(qFilePath, qParsedFilePath)

analyzer = QuestionAnalysis(ourQuestions[0])

# analyzer.visualizeQuestion()

QuestionAnalysis.visualizeAll(ourQuestions)
