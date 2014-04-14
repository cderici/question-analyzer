import re
import codecs

queryDir = '/home/caner/question-analyzer/src/querier/queries/'

#indexDir = '/home/caner/clean/experiment/indexDir/'
indexDir = '/home/caner/clean/indri-5.0/vikiIndex/'

def buildIndriQuerySingle(qID, question):

    terms = question.questionText.split()

    termsText = " ".join(terms)

    termsText = re.sub("[,]", '', termsText)

    queryText = """ 
<parameters>
<index>""" + indexDir + """</index>

<query>
<number>0</number>
<text>#combine("""

    queryText += termsText + ')'


    queryText += """</text>
</query>
</parameters>
"""

    with codecs.open(queryDir + str(qID), 'w+', 'utf-8') as qFile:
        qFile.write(queryText)

def buildAll(questionSet):
    
    print("BEGIN: buildALL")

    for i in range(1000):
        buildIndriQuerySingle(i+1, questionSet[i])

    print("END: buildALL")
