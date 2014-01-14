from qAnalyzer import *
from maltImporter import MaltImporter
from hmmGlasses import *

ourQuestions = MaltImporter().importMaltOutputs(qFilePath, qParsedFilePath)

analyzer = QuestionAnalysis(ourQuestions[0])

if 'visualize' in sys.argv:
    print("visualizing...")
    QuestionAnalysis.visualizeAll(ourQuestions)
    print("visualization done ....")
# analyzer.showFocusMod()


mass = MassAnalyzer(ourQuestions)

filteredNedir = mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'nedir')

filteredVerilir = mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'verilir')

filteredHangisidir = mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'hangisidir')

filteredHangisidir.extend(mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'hangileridir'))

filteredHangiBetween = mass.filterByPartValue('depenTag', '*', 'text', 'hangi')

filteredDenir = mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'denir')

filteredDenir.extend(mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'denilir'))
filteredDenir.extend(mass.filterByPartValue('depenTag', 'SENTENCE', 'text', 'denilmektedir'))


"""
for q in filteredDenir:
    print "-" + q.questionText
"""

def getAllExpertResults():
    print("\n\n -- nedir -- \n\n")
    
    MassAnalyzer.massShowFocusMod(filteredNedir)

    print("\n\n -- verilir -- \n\n")
    
    MassAnalyzer.massShowFocusMod(filteredVerilir)
    
    print("\n\n -- hangisidir/hangileridir -- \n\n")
    
    MassAnalyzer.massShowFocusMod(filteredHangisidir)
    
    print("\n\n -- .... hangi .... -- \n\n")
    
    MassAnalyzer.massShowFocusMod(filteredHangiBetween)
    
    print("\n\n -- denir -- \n\n")
    
    MassAnalyzer.massShowFocusMod(filteredDenir)

    print(len(filteredNedir) + len(filteredVerilir) + len(filteredHangisidir) + len(filteredHangiBetween) + len(filteredDenir))

if 'experts' in sys.argv:
    getAllExpertResults()

if 'others' in sys.argv:
    print("\n\n ===================== OTHERS ======================== \n\n")

    allExperts = filteredNedir

    allExperts.extend(filteredVerilir)
    allExperts.extend(filteredHangisidir)
    allExperts.extend(filteredHangiBetween)
    allExperts.extend(filteredDenir)

    MassAnalyzer.massShowFocusMod(mass.filterOthers(allExperts))


if 'hmm' in sys.argv:
    print(ourQuestions[0].questionText)
    print(type(ourQuestions[0].focus))
    print(ourQuestions[0].mod)

    print(ourQuestions[0].questionParts)
    print("\n\n")
    print(ourQuestions[0].questionPartsMeta)

    hmmLearn(ourQuestions)
