
import codecs;
import math;

from maltImporter import MaltImporter;

classPath = 'classBags/classes';
classQuestionWordsPath = 'classBags/question_words';
classQuestionKeywordsPath = 'classBags/question_keywords';

class RuleClass:
    coarseCategory = '';
    fineCategory = '';

    qxnWords = [];
    qnxWordsScores = [];
    keywords = [];
    keywordsScores = [];
    
    parts = [];

    def __init__(self, coarseCategory, fineCategory):
        self.coarseCategory = coarseCategory;
        self.fineCategory = fineCategory;

        self.qxnWords = [];
        self.keywords = [];
        self.qnxWordsScores = [];
        self.keywordsScores = [];
        
        self.parts = [];

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
        ##file = codecs.open(classQuestionKeywordsPath, 'r', 'utf-8');

        ##lines = file.readlines();
        ##lines = [line.strip().split('\t') for line in lines];

        ##[self.getRuleClass(line[0], line[1]).addToKeywords(line[2]) for line in lines if self.getRuleClass(line[0], line[1]) is not None];
        
        ##file.close();

    def doClassification(self):

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
        
        total_coarse_TP = 0.0;
        total_coarse_TN = 0.0;
        total_coarse_FP = 0.0;
        total_coarse_FN = 0.0;
        
        total_coarse_FMeasure = 0.0;
        
        for i in range(0, len(self.ruleClasses)):
            coarse_TP = 0.0;
            coarse_TN = 0.0;
            coarse_FP = 0.0;
            coarse_FN = 0.0;
            
            coarse_Precision = 0.0;
            coarse_Recall = 0.0;
            coarse_FMeasure = 0.0;
            
            for j in range(0, len(self.finalCategory)):
                if(self.questions[j].coarseClass == self.ruleClasses[i].coarseCategory and self.finalCategory[j].coarseCategory == self.ruleClasses[i].coarseCategory):
                    coarse_TP += 1.0;
                    total_coarse_TP += 1.0;
                if(self.questions[j].coarseClass != self.ruleClasses[i].coarseCategory and self.finalCategory[j].coarseCategory != self.ruleClasses[i].coarseCategory):
                    coarse_TN += 1.0;
                    total_coarse_TN += 1.0;
                if(self.questions[j].coarseClass != self.ruleClasses[i].coarseCategory and self.finalCategory[j].coarseCategory == self.ruleClasses[i].coarseCategory):
                    coarse_FP += 1.0;
                    total_coarse_FP += 1.0;
                if(self.questions[j].coarseClass == self.ruleClasses[i].coarseCategory and self.finalCategory[j].coarseCategory != self.ruleClasses[i].coarseCategory):
                    coarse_FN += 1.0;
                    total_coarse_FN += 1.0

            if (coarse_TP + coarse_FP) != 0.0:
                coarse_Precision = coarse_TP / (coarse_TP + coarse_FP);
            if (coarse_TP + coarse_FN) != 0.0:
                coarse_Recall = coarse_TP / (coarse_TP + coarse_FN);
            if((coarse_Precision + coarse_Recall) > 0):
                coarse_FMeasure = 2 * coarse_Precision * coarse_Recall / (coarse_Precision + coarse_Recall);
            
            total_coarse_FMeasure += coarse_FMeasure;

            ##print('Coarse Class: ' + self.ruleClasses[i].coarseCategory + '\tCoarse TP: ' + str(coarse_TP) + '\tCoarse TN: ' + str(coarse_TN) + '\tCoarse FP: ' + str(coarse_FP) + '\tCoarse FN: ' + str(coarse_FN));
            ##print('Coarse Class: ' + self.ruleClasses[i].coarseCategory + '\tPrecision: ' + str(coarse_Precision) + '\tRecall: ' + str(coarse_Recall) + '\tFMeasure: ' + str(coarse_FMeasure));
        
        coarse_Precision = 0.0;
        coarse_Recall = 0.0;
        coarse_Micro_F = 0.0;
        coarse_Macro_F = 0.0;
        
        if(total_coarse_TP + total_coarse_FP) != 0 : 
            coarse_Precision = (total_coarse_TP / (total_coarse_TP + total_coarse_FP));
            
        if(total_coarse_TP + total_coarse_FN) != 0 : 
            coarse_Recall = (total_coarse_TP / (total_coarse_TP + total_coarse_FN));
    
        if(coarse_Precision + coarse_Recall) != 0:
            coarse_Micro_F = 2 * coarse_Precision * coarse_Recall / (coarse_Precision + coarse_Recall);

        coarse_Macro_F = total_coarse_FMeasure / len(self.ruleClasses);
        
        total_fine_TP = 0.0;
        total_fine_TN = 0.0;
        total_fine_FP = 0.0;
        total_fine_FN = 0.0;
        
        total_fine_FMeasure = 0.0;
        
        for i in range(0, len(self.ruleClasses)):
            fine_TP = 0.0;
            fine_TN = 0.0;
            fine_FP = 0.0;
            fine_FN = 0.0;
            
            fine_Precision = 0.0;
            fine_Recall = 0.0;
            fine_FMeasure = 0.0;
            
            for j in range(0, len(self.finalCategory)):          
                if(self.questions[j].fineClass == self.ruleClasses[i].fineCategory and self.finalCategory[j].fineCategory == self.ruleClasses[i].fineCategory):
                    fine_TP += 1.0;
                    total_fine_TP += 1.0;
                if(self.questions[j].fineClass != self.ruleClasses[i].fineCategory and self.finalCategory[j].fineCategory != self.ruleClasses[i].fineCategory):
                    fine_TN += 1.0;
                    total_fine_TN += 1.0;
                if(self.questions[j].fineClass != self.ruleClasses[i].fineCategory and self.finalCategory[j].fineCategory == self.ruleClasses[i].fineCategory):
                    fine_FP += 1.0;
                    total_fine_FP += 1.0;
                if(self.questions[j].fineClass == self.ruleClasses[i].fineCategory and self.finalCategory[j].fineCategory != self.ruleClasses[i].fineCategory):
                    fine_FN += 1.0;
                    total_fine_FN += 1.0;
            
            if (fine_TP + fine_FP) != 0.0:
                fine_Precision = fine_TP / (fine_TP + fine_FP);
            if (fine_TP + fine_FN) != 0.0:
                fine_Recall = fine_TP / (fine_TP + fine_FN);
            if((fine_Precision + fine_Recall) > 0):
                fine_FMeasure = 2 * fine_Precision * fine_Recall / (fine_Precision + fine_Recall);
            
            total_fine_FMeasure += fine_FMeasure;
            
            ##print('Fine Class: ' + self.ruleClasses[i].fineCategory + '\tFine TP: ' + str(fine_TP) + '\tFine TN: ' + str(fine_TN) + '\tFine FP: ' + str(fine_FP) + '\tFine FN: ' + str(fine_FN));
            ##print('Fine Class: ' + self.ruleClasses[i].fineCategory + '\tPrecision: ' + str(fine_Precision) + '\tRecall: ' + str(fine_Recall)+ '\tFMeasure: ' + str(fine_FMeasure));
            
        
        fine_Precision = 0.0;
        fine_Recall = 0.0;
        fine_Micro_F = 0.0;
        fine_Macro_F = 0.0;
        
        if(total_fine_TP + total_fine_FP) != 0 : 
            fine_Precision = (total_fine_TP / (total_fine_TP + total_fine_FP));
            
        if(total_fine_TP + total_fine_FN) != 0 : 
            fine_Recall = (total_fine_TP / (total_fine_TP + total_fine_FN));
    
        if(fine_Precision + fine_Recall) != 0:
            fine_Micro_F = 2 * fine_Precision * fine_Recall / (fine_Precision + fine_Recall);

        fine_Macro_F = total_fine_FMeasure / len(self.ruleClasses);
        
        print('Coarse Class Results:');
        print('Micro Average Precision: ' + str(coarse_Precision));
        print('Micro Average Recall: ' + str(coarse_Recall));
        print('Micro Average F-Measure: ' + str(coarse_Micro_F));
        print('Macro Average F-Measure: ' + str(coarse_Macro_F));
        
        print('Fine Class Results:');
        print('Micro Average Precision: ' + str(fine_Precision));
        print('Micro Average Recall: ' + str(fine_Recall));
        print('Micro Average F-Measure: ' + str(fine_Micro_F));
        print('Macro Average F-Measure: ' + str(fine_Macro_F));

