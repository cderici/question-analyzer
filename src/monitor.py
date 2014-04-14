# -*- coding: utf-8 -*-

import sys

sys.path.append('classBags')
sys.path.append('querier')

from qAnalyzer import *
from maltImporter import MaltImporter
from hmmGlasses import *
from featureBasedClassifier import *

ourQuestions = MaltImporter().importMaltOutputs(qFilePath, qParsedFilePath)

analyzer = QuestionAnalysis(ourQuestions[0])

mass = MassAnalyzer(ourQuestions)

filteredNedir = mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'nedir')
filteredVerilir = mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'verilir')
filteredHangisidir = mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'hangisidir')
filteredHangisidir.extend(mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'hangileridir'))

filteredHangiBetween = mass.filterByPartValue('depenTag', '*', 'text', 'hangi')
filteredNeKadardir = mass.filterByPartValue('depenTag', 'SENTENCE', 'text', "kadardır")
filteredKac = mass.filterByPartValue('depenTag', '*', 'text', 'kaç')
filteredKac.extend(mass.filterByPartValue('depenTag', '*', 'text', 'Kaç'))

filteredDenir = mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'denir')
filteredDenir.extend(mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'denilir'))
filteredDenir.extend(mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'denilmektedir'))

def getAllExpertResults():

    lenQ = len(ourQuestions)
    lenKadar = len(filteredNeKadardir)
    lenNedir = len(filteredNedir)
    lenVerilir = len(filteredVerilir)
    lenHangisidir = len(filteredHangisidir)
    lenHangi = len(filteredHangiBetween)
    lenDenir = len(filteredDenir)
    lenKac = len(filteredKac)
 
    if 'all' in sys.argv or 'kadardır' in sys.argv:
        print("\n\n -- ne kadardır -- \n\n")
        mass.massShowFocusMod(filteredNeKadardir, onlyDistiller=True)
   
        print("ne kadardır # : " + str(lenKadar))

    if 'all' in sys.argv or 'kaç' in sys.argv:
        print("\n\n -- kaç -- \n\n")
        mass.massShowFocusMod(filteredKac, onlyDistiller=True)
   
        print("kaç # : " + str(lenKac))

    if 'all' in sys.argv or 'nedir' in sys.argv:
        print("\n\n -- nedir -- \n\n")
        mass.massShowFocusMod(filteredNedir, onlyDistiller=True)

        print("nedir # : " + str(lenNedir))

    if 'all' in sys.argv or 'verilir' in sys.argv:
        print("\n\n -- verilir -- \n\n")
    
        mass.massShowFocusMod(filteredVerilir, onlyDistiller=True)
    
        print("verilir # : " + str(lenVerilir))

    if 'all' in sys.argv or 'hangisidir' in sys.argv:
        print("\n\n -- hangisidir/hangileridir -- \n\n")
    
        mass.massShowFocusMod(filteredHangisidir, onlyDistiller=True)
    
        print("hangisidir # : " + str(lenHangisidr))

    if 'all' in sys.argv or 'hangi' in sys.argv:
        print("\n\n -- .... hangi .... -- \n\n")
    
        mass.massShowFocusMod(filteredHangiBetween, onlyDistiller=True)
    
        print("hangi # : " + str(lenHangi))

    if 'all' in sys.argv or 'denir' in sys.argv:
        print("\n\n -- denir -- \n\n")
    
        mass.massShowFocusMod(filteredDenir, onlyDistiller=True)

        print("denir # : " + str(lenDenir))

    if 'stats' in sys.argv:

        print("Total Questions # : " + str(lenQ) + "\n")
        print("ne kadardır # : " + str(lenKadar) + " ----> % " + str(int(lenKadar*100.0/lenQ)))
        print("nedir # : " + str(lenNedir) + " ---------> % " + str(int(lenNedir*100.0/lenQ)))
        print("verilir # : " + str(lenVerilir) + " --------> % " + str(int(lenVerilir*100.0/lenQ)))
        print("hangisidir # : " + str(lenHangisidir) + " -----> % " + str(int(lenHangisidir*100.0/lenQ)))
        print("hangi # : " + str(lenHangi) + " ---------> % " + str(int(lenHangi*100.0/lenQ)))
        print("denir # : " + str(lenDenir) + " ----------> % " + str(int(lenDenir*100.0/lenQ)))
        print("kaç # : " + str(lenKac) + " ----------> % " + str(int(lenKac*100.0/lenQ)))

        lenOther = lenQ-(lenNedir + lenVerilir + lenHangisidir + lenHangi + lenDenir + lenKadar)

        print("\nOthers # : " + str(lenOther) + " -------> % " + str(int(lenOther*100.0/lenQ)))

        checkSum = lenKadar+lenNedir+lenVerilir+lenHangisidir+lenHangi+lenDenir+lenKac+lenOther
        print("\nChecksum Status : " + str(checkSum == lenQ))
        if checkSum != lenQ:
            print("Diff : " + str(lenQ-checkSum))

if 'experts' in sys.argv:
    getAllExpertResults()

if 'others' in sys.argv:
    print("\n\n ===================== OTHERS ======================== \n\n")

    allExperts = filteredNedir

    allExperts.extend(filteredVerilir)
    allExperts.extend(filteredHangisidir)
    allExperts.extend(filteredHangiBetween)
    allExperts.extend(filteredDenir)
    allExperts.extend(filteredNeKadardir)

    MassAnalyzer.massShowFocusMod(mass.filterOthers(allExperts))


if 'hmm' in sys.argv:
    """
    print(ourQuestions[0].questionText)
    print(type(ourQuestions[0].focus))
    print(ourQuestions[0].mod)

    print(ourQuestions[0].questionParts)
    print("\n\n")
    print(ourQuestions[0].questionPartsMeta)
    """
    #learnerCheck(ourQuestions)
    glass = Glass(ourQuestions, reverse=True)
    #glass.printAllDebug()
    revGlass = Glass(ourQuestions, reverse=False)
    import pprint
    qIndex = 272
    pp = pprint.PrettyPrinter(indent=4)
    print(ourQuestions[qIndex].questionText)
    print(ourQuestions[qIndex].trueFocus)
    pp.pprint(glass.computeFocusProbs(ourQuestions[qIndex]))
    pp.pprint(revGlass.computeFocusProbs(ourQuestions[qIndex]))
    

if 'class' in sys.argv:
    rule = RuleBasedQuestionClassification(ourQuestions);
    rule.doClassification();

if 'overall' in sys.argv:
    mass.massAnalyze()

if 'visualize' in sys.argv:
    print("visualizing..." + str(len(ourQuestions)) + " questions..")
    QuestionAnalysis.visualizeAll(ourQuestions)
    print("visualization done ....")


if 'query' in sys.argv:

    from queryBuilder import *
    from indriHandler import singleIndriQuery

    print('Query Builder is active..\n')

    if 'build' in sys.argv:

        if 'all' in sys.argv:
            buildAll(ourQuestions)
        elif 'single' in sys.argv:
            print("Built query for question : 1")
            buildIndriQuerySingle(1, ourQuestions[0])
        else:
            raise RuntimeError("Usage: monitor.py query build <all|single>")


    if 'run' in sys.argv:
        if 'single' in sys.argv:
            print("Running query for question : 1")
            docs = singleIndriQuery(1)
            print("Indri relevant docs: ")
            print(docs)
            print("End.")

if 'relatedDoc' in sys.argv:

    from indriHandler import singleIndriQuery
    from indriDocFetch import getDoc

    docs = singleIndriQuery(1)

    print(ourQuestions[0])
    print(docs)

    for dc in docs:
        doc = getDoc(dc)
        print(doc)
        print(type(doc))
        print("Sonbahar" in doc)
