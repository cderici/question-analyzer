from question import *

"""
1 - tree serialize
2 - learn
3 - evaluate
"""

def serializeAtree(parts):

    # serialize parts

    return parts

def hmmLearn(questions):

    # focus and mod parts (same index with questions)
    focuses = []
    mods = []

    allParts = []


    totalTagCounts = {'SENTENCE':0,
                      'SUBJECT':0,
                      'MODIFIER':0,
                      'CLASSIFIER':0,
                      'POSSESSOR':0,
                      'DETERMINER':0,
                      'LOCATIVE.ADJUNCT':0,
                      'DATIVE.ADJUNCT':0,
                      'OBJECT':0,
                      'DERIV':0,
                      'ABLATIVE.ADJUNCT':0,
                      'INSTRUMENTAL.ADJUNCT':0,
                      'COORDINATION':0,
                      'ROOT':0,
                      'VOCATIVE':0,
                      'APPOSITION':0,
                      'QUESTION.PARTICLE':0,
                      'INTENSIFIER':0,
                      'S.MODIFIER':0,
                      'notconnected':0}

    focusTagCounts = totalTagCounts.copy()
    modTagCounts = totalTagCounts.copy()

    for question in questions:
        for fPart in question.trueFocus:
            tag = QPart.getPartField(fPart, 'depenTag')
            focusTagCounts[tag] = focusTagCounts[tag] + 1

        for mPart in question.trueMod:
            tag = QPart.getPartField(mPart, 'depenTag')
            modTagCounts[tag] = modTagCounts[tag] + 1

        for part in question.questionParts:
            tag = QPart.getPartField(part, 'depenTag')
            totalTagCounts[tag] = totalTagCounts[tag] + 1


    print("Total Counts:\n\n")
    print(totalTagCounts)
    print(sum(totalTagCounts.values()))
    
    print("Focus Tag Counts:\n\n")
    print(focusTagCounts)

    
    print("Mod Tag Counts:\n\n")
    print(modTagCounts)

    


    

    
    
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
