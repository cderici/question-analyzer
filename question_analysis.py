
import codecs;
from itertools import groupby;

qFilePath = 'q.q';
qParsedFilePath = 'q_parsed.qp';

class Question:
    questionText = '';

    questionParts = [];

    root = None;

    def __init__(self, qText, qParts):
        self.questionText = qText;
        self.questionParts = qParts;

        self.findRoot();

    def findRoot(self):
        temp = [a for a in self.questionParts if a[1] == '.'];

        if(len(temp) == 1):
            self.root = temp[0];
        else:
            self.root = None;

    def findChilds(self, node):
        return [part for part in self.questionParts if part[6] == node[0]];

    def findParent(self, node):
        temp = [part for part in self.questionParts if part[0] == node[6]];

        if(len(temp) == 1):
            return temp[0];
        else:
            return None;

class Parser:

    questions = [];

    def getRawQuestionTexts(self, qFilePath):
        qFile = codecs.open(qFilePath, 'r', 'utf-8');
        qTexts = qFile.readlines();
        qTexts = [text.strip() for text in qTexts];

        return qTexts;

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
        
        return questions;
    
    def parseFile(self, qFilePath, qParsedFilePath):
        self.questions = [];

        qTexts = self.getRawQuestionTexts(qFilePath);
        qTextParts = self.getParsedQuestionTexts(qParsedFilePath);

        length = len(qTexts);

        for i in range(0, length):
            self.questions.append(Question(qTexts[i], qTextParts[i]))            

        return self.questions;

parser = Parser();
questions = parser.parseFile(qFilePath, qParsedFilePath);



