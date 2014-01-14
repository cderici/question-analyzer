from question import *

"""
1 - tree serialize
2 - learn
3 - evaluate
"""

def serializeAtree(parts):

    # serialize parts

    return parts

def learn(questions):

    # focus and mod parts (same index with questions)
    focuses = []
    mods = []
    for question in questions:
        focuses.append(question.extract_FM_Parts('FOC'))
        mods.append(question.extract_FM_Parts('MOD'))

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
