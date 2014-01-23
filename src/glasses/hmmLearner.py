from question import *

import copy

"""
1 - tree serialize
2 - learn
3 - evaluate
"""

def serializeDepTree(parts, reverse=True):

    # serialize parts
    prt = []
    for part in parts:
        pTag = QPart.getPartField(part, 'depenTag')
        pText = QPart.getPartField(part, 'text')

        if pTag != 'DERIV' and pText != '.':
            prt.append(part)

    if reverse:
        prt.reverse()
    return prt

def hmmLearn(questions, reverse=True):

    wordCounts = {}

    # total: total tag count
    # focus: number of times this tag is being seen as focus
    # mod: see focus
    tagCounts = {'SENTENCE':{'total':0,'focus':0, 'mod':0, 'non':0},
                 'SUBJECT':{'total':0,'focus':0, 'mod':0, 'non':0},
                 'MODIFIER':{'total':0,'focus':0, 'mod':0, 'non':0},
                 'CLASSIFIER':{'total':0,'focus':0, 'mod':0, 'non':0},
                 'POSSESSOR':{'total':0,'focus':0, 'mod':0, 'non':0},
                 'DETERMINER':{'total':0,'focus':0, 'mod':0, 'non':0},
                 'LOCATIVE.ADJUNCT':{'total':0,'focus':0, 'mod':0, 'non':0},
                 'DATIVE.ADJUNCT':{'total':0,'focus':0, 'mod':0, 'non':0},
                 'OBJECT':{'total':0,'focus':0, 'mod':0, 'non':0},
                 #             'DERIV':{'total':0,'focus':0, 'mod':0},
                 'ABLATIVE.ADJUNCT':{'total':0,'focus':0, 'mod':0, 'non':0},
                 'INSTRUMENTAL.ADJUNCT':{'total':0,'focus':0, 'mod':0, 'non':0},
                 'COORDINATION':{'total':0,'focus':0, 'mod':0, 'non':0},
#                 'ROOT':{'total':0,'focus':0, 'mod':0, 'non':0},
                 'VOCATIVE':{'total':0,'focus':0, 'mod':0, 'non':0},
                 'APPOSITION':{'total':0,'focus':0, 'mod':0, 'non':0},
                 'QUESTION.PARTICLE':{'total':0,'focus':0, 'mod':0, 'non':0},
                 'INTENSIFIER':{'total':0,'focus':0, 'mod':0, 'non':0},
                 'S.MODIFIER':{'total':0,'focus':0, 'mod':0, 'non':0},
#                 'notconnected':{'total':0,'focus':0, 'mod':0, 'non':0}
                 }



    FmnCounts = {'FOC':0,
                 #'MOD':0,
                 'NON':0
                 }

    initFmnCounts = copy.deepcopy(FmnCounts)

    dummy = FmnCounts.copy()

    for k in FmnCounts.keys():
        FmnCounts[k] = dummy.copy()

    allParts = []
    #totalPartCount = 0
    for question in questions:

        serialParts = serializeDepTree(question.questionParts, reverse)
        #totalPartCount += len(serialParts)

        for part in serialParts:
            tag = QPart.getPartField(part, 'depenTag')
            
            word = extractWord(question, part)

            if not wordCounts.has_key(word):
                wordCounts[word] = {'total':0, 'focus':0, 'mod':0, 'non':0}

            if part in question.trueFocus:
                tagCounts[tag]['focus'] += 1
                wordCounts[word]['focus'] += 1
            elif part in question.trueMod:
                tagCounts[tag]['non'] += 1
                wordCounts[word]['non'] += 1
            else:                
                tagCounts[tag]['non'] += 1
                wordCounts[word]['non'] +=1 

            tagCounts[tag]['total'] += 1
            wordCounts[word]['total'] += 1

        """ Computing initial counts """
        initPart = serialParts[0]

        if initPart in question.trueFocus:
            initFmnCounts['FOC'] += 1
        elif initPart in question.trueMod:
            initFmnCounts['NON'] += 1
        else:
            initFmnCounts['NON'] += 1

        """ Computing bigram counts P({Foc Mod Non | Foc Mod Non) """
        for i in range(0, len(serialParts)-1):

            part = serialParts[i]
            partProp = ''
            if part in question.trueFocus:
                partProp = 'FOC'
            elif part in question.trueMod:
                partProp = 'NON'
            else:
                partProp = 'NON'

            nextPart = serialParts[i+1]
            nPartProp = ''
            if nextPart in question.trueFocus:
                nPartProp = 'FOC'
            elif nextPart in question.trueMod:
                nPartProp = 'NON'
            else:
                nPartProp = 'NON'

            FmnCounts[partProp][nPartProp] += 1
        

    return tagCounts, initFmnCounts, FmnCounts, wordCounts


def learnerCheck(questions):

    import pprint
    pp = pprint.PrettyPrinter(indent=4)

    print("\n\n ===== Manual Check: HMM-Glasses Learning ====== \n\n")

    print("Given " + str(len(questions)) + " questions...")
    tagCounts, initFmnCounts, FmnCounts, wordCounts = hmmLearn(questions)

    print("\nTotal Counts:\n\n")
    #print(tagCounts)
    pp.pprint(tagCounts)
    
    print("\nInit Counts:\n\n")
    #print(initTagCounts)
    pp.pprint(initFmnCounts)

    print("\nFMN Counts:\n\n")
    #print(FmnCounts)
    pp.pprint(FmnCounts)

    print("\nWords Counts:\n\n")
    pp.pprint(wordCounts)
    print("VOCABULARY SIZE (V) : " + str(len(wordCounts)))
    print("_ COUNT : ")
    print(wordCounts.get('_'))
    """
    print("Total Part Count : " + str(totalPartCount))
    checkSum = 0
    checkSum += sum(FmnCounts['FOC'].values())
    checkSum += sum(FmnCounts['MOD'].values())
    checkSum += sum(FmnCounts['NON'].values())
    
    print("Checksum : " + str((totalPartCount-490) == checkSum))
    """

def extractWord(question, part):
    specialWords = ['nedir', 'verilir', 'hangisidir', 'hangileridir', 'denir', 'denilir', 'denilmektedir', 'nereleridir']
    word = QPart.getPartField(part, 'text')
    if not word in specialWords:
        word = QPart.getPartField(part, 'morphRoot')
        prt = part
        while word == "_":
            derivChild = question.findChildrenDepenTag(prt, 'DERIV')[0]
            word = QPart.getPartField(derivChild, 'morphRoot')
            prt = derivChild

    return word
