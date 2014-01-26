
import codecs;
import math;

from maltImporter import MaltImporter;

class RuleClass:
    category = '';

    words = [];
    wordScores = [];
    
    parts = [];

    def __init__(self, cat):
        self.category = cat;

        self.words = [];
        self.wordScores = [];
        
        self.parts = [];

    def addToWords(self, word):
        self.words.append(word);

    def getWordScore(self, word, method):
        for i in range(0, len(self.words)):
            if(self.words[i] == word and method == 'e'):
                return self.wordScores[i];
            if(self.words[i].startswith(word) and method == 'c1'):
                return self.wordScores[i];
            if(word.startswith(self.words[i]) and method == 'c2'):
                return self.wordScores[i];
        return 0.0;
    
    def removeDuplicates(self):
        self.words = list(set(self.words));


class QuestionClass:
    
    coarse = '';
    fine = '';
    questions = [];
    originalQuestions = [];
    length = 0;
    
    def __init__(self, coarse, fine):
        self.coarse = coarse;
        self.fine = fine;
        self.questions = [];
    
    def setLength(self):
        self.originalQuestions = [question for question in self.questions];
        self.length = len(self.originalQuestions);
        
class RuleBasedQuestionClassification:
    questions = [];
    
    trainQuestions = [];
    testQuestions = [];
    
    fineRuleClasses = [];
    fineFinalCategory = [];
    
    coarseRuleClasses = [];
    coarsefinalCategory = [];

    def __init__(self, questions):
        
        self.questions = questions;

    def getFineRuleClass(self, fine):
        results = [ruleClass for ruleClass in self.fineRuleClasses if ruleClass.category == fine];
        if(len(results) > 0):
            return results[0];
        else:
            return None;
            
    def getCoarseRuleClass(self, coarse):
        results = [ruleClass for ruleClass in self.coarseRuleClasses if ruleClass.category == coarse];
        if(len(results) > 0):
            return results[0];
        else:
            return None;

    def calculateFineFeatureScores(self):
        allWords = [];
        [[allWords.append(word) for word in ruleClass.words] for ruleClass in self.fineRuleClasses];
        
        for ruleClass in self.fineRuleClasses:
            ruleClass.wordScores = [math.log(len(allWords) / len([w for w in allWords if w == word])) for word in ruleClass.words];
    
    def calculateCoarseFeatureScores(self):
        allWords = [];
        [[allWords.append(word) for word in ruleClass.words] for ruleClass in self.coarseRuleClasses];

        for ruleClass in self.coarseRuleClasses:
            ruleClass.wordScores = [math.log(len(allWords) / len([w for w in allWords if w == word])) for word in ruleClass.words];

    def trainModels(self):
            
        fineClassNames = list(set([question.fineClass for question in self.trainQuestions]));    
        self.fineRuleClasses = [RuleClass(fineClassName) for fineClassName in fineClassNames];

        coarseClassNames = list(set([question.coarseClass for question in self.trainQuestions]));
        self.coarseRuleClasses = [RuleClass(coarseClassName) for coarseClassName in coarseClassNames];
        
        for question in self.trainQuestions:
            
            fineClass = self.getFineRuleClass(question.fineClass);
            coarseClass = self.getCoarseRuleClass(question.coarseClass);
            
            [fineClass.addToWords(part[2]) for part in question.questionParts if part[2] != '_' and part[2] != '.'];
            [coarseClass.addToWords(part[2]) for part in question.questionParts if part[2] != '_' and part[2] != '.'];
        
        [ruleClass.removeDuplicates() for ruleClass in self.fineRuleClasses];
        [ruleClass.removeDuplicates() for ruleClass in self.coarseRuleClasses];
        
        self.calculateFineFeatureScores();
        self.calculateCoarseFeatureScores();
    
    def doClassification(self):
        
        noOfChunk = 4;
        
        classNames = list(set([question.coarseClass + '|' + question.fineClass for question in self.questions]));
        
        questionClasses = [QuestionClass(className.split('|')[0], className.split('|')[1]) for className in classNames];
        
        for questionClass in questionClasses:
            questionClass.questions = [question for question in self.questions if question.coarseClass == questionClass.coarse and question.fineClass == questionClass.fine];
            questionClass.setLength();
            
        listOfTrainQs = [];
        listOfTestQs = [];
        
        for i in range(0, noOfChunk):
            trainQs = [];
            testQs = [];
            
            for questionClass in questionClasses:
                testQs.extend(questionClass.questions[0:questionClass.length/noOfChunk]);
                ##print(questionClass.coarse+'.'+questionClass.fine+'> '+str(len(questionClass.questions[0:questionClass.length/noOfChunk])));
                questionClass.questions[0:questionClass.length/noOfChunk] = [];
                trainQs.extend([question for question in questionClass.originalQuestions if question not in testQs]);
            ##print('Train Questions: '+str(len(trainQs))+'\tTest Questions: '+str(len(testQs)));
            listOfTrainQs.append(trainQs);
            listOfTestQs.append(testQs);
        
        Precision_Fine_Total = 0.0;
        Recall_Fine_Total = 0.0;
        F_Micro_Fine_Total = 0.0;
        F_Macro_Fine_Total = 0.0;
        
        Precision_Coarse_Total = 0.0;
        Recall_Coarse_Total = 0.0;
        F_Micro_Coarse_Total = 0.0;
        F_Macro_Coarse_Total = 0.0;
        
        Individual_Coarse_Class_Results = [];
        
        for i in range(0,noOfChunk):
            self.testQuestions = listOfTestQs[i];
            self.trainQuestions = listOfTrainQs[i];
            
            self.trainModels();
            
            res = self.doFineClassification();
            Precision_Fine_Total += res[0];
            Recall_Fine_Total += res[1];
            F_Micro_Fine_Total += res[2];
            F_Macro_Fine_Total += res[3];
            print('================================================================');
            print('\n\n>>Fold '+str(i+1) + ' Results:');
            print('\n>Fine Class Results:');
            print('Micro Average Precision: ' + str(res[0]));
            print('Micro Average Recall: ' + str(res[1]));
            print('Micro Average F-Measure: ' + str(res[2]));
            print('Macro Average F-Measure: ' + str(res[3]));
            
            res = self.doCoarseClassification();
            Precision_Coarse_Total += res[0];
            Recall_Coarse_Total += res[1];
            F_Micro_Coarse_Total += res[2];
            F_Macro_Coarse_Total += res[3];
            
            print('\n>Coarse Class Results:');
            print('Micro Average Precision: ' + str(res[0]));
            print('Micro Average Recall: ' + str(res[1]));
            print('Micro Average F-Measure: ' + str(res[2]));
            print('Macro Average F-Measure: ' + str(res[3]));
            
            print('\n>Individual Coarse Class Results');
            for result in res[4]:
                found = False;
                for item in Individual_Coarse_Class_Results:
                    if(item[0] == result[0]):
                        item[1] += result[1];
                        item[2] += result[2];
                        item[3] += result[3];
                        found = True;
                        break;
                
                if(found == False):
                    Individual_Coarse_Class_Results.append(result);
                print(result[0] + '\tPrecision: ' + str(result[1]) + '\tRecall: ' + str(result[2]) + '\tFMeasure: ' + str(result[3]));
        
        print('================================================================');
        
        print('\n\n====Overall Results=====')
        print('\n>Fine Class Results:');
        print('Micro Average Precision: ' + str(Precision_Fine_Total/(noOfChunk*1.0)));
        print('Micro Average Recall: ' + str(Recall_Fine_Total/(noOfChunk*1.0)));
        print('Micro Average F-Measure: ' + str(F_Micro_Fine_Total/(noOfChunk*1.0)));
        print('Macro Average F-Measure: ' + str(F_Macro_Fine_Total/(noOfChunk*1.0)));
        
        print('\n>Coarse Class Results:');
        print('Micro Average Precision: ' + str(Precision_Coarse_Total/(noOfChunk*1.0)));
        print('Micro Average Recall: ' + str(Recall_Coarse_Total/(noOfChunk*1.0)));
        print('Micro Average F-Measure: ' + str(F_Micro_Coarse_Total/(noOfChunk*1.0)));
        print('Macro Average F-Measure: ' + str(F_Macro_Coarse_Total/(noOfChunk*1.0)));
        
        print('\n>Individual Coarse Class Results');
        for result in Individual_Coarse_Class_Results:
            print(result[0] + '\tPrecision: ' + str(result[1]/(noOfChunk*1.0)) + '\tRecall: ' + str(result[2]/(noOfChunk*1.0)) + '\tFMeasure: ' + str(result[3]/(noOfChunk*1.0)));
        
    def doFineClassification(self):

        self.fineFinalCategory = [];
        
        noOfCategoryInTest = len(list(set([question.fineClass for question in self.testQuestions])));
        
        for question in self.testQuestions:
            scores1 = [sum([ruleClass.getWordScore(item[1], 'e') for item in question.questionParts]) * 2 for ruleClass in self.fineRuleClasses];
            scores2 = [sum([ruleClass.getWordScore(item[1], 'c1') for item in question.questionParts]) * 1 for ruleClass in self.fineRuleClasses];
            scores3 = [sum([ruleClass.getWordScore(item[1], 'c2') for item in question.questionParts]) * 1 for ruleClass in self.fineRuleClasses];
            
            totalScores = [scores1[i] + scores2[i] + scores3[i] for i in range(len(scores1))];

            indexOfBestScore = totalScores.index(max(totalScores));

            self.fineFinalCategory.append(self.fineRuleClasses[indexOfBestScore]);
            
            ##print(self.fineRuleClasses[indexOfBestScore].category + '\t'+ str(max(totalScores)));
        
        total_TP = 0.0;
        total_TN = 0.0;
        total_FP = 0.0;
        total_FN = 0.0;
        
        total_FMeasure = 0.0;
        
        for i in range(0, len(self.fineRuleClasses)):
            TP = 0.0;
            TN = 0.0;
            FP = 0.0;
            FN = 0.0;
            
            Precision = 0.0;
            Recall = 0.0;
            FMeasure = 0.0;
            
            for j in range(0, len(self.fineFinalCategory)):          
                if(self.testQuestions[j].fineClass == self.fineRuleClasses[i].category and self.fineFinalCategory[j].category == self.fineRuleClasses[i].category):
                    TP += 1.0;
                    total_TP += 1.0;
                if(self.testQuestions[j].fineClass != self.fineRuleClasses[i].category and self.fineFinalCategory[j].category != self.fineRuleClasses[i].category):
                    TN += 1.0;
                    total_TN += 1.0;
                if(self.testQuestions[j].fineClass != self.fineRuleClasses[i].category and self.fineFinalCategory[j].category == self.fineRuleClasses[i].category):
                    FP += 1.0;
                    total_FP += 1.0;
                if(self.testQuestions[j].fineClass == self.fineRuleClasses[i].category and self.fineFinalCategory[j].category != self.fineRuleClasses[i].category):
                    FN += 1.0;
                    total_FN += 1.0;
            
            if (TP + FP) != 0.0:
                Precision = TP / (TP + FP);
            if (TP + FN) != 0.0:
                Recall = TP / (TP + FN);
            if((Precision + Recall) > 0):
                FMeasure = 2 * Precision * Recall / (Precision + Recall);
            
            total_FMeasure += FMeasure;
            
            ##print('Fine Class: ' + self.fineRuleClasses[i].category + '\tTP: ' + str(TP) + '\tTN: ' + str(TN) + '\tFP: ' + str(FP) + '\tFN: ' + str(FN));
            ##print('Fine Class: ' + self.fineRuleClasses[i].category + '\tPrecision: ' + str(Precision) + '\tRecall: ' + str(Recall)+ '\tFMeasure: ' + str(FMeasure));
            
        Precision = 0.0;
        Recall = 0.0;
        Micro_F = 0.0;
        Macro_F = 0.0;
        
        if(total_TP + total_FP) != 0 : 
            Precision = (total_TP / (total_TP + total_FP));
            
        if(total_TP + total_FN) != 0 : 
            Recall = (total_TP / (total_TP + total_FN));
    
        if(Precision + Recall) != 0:
            Micro_F = 2 * Precision * Recall / (Precision + Recall);

        Macro_F = total_FMeasure / noOfCategoryInTest;
        
        return [Precision, Recall, Micro_F, Macro_F];
    
    def doCoarseClassification(self):
        
        coarseClassResults = [];
        
        self.coarseFinalCategory = [];
        
        noOfCategoryInTest = len(list(set([question.coarseClass for question in self.testQuestions])));
        
        for question in self.testQuestions:
            scores1 = [sum([ruleClass.getWordScore(item[1], 'e') for item in question.questionParts]) * 2 for ruleClass in self.coarseRuleClasses];
            scores2 = [sum([ruleClass.getWordScore(item[1], 'c1') for item in question.questionParts]) * 1 for ruleClass in self.coarseRuleClasses];
            scores3 = [sum([ruleClass.getWordScore(item[1], 'c2') for item in question.questionParts]) * 1 for ruleClass in self.coarseRuleClasses];

            totalScores = [scores1[i] + scores2[i] + scores3[i] for i in range(len(scores1))];

            indexOfBestScore = totalScores.index(max(totalScores));

            self.coarseFinalCategory.append(self.coarseRuleClasses[indexOfBestScore]);
            
            ##print(self.coarseRuleClasses[indexOfBestScore].category + '\t'+ str(max(totalScores)));
        
        total_TP = 0.0;
        total_TN = 0.0;
        total_FP = 0.0;
        total_FN = 0.0;
        
        total_FMeasure = 0.0;
        
        for i in range(0, len(self.coarseRuleClasses)):
            TP = 0.0;
            TN = 0.0;
            FP = 0.0;
            FN = 0.0;
            
            Precision = 0.0;
            Recall = 0.0;
            FMeasure = 0.0;
            
            for j in range(0, len(self.coarseFinalCategory)):          
                if(self.testQuestions[j].coarseClass == self.coarseRuleClasses[i].category and self.coarseFinalCategory[j].category == self.coarseRuleClasses[i].category):
                    TP += 1.0;
                    total_TP += 1.0;
                if(self.testQuestions[j].coarseClass != self.coarseRuleClasses[i].category and self.coarseFinalCategory[j].category != self.coarseRuleClasses[i].category):
                    TN += 1.0;
                    total_TN += 1.0;
                if(self.testQuestions[j].coarseClass != self.coarseRuleClasses[i].category and self.coarseFinalCategory[j].category == self.coarseRuleClasses[i].category):
                    FP += 1.0;
                    total_FP += 1.0;
                if(self.testQuestions[j].coarseClass == self.coarseRuleClasses[i].category and self.coarseFinalCategory[j].category != self.coarseRuleClasses[i].category):
                    FN += 1.0;
                    total_FN += 1.0;
            
            if (TP + FP) != 0.0:
                Precision = TP / (TP + FP);
            if (TP + FN) != 0.0:
                Recall = TP / (TP + FN);
            if((Precision + Recall) > 0):
                FMeasure = 2 * Precision * Recall / (Precision + Recall);
            
            total_FMeasure += FMeasure;
            coarseClassResults.append([self.coarseRuleClasses[i].category, Precision, Recall, FMeasure]);
            ##print('Coarse Class: ' + self.coarseRuleClasses[i].category + '\tTP: ' + str(TP) + '\tTN: ' + str(TN) + '\tFP: ' + str(FP) + '\tFN: ' + str(FN));
            ##print('Coarse Class: ' + self.coarseRuleClasses[i].category + '\tPrecision: ' + str(Precision) + '\tRecall: ' + str(Recall)+ '\tFMeasure: ' + str(FMeasure));
            
        Precision = 0.0;
        Recall = 0.0;
        Micro_F = 0.0;
        Macro_F = 0.0;
        
        if(total_TP + total_FP) != 0 : 
            Precision = (total_TP / (total_TP + total_FP));
            
        if(total_TP + total_FN) != 0 : 
            Recall = (total_TP / (total_TP + total_FN));
    
        if(Precision + Recall) != 0:
            Micro_F = 2 * Precision * Recall / (Precision + Recall);

        Macro_F = total_FMeasure / noOfCategoryInTest;
        
        return [Precision, Recall, Micro_F, Macro_F, coarseClassResults];
