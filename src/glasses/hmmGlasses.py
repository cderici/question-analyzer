from question import *

import copy

"""
1 - tree serialize
2 - learn
3 - evaluate
"""

# total: total tag count
# focus: number of times this tag is being seen as focus
# mod: see focus
tagCounts = {'SENTENCE':{'total':0,'focus':0, 'mod':0},
             'SUBJECT':{'total':0,'focus':0, 'mod':0},
             'MODIFIER':{'total':0,'focus':0, 'mod':0},
             'CLASSIFIER':{'total':0,'focus':0, 'mod':0},
             'POSSESSOR':{'total':0,'focus':0, 'mod':0},
             'DETERMINER':{'total':0,'focus':0, 'mod':0},
             'LOCATIVE.ADJUNCT':{'total':0,'focus':0, 'mod':0},
             'DATIVE.ADJUNCT':{'total':0,'focus':0, 'mod':0},
             'OBJECT':{'total':0,'focus':0, 'mod':0},
#             'DERIV':{'total':0,'focus':0, 'mod':0},
             'ABLATIVE.ADJUNCT':{'total':0,'focus':0, 'mod':0},
             'INSTRUMENTAL.ADJUNCT':{'total':0,'focus':0, 'mod':0},
             'COORDINATION':{'total':0,'focus':0, 'mod':0},
             'ROOT':{'total':0,'focus':0, 'mod':0},
             'VOCATIVE':{'total':0,'focus':0, 'mod':0},
             'APPOSITION':{'total':0,'focus':0, 'mod':0},
             'QUESTION.PARTICLE':{'total':0,'focus':0, 'mod':0},
             'INTENSIFIER':{'total':0,'focus':0, 'mod':0},
             'S.MODIFIER':{'total':0,'focus':0, 'mod':0},
             'notconnected':{'total':0,'focus':0, 'mod':0}
             }

initTagCounts = copy.deepcopy(tagCounts)

FmnCounts = {'FOC':0,
             'MOD':0,
             'NON':0
             }

dummy = FmnCounts.copy()

for k in FmnCounts.keys():
    FmnCounts[k] = dummy.copy()

def serializeDepTree(parts):

    # serialize parts
    prt = []
    for part in parts:
        pTag = QPart.getPartField(part, 'depenTag')
        pText = QPart.getPartField(part, 'text')

        if pTag != 'DERIV' and pText != '.':
            prt.append(part)

    prt.reverse()
    return prt

def hmmLearn(questions):

    # focus and mod parts (same index with questions)
    focuses = []
    mods = []

    allParts = []
    totalPartCount = 0
    for question in questions:

        serialParts = serializeDepTree(question.questionParts)
        totalPartCount += len(serialParts)

        for fPart in question.trueFocus:
            tag = QPart.getPartField(fPart, 'depenTag')
            tagCounts[tag]['focus'] += 1

        for mPart in question.trueMod:
            tag = QPart.getPartField(mPart, 'depenTag')
            try:
                tagCounts[tag]['mod'] += 1
            except:
                raise RuntimeError(question.questionText)

        for part in serialParts:
            tag = QPart.getPartField(part, 'depenTag')
            tagCounts[tag]['total'] += 1




        """ Computing initial counts """
        initPart = serialParts[0]

        ipTag = QPart.getPartField(initPart, 'depenTag')
        
        initTagCounts[ipTag]['total'] += 1
        
        if initPart in question.trueFocus:
            initTagCounts[ipTag]['focus'] += 1
        elif initPart in question.trueMod:
            initTagCounts[ipTag]['mod'] += 1
        

        """ Computing bigram counts P({Foc Mod Non | Foc Mod Non) """
        for i in range(0, len(serialParts)-1):

            part = serialParts[i]
            partProp = ''
            if part in question.trueFocus:
                partProp = 'FOC'
            elif part in question.trueMod:
                partProp = 'MOD'
            else:
                partProp = 'NON'

            nextPart = serialParts[i+1]
            nPartProp = ''
            if nextPart in question.trueFocus:
                nPartProp = 'FOC'
            elif nextPart in question.trueMod:
                nPartProp = 'MOD'
            else:
                nPartProp = 'NON'

            FmnCounts[partProp][nPartProp] += 1
        
    print("Total Counts:\n\n")
    print(tagCounts)
    
    print("Init Counts:\n\n")
    print(initTagCounts)

    print("FMN Counts:\n\n")
    print(FmnCounts)
    
    print("Total Part Count : " + str(totalPartCount))
    checkSum = 0
    checkSum += sum(FmnCounts['FOC'].values())
    checkSum += sum(FmnCounts['MOD'].values())
    checkSum += sum(FmnCounts['NON'].values())
    
    print("Checksum : " + str((totalPartCount-490) == checkSum))
    
    
    """ check exists, if not learn and store
    P(FOC|tag) 
    P(MOD|tag) 
    P(NON|tag)
    """

     

    """ check exists, if not learn and store
    P(FOC|FOC) P(FOC|MOD) P(FOC|NON)
    P(MOD|FOC) P(MOD|MOD) P(MOD|NON)
    P(NON|FOC) P(NON|MOD) P(NON|NON)
    """
