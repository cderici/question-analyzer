
import codecs;
import math;

qFilePath = 'q.q';
qParsedFilePath = 'q_parsed.qp';

classPath = 'rule/classes';
classQuestionWordsPath = 'rule/question_words';
classQuestionKeywordsPath = 'rule/qeustion_keywords';

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
            self.questions.append(Question(qTexts[i][0], qTextParts[i]))            

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
    questions = [];

    def __init__(self, questions = []):
        self.questions = questions;

class RuleClass:
    coarseCategory = '';
    fineCategory = '';

    qxnWords = [];
    qnxWordsScores = [];
    keywords = [];
    keywordsScores = [];

    def __init__(self, coarseCategory, fineCategory):
        self.coarseCategory = coarseCategory;
        self.fineCategory = fineCategory;

        self.qxnWords = [];
        self.keywords = [];
        self.qnxWordsScores = [];
        self.keywordsScores = [];

    def addToQxnWords(self, word):
        self.qxnWords.append(word);

    def addToKeywords(self, word):
        self.keywords.append(word);

    def getQxnWordScore(self, word, method):
        for i in range(0, len(self.qxnWords)):
            if(self.qxnWords[i] == word and method == 'e'):
                return self.qnxWordsScores[i];
            if(self.qxnWords[i].startswith(word) and method == 'c1'):
                return self.qnxWordsScores[i];
            if(word.startswith(self.qxnWords[i]) and method == 'c2'):
                return self.qnxWordsScores[i];
        return 0.0;

    def getKeywordScore(self, word, method):
        for i in range(0, len(self.keywords)):
            if(self.keywords[i] == word and method == 'e'):
                return self.keywordsScores[i];
            if(self.keywords[i].startswith(word) and method == 'c1'):
                return self.keywordsScores[i];
            if(word.startswith(self.keywords[i]) and method == 'c2'):
                return self.keywordsScores[i];
        return 0.0;

class RuleBasedQuestionClassification:
    questions = [];
    
    finalCategory = [];
    
    ruleClasses = [];
        
    def __init__(self, questions, classPath, classQuestionWordsPath, classQuestionKeywordsPath):
        self.questions = questions;

        self.readClassDefinitions(classPath, classQuestionWordsPath, classQuestionKeywordsPath);
        self.calculateFeatureScores();

    def getRuleClass(self, coarseCategory, fineCategory):
        results = [ruleClass for ruleClass in self.ruleClasses if ruleClass.coarseCategory == coarseCategory and ruleClass.fineCategory == fineCategory];
        if(len(results) > 0):
            return results[0];
        else:
            return None;

    def calculateFeatureScores(self):
        allQnxWords = [];
        [[allQnxWords.append(word) for word in ruleClass.qxnWords] for ruleClass in self.ruleClasses];

        allKeywords = [];
        [[allKeywords.append(word) for word in ruleClass.keywords] for ruleClass in self.ruleClasses];

        for ruleClass in self.ruleClasses:
            ruleClass.qnxWordsScores = [math.log(len(allQnxWords) / len([w for w in allQnxWords if w == word])) for word in ruleClass.qxnWords];
            ruleClass.keywordsScores = [math.log(len(allKeywords) / len([w for w in allKeywords if w == word])) for word in ruleClass.keywords];

        '''
        for ruleClass in self.ruleClasses:
            for i in range(0, len(ruleClass.qxnWords)):
                print(ruleClass.qxnWords[i] + '\t' + str(ruleClass.qnxWordsScores[i]));
        
        for ruleClass in self.ruleClasses:
            for i in range(0, len(ruleClass.keywords)):
                print(ruleClass.keywords[i] + '\t' + str(ruleClass.keywordsScores[i]));
        '''
        
    def readClassDefinitions(self, classPath, classQuestionWordsPath, classQuestionKeywordsPath):

        ##Coarse and Fine Category
        file = codecs.open(classPath, 'r', 'utf-8');

        lines = file.readlines();
        lines = [line.strip().split('\t') for line in lines];

        self.ruleClasses = [RuleClass(line[0], line[1]) for line in lines];
        
        file.close();

        ##Question words
        file = codecs.open(classQuestionWordsPath, 'r', 'utf-8');

        lines = file.readlines();
        lines = [line.strip().split('\t') for line in lines];                                
       
        [self.getRuleClass(line[0], line[1]).addToQxnWords(line[2]) for line in lines if self.getRuleClass(line[0], line[1]) is not None];
        
        file.close();

        ##Keywords
        file = codecs.open(classQuestionKeywordsPath, 'r', 'utf-8');

        lines = file.readlines();
        lines = [line.strip().split('\t') for line in lines];

        [self.getRuleClass(line[0], line[1]).addToKeywords(line[2]) for line in lines if self.getRuleClass(line[0], line[1]) is not None];
        
        file.close();

    def findCategories(self):

        self.finalCategory = [];
        
        for question in self.questions:
            scores1 = [sum([ruleClass.getQxnWordScore(item[1], 'e') for item in question.questionParts]) * 2 for ruleClass in self.ruleClasses];
            scores2 = [sum([ruleClass.getQxnWordScore(item[1], 'c1') for item in question.questionParts]) * 1 for ruleClass in self.ruleClasses];
            scores3 = [sum([ruleClass.getQxnWordScore(item[1], 'c2') for item in question.questionParts]) * 1 for ruleClass in self.ruleClasses];

            scores4 = [sum([ruleClass.getKeywordScore(item[1], 'e') for item in question.questionParts]) * 4 for ruleClass in self.ruleClasses];
            scores5 = [sum([ruleClass.getKeywordScore(item[1], 'c1') for item in question.questionParts]) * 2 for ruleClass in self.ruleClasses];
            scores6 = [sum([ruleClass.getKeywordScore(item[1], 'c2') for item in question.questionParts]) * 2 for ruleClass in self.ruleClasses];

            totalScores = [scores1[i] + scores2[i] + scores3[i] + scores4[i] + scores5[i] + scores6[i] for i in range(len(scores1))];

            indexOfBestScore = totalScores.index(max(totalScores));

            self.finalCategory.append(self.ruleClasses[indexOfBestScore]);
            
            print(self.ruleClasses[indexOfBestScore].coarseCategory + '\t' + self.ruleClasses[indexOfBestScore].fineCategory+ '\t'+ str(max(totalScores)));
        
analyzer = QuestionAnalysis(Parser().parseFile(qFilePath, qParsedFilePath))
rule = RuleBasedQuestionClassification(analyzer.questions, classPath, classQuestionWordsPath, classQuestionKeywordsPath);
rule.findCategories();


