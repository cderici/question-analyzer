# -*- coding: utf-8 -*-

from question import *


def handleNedir(question, qParts):

    qFocus = []
    qMods = []

    SUBJ = QPart.getQPartWithField(qParts, 'depenTag', 'SUBJECT')
    """
    we know that everyone in 'nedir' has subjects
    but nevertheless
    """
    if not SUBJ:
        return False, False
    else:
        
        """ FOCUS EXTRACTION """

        qFocus = [SUBJ]

        """ we find the possessors and classifiers among the children of the subject"""
        subjChildren = question.findChildren(SUBJ)

        possAndClassifierChildren = question.findChildrenDepenTag(SUBJ, 'POSSESSOR')
        possAndClassifierChildren.extend(question.findChildrenDepenTag(SUBJ, 'CLASSIFIER'))

        """ register the focus parts"""
        for cpChild in possAndClassifierChildren:
            qFocus.append(cpChild)
            qFocus.extend(question.tracebackFromFoldTamlama(cpChild))

        """ MOD EXTRACTION """

        """ don't need the modifiers of the subject, it's also a part of the focus"""
        modChildren = []

        """extend the modChildren with the modifier children of the focus parts """
        for focusPart in qFocus:
            modChildren.extend(question.findChildrenDepenTag(focusPart, 'MODIFIER'))

        """ register the final mod parts"""
        for modChild in modChildren:
            qMods.append(modChild)
            qMods.extend(question.tracebackFrom(modChild))
                        
        
        return reversed(qFocus), reversed(qMods)


def handleVerilir(question, qParts):

    qFocus = []
    qMods = []

    SUBJ = QPart.getQPartWithField(qParts, 'depenTag', 'SUBJECT')

    SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')

    
    """ FOCUS EXTRACTION """

    """ 
    Assumptions: 

    -- every 'verilir' question has DATIVE.ADJUNCT

    -- if a DATIVE.ADJUNCT has more than one MODIFIER, the last one is its classifier
    """

    DativeADJ = question.findChildrenDepenTag(SEN, 'DATIVE.ADJUNCT')[0]

    qFocus.extend([SUBJ, DativeADJ])

    dativeModChildren = question.findChildrenDepenTag(DativeADJ, 'MODIFIER')
    dativeModChildren.extend(question.findChildrenDepenTag(DativeADJ, 'POSSESSOR'))
    dativeModChildren.extend(question.findChildrenDepenTag(DativeADJ, 'CLASSIFIER'))
                             

    numOfModChildren = len(dativeModChildren)

    if numOfModChildren > 1:
        """ we take (and remove) the last modifier"""
        focusChild = dativeModChildren.pop(numOfModChildren-1)
        qFocus.append(focusChild)
        qFocus.extend(question.tracebackFrom(focusChild))

    
    """ MOD EXTRACTION """

    if dativeModChildren != []:
        for modChild in dativeModChildren:
            qMods.append(modChild)
            qMods.extend(question.tracebackFrom(modChild))

    return reversed(qFocus), reversed(qMods)


def handleDenir(question, qParts):

    qFocus = []
    qMods = []

    SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')

    return reversed(qFocus), reversed(qMods)


def handleHangiHangileri(question,qParts):
    
    qFocus = []
    qMods = []

    SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')

    subjChildren = question.findChildrenDepenTag(SEN, 'SUBJECT')

    if len(subjChildren)<=0:
        """ this will get the subject which is nearest to the sentence """
        SUBJ = QPart.getQPartWithField(qParts, 'depenTag', 'SUBJECT')
        if not SUBJ:
            return False,False
    else:
        SUBJ = subjChildren[len(subjChildren)-1]


    """ FOCUS EXTRACTION """

    qFocus.append(SUBJ)
    qFocus.extend(question.tracebackFromFoldTamlama(SUBJ))
    
    """ MOD EXTRACTION """    

    modChildren = []
    
    """extend the modChildren with the modifier children of the focus parts """
    for focusPart in qFocus:
        modChildren.extend(question.findChildrenDepenTag(focusPart, 'MODIFIER'))
        
    """ register the final mod parts"""
    for modChild in modChildren:
        qMods.append(modChild)
        qMods.extend(question.tracebackFrom(modChild))

    return reversed(qFocus), reversed(qMods)



def handleBetweenHangi(question, qParts):

    qFocus = []
    qMods = []

    hangiParts = QPart.getQPartWithField(qParts, 'text', 'hangi')

    """ eliminate the hangi parts which are DERIV """
    hangiFiltered=[ part for part in hangiParts if (QPart.getPartField(part, 'depenTag') != 'DERIV')]

    if len(hangiFiltered) != 1:
        raise RuntimeError("Confused with this question: " + question.questionText)

    HANGI = hangiFiltered[0]

    SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')


    """ FOCUS EXTRACTION """

    qFocus = [HANGI]

    hangiParent = question.findParent(HANGI)

    qFocus.append(hangiParent)

    if QPart.getPartField(hangiParent, 'depenTag') == 'CLASSIFIER':
        qFocus.extend(question.traceForwardFromFoldTamlama(hangiParent, False, True, False))
        """                                                        No POSS, yes CLASS, no MODIF"""

    """ MOD EXTRACTION """

    return reversed(qFocus), reversed(qMods)
