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

    hangiParts = QPart.getAllPartsWithField(qParts, 'text', 'hangi')

    """ eliminate the hangi parts which are DERIV """
    hangiFiltered=[ part for part in hangiParts if (QPart.getPartField(part, 'depenTag') != 'DERIV')]

    if len(hangiFiltered) != 1:
        raise RuntimeError("Confused with this question: " + question.questionText)

    HANGI = hangiFiltered[0]

    SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')


    """ FOCUS EXTRACTION """

    qFocus = [HANGI]

    hangiParent = question.findParent(HANGI)[0]

    if QPart.getPartField(hangiParent, 'depenTag') == 'DERIV':
        while True:
            hangiParent = question.findParent(hangiParent)[0]
            if QPart.getPartField(hangiParent, 'depenTag') != 'DERIV':
                break

    qFocus.append(hangiParent)

    if QPart.getPartField(hangiParent, 'depenTag') == 'CLASSIFIER':
        qFocus.extend(question.traceForwardFromFoldTamlama(hangiParent, True, True, False, True))
        """                                                        No POSS, yes CLASS, no MODIF"""

    """ MOD EXTRACTION """

    """ Tricky...

    there are USUALLY 2 kinds of mods here:
    1) modifier of HANGI --- en çok hangi ...
    2) subjects, adjuncts and other modifiers attached to SENTENCE


    we dump all (2), then traverse upwards from HANGI for (1)
    """

    hangiMods = question.tracebackFromFoldTamlama(HANGI, False, False, True)

    senChildren = question.findChildren(SEN)

    for child in senChildren:
        modCandidates = question.tracebackFrom(child)

        """ excluding the branch ...."""
        isHangiThere = False

        for mod in modCandidates:
            if QPart.getPartField(mod, 'text') == 'hangi':
                isHangiThere = True

        """ .... that has HANGI in it. So: 

        if HANGI is not there, include the branch"""
        if (not isHangiThere):
            modBranch = question.tracebackFrom(child)
            modBranch.reverse()
            modBranch.append(child)

            qMods.extend(modBranch)

    """ Also, if SENTENCE is not included in Focus, include it at the end of qMods"""
    if QPart.getPartField(qFocus[len(qFocus)-1], 'depenTag') != 'SENTENCE':
        qMods.append(SEN)
    
    return qFocus, qMods