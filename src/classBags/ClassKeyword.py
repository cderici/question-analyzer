import codecs;
import collections;
import math;

class MaltImporter:

    questions = [];
    
    def getRawQuestionTexts(self, qFilePath):
        qFile = codecs.open(qFilePath, 'r', 'utf-8');
        qTexts = qFile.readlines();
        qTexts = [text.strip().split('|') for text in qTexts];

        return qTexts; ## list of raw questions with Focus and Mod

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


    def importMaltOutputs(self, qFilePath, qParsedFilePath):
        self.questions = [];

        qTexts = self.getRawQuestionTexts(qFilePath);
        qTextParts = self.getParsedQuestionTexts(qParsedFilePath);

        length = len(qTexts);

        for i in range(0, length):
            question = Question(qTexts[i][0], qTextParts[i]);
            
            question.coarseClass = qTexts[i][3];
            question.fineClass = qTexts[i][4];
            
            self.questions.append(question);
            
        return self.questions;



class Question:
    questionText = '';
	
    coarseClass = '';
    fineClass = '';
    
    questionParts = [];

    def __init__(self, text, parts):
        self.questionText = text;
        self.questionParts = parts;


class RuleClass:
    coarseCategory = '';
    fineCategory = '';
    
    parts = None;

    def __init__(self, coarseCategory, fineCategory):
        self.coarseCategory = coarseCategory;
        self.fineCategory = fineCategory;

        self.parts = collections.defaultdict(lambda : 0);

    
def buildRuleClasses(questions):
    classes  = [category.split('|') for category in list(set([question.coarseClass + '|' + question.fineClass for question in questions]))];
    
    _ruleClasses = [RuleClass(category[0], category[1]) for category in classes];

    parts = collections.defaultdict(lambda: set());
        
    for question in questions:
        
        classIndex = 0;
        
        for i in range(0, len(_ruleClasses)):
            if(_ruleClasses[i].coarseCategory == question.coarseClass and _ruleClasses[i].fineCategory == question.fineClass):
                classIndex = i;
                break;
        
        for part in question.questionParts:
            if(part[2] != '_' and part[2] != '.'):
                _ruleClasses[classIndex].parts[part[2]] += 1;
                parts[part[2]].add(question.coarseClass+'|'+question.fineClass);

    noOfClasses = len(_ruleClasses);
    print(noOfClasses);
                
    for _ruleClass in _ruleClasses:
        for key in _ruleClass.parts:
            tf = 1.0 + math.log10(_ruleClass.parts[key]);
            idf = math.log10(noOfClasses/(1.0 * len(parts[key])));
            print(_ruleClass.coarseCategory + '\t' + _ruleClass.fineCategory + '\t' + key + '\t' + str(tf) + '\t' + str(idf) + '\t' + str(tf * idf));

questions = MaltImporter().importMaltOutputs('q.q', 'q_parsed.qp')

buildRuleClasses(questions);
