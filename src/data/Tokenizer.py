## Postgresql
import psycopg2;

##Tokenization
import re;
import collections;

##File IO
import codecs;

class QuestionParser:

    questions = [];

    questionsTokenized = [];

    def getQeustionsFromDatabase(self):
        conn = psycopg2.connect("dbname='FatihDB' user='postgres' host='localhost' password='123123'");
        cur = conn.cursor();
        cur.execute("select question from question order by q_id");
        rows = cur.fetchall();

        self.questions = [row[0] for row in rows];

        return self.questions;

    def tokenize(self, text):

        p = re.findall('\(([^()]*)\)', text);

        for p_item in p:
            text = text.replace('(' + p_item + ')', ' ');
        res = re.findall('[0-9,a-z,ğ,ü,ş,ç,ö,ı,â,'',’,A-Z,Ğ,Ü,Ş,Ç,Ö,İ,Â,-]+', text.replace('i̇','i').replace('\'','').replace('’',''));
        
        return [item.strip(',').strip('.').strip('?').strip('!').strip('.').strip(':').strip(';') for item in res]; 
    
    def tokenizeQuestions(self):
        self.questionsTokenized = [self.tokenize(sentence) for sentence in self.questions];
        return self.questionsTokenized;

    def writeToFile(self,path):
        file = ['\n\n'.join(sentence) +'\n\n.\n\n*****\n' for sentence in self.questionsTokenized];

        fileStr = '\n'.join(file);

        w = codecs.open(path,'w','utf-8');
        w.write(u'\ufeff');
        w.write(fileStr);
        w.close();

parser = QuestionParser();
questions = parser.getQeustionsFromDatabase();
tokenizedQuestions = parser.tokenizeQuestions();
a = parser.writeToFile('C:/Users/Kerem/Desktop/input.txt');
