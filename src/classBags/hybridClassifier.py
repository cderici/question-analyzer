# -*- coding: utf-8 -*-

import codecs, operator





def coarseFinder(question):

    qClass = False

    temporalPhrases = ['ne zaman', 
                       'hangi tarihte', 
                       'tarihi nedir', 
                       'hangi yüzyıl',
                       'kuruluş yılı', 
                       'hangi jeolojik ', 
                       'hangi çağ', 
                       'hangi yıl', 
                       'kaç yılında', 
                       'kaçıncı yüzyıl', 
                       'hangi mevsim', 
                       'hangi tarih',
                       'kuruluş yılı nedir']

    locationPhrases = ['hangi ülke', # 16
                       'hangi il', # 10
                       'nerede', # 15
                       'hangi bölge', # 14
                       'nereye', # 3
                       'hangi kıta', # 5
                       'nere', # 17
                       'bölge hangisidir', # 5
                       'kıta hangisidir', # 3
                       'ülke hangisidir', # 3
                       'bölgesi hangisidir', # 3
                       'kıtası hangisidir', # 2
                       'şehir hangisidir', # 1
                       'ilinin adı', # 2
                       'şehri', # 3
                       ]

    abbreviationPhrases = ['açılımı', 'kısa', 'ne demektir']

    humanPhrases = ['kim ', 'kimdir', 'kimin', 
                    'dili ', 
                    'hangi topluluk', 
                    'hangi uygarlık',
                    'hangi padişah',
                    'hangi kültür',
                    'uygarlık hangisidir']

    numericPhrases = ['kaç', 'kadardır']

    descriptionPhrases = ['ne denir', 
                          'ne ad verilir', 
                          'ne isim verilir',
                          'sonucu nedir', 
                          'sonuç nedir', 
                          'faktör', 
                          'sebebi nedir', 
                          'temel nedeni', 
                          'neye',
                          'neyi verir', 
                          'ne elde edilir']


    t = question.questionText

    """
    TEMPORAL
    """
    if not qClass:
        for tPhrase in temporalPhrases:
            if tPhrase.decode('utf-8') in t:
                qClass = 'TEMPORAL'
                break

    """
    LOCATION
    """
    if not qClass:
        for lPhrase in locationPhrases:
            if lPhrase.decode('utf-8') in t:
                qClass = 'LOCATION'
                break

    """
    ABBREVIATION
    """
    if not qClass:
        for aPhrase in abbreviationPhrases:
            if aPhrase.decode('utf-8') in t:
                qClass = 'ABBREVIATION'
                break

    """
    HUMAN
    """
    if not qClass:
        for hPhrase in humanPhrases:
            if hPhrase.decode('utf-8') in t:
                qClass = 'HUMAN'
                break

    """
    NUMERIC
    """
    if not qClass:
        for nPhrase in numericPhrases:
            if nPhrase.decode('utf-8') in t:
                qClass = 'NUMERIC'
                break

    """
    DESCRIPTION
    """
    if not qClass:
        for dPhrase in descriptionPhrases:
            if dPhrase.decode('utf-8') in t:
                qClass = 'DESCRIPTION'
                break

    if not qClass:
        qClass = 'ENTITY'

    return qClass


def experiment(ourQuestions):

    qstnWords = ['hangi ', 
                 'kaç ', 
                 'Kaç ',
                 ' kim ',
                 'kimin ',
                 'ne zaman',
                 'nereye',
                 'nereden',
                 'nerede ',
                 'yüzde kaç', 
                 'ne denir',
                 'kaçtır',
                 'neresidir',
                 'nedir',
                 'hangisidir',
                 'hangileridir',
                 'verilir',
                 'ne kadardır',
                 'nerelerdir',
                 'neye',
                 'neyin',
                 'ne zamandır', 
                 'ne zamandan',
                 'nerededir',
                 'ne ',
                 'kaçıncı ',
                 'kaça ',
                 'neyle ',
                 'neyi ',
                 'kimdir']

    classCount = {'TEMPORAL':0,
                  'DESCRIPTION':0,
                  'ENTITY':0,
                  'ABBREVIATION':0,
                  'LOCATION':0,
                  'NUMERIC':0,
                  'HUMAN':0}

    classes = classCount.keys()

    with open('qWordClasses', 'w') as f:
        for cls in classes:

            f.write("\n ===== " + cls + " ===== \n")

            # qWordCount keeps :
            # how many of each of question words are used for a particular cls
            qWordCount = {}

            focusWordCount = {}

            for w in qstnWords:
                qWordCount[w] = 0

            for question in ourQuestions:
                c = question.coarseClass

                if cls == c: # this is the class that we are currently interested in
                    qWordMatch = False

                    for w in qstnWords:
                        if w.decode('utf-8') in question.questionText:
                            qWordMatch = True
                            qWordCount[w] += 1

                            for focus in question.trueFocus:
                                foc = focus[1]
                                if foc not in focusWordCount.keys():
                                    focusWordCount[foc] = 1
                                else:
                                    focusWordCount[foc] += 1

                    if not qWordMatch:
                        print(question.questionText)

            sortedCounts = sorted(qWordCount.iteritems(), key=operator.itemgetter(1), reverse=True)

            sortedFcounts = sorted(focusWordCount.iteritems(), key=operator.itemgetter(1), reverse=True)

            for wordCount in sortedCounts:
                if wordCount[1] != 0:
                    f.write(wordCount[0] + " - " + str(wordCount[1]) + "\n")

            f.write("\n\n Most Used Focus Words: \n\n")

            for focusCount in sortedFcounts:
                isQword = False
                fWord = focusCount[0]

                if focusCount[1] < 3:
                    continue

                for qWord in qstnWords:
                    if fWord in qWord.decode('utf-8'):
                        #print("hop")
                        isQword = True
                        break

                if not isQword:
                    f.write(fWord.encode('utf-8') + " - " + str(focusCount[1]) + "\n")

            f.write("\n ========================== \n")
    



def displayCoarseClasses(ourQuestions):

    classes = []

    for question in questions:
        c = question.coarseClass

        if c not in classes:
            classes.append(c)

    print(classes)

