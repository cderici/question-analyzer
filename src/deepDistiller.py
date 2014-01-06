# -*- coding: utf-8 -*-

import re
from question import *

nedirFC = 0
verilirFC = 0
denirFC = 0
hangisidirFC = 0
hangiBtwFC = 0

nedirMC = 0
verilirMC = 0
denirMC = 0
hangisidirMC = 0
hangiBtwMC = 0

def nedirExpert(question, qParts, trainMode = False, rFocus = [], rMods = []):

    qFocus = []
    qMods = []

    SUBJ = QPart.getQPartWithField(qParts, 'depenTag', 'SUBJECT')
    """
    we know that everyone in 'nedir' has subjects
    but nevertheless
    """
    if not SUBJ:
        return False, False, nedirFC, nedirMC
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
        for modChild in reversed(modChildren):
            qMods.append(modChild)
            qMods.extend(question.tracebackFrom(modChild))
            
        """special hack for parts like 'Türkiyeden'"""
        subjects = QPart.getAllPartsWithField(qParts, 'depenTag', 'SUBJECT')
        if len(subjects) > 1:
            for subj in subjects:
                subjText = QPart.getPartField(subj, 'text')

                compl = re.compile(ur"Türkiye", re.UNICODE)

                if compl.search(subjText) != None:
                    qMods.append(subj)

        return reversed(qFocus), reversed(qMods), nedirFC, nedirMC


def verilirExpert(question, qParts, trainMode = False, rFocus = [], rMods = []):

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

    if DativeADJ == []:
        return False, False, verilirFC, verilirMC

    qFocus.extend([SUBJ, DativeADJ])

    focusChildren = question.findChildrenDepenTag(DativeADJ, 'POSSESSOR')
    focusChildren.extend(question.findChildrenDepenTag(DativeADJ, 'CLASSIFIER'))

    dativeModChildren = question.findChildrenDepenTag(DativeADJ, 'MODIFIER')
    dativeModChildren.extend(question.findChildrenDepenTag(DativeADJ, 'POSSESSOR'))
    dativeModChildren.extend(question.findChildrenDepenTag(DativeADJ, 'CLASSIFIER'))
                             
    numFocusChildren = len(focusChildren)

    numOfModChildren = len(dativeModChildren)



    if numOfModChildren > 1:
        """ we take (and remove) the last modifier"""
        #focusChild = focusChildren.pop(numFocusChildren-1)
        
        focusChild = dativeModChildren[numOfModChildren-1]

        childTag = QPart.getPartField(focusChild, 'depenTag')

        if childTag != 'MODIFIER':
            focusChild = dativeModChildren.pop(numOfModChildren-1)
            qFocus.append(focusChild)
            qFocus.extend(question.tracebackFrom(focusChild))
        
    elif numOfModChildren == 1:
        childTag = QPart.getPartField(dativeModChildren[0], 'depenTag')
        if childTag == 'POSSESSOR' or childTag == 'CLASSIFIER':
            fChild = dativeModChildren.pop(0)
            qFocus.append(fChild)
            qFocus.extend(question.tracebackFromFoldTamlama(fChild, includePOSS=True, includeCLASS=True))
            
            modCandidates = question.tracebackFrom(fChild)
            for candy in modCandidates:
                if candy not in qFocus:
                    qMods.append(candy)
                    qMods.extend(question.tracebackFrom(candy))
    """ MOD EXTRACTION """

    if dativeModChildren != []:
        for modChild in reversed(dativeModChildren):
            qMods.append(modChild)
            qMods.extend(question.tracebackFrom(modChild))

    return reversed(qFocus), reversed(qMods), verilirFC, verilirMC


def denirExpert(question, qParts, trainMode = False, rFocus = [], rMods = []):

    qFocus = []
    qMods = []

    SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')

    """ FOCUS EXTRACTION """

    """ FALSE Assumption: every 'denir' has a dative.adjunct """

    DativeADJchildren = question.findChildrenDepenTag(SEN, 'DATIVE.ADJUNCT')

    if DativeADJchildren == []:
        return False, False, denirFC, denirMC

    """ Assumption: if it has more than one dative.adjunct, the last one (the closests to the SENTENCE) is most likely the correct one"""

    DativeADJ = DativeADJchildren[len(DativeADJchildren)-1]

    qFocus = [SEN, DativeADJ]
    qFocus.extend(question.tracebackFromFoldTamlama(DativeADJ, True, True, False, False, True))

    """ MOD EXTRACTION """

    """ dump all children of focus parts """

    for fPart in qFocus:
        children = question.findChildren(fPart)
        
        for child in children:

            childPartsDummy = question.tracebackFrom(child)
            childParts = question.tracebackFrom(child)

            for cPart in childPartsDummy:
                if (cPart in qFocus) or (cPart in qMods):
                    childParts.remove(cPart)

            qMods.extend(childParts)

    return reversed(qFocus), reversed(qMods), denirFC, denirMC


def hangisidirExpert(question, qParts, trainMode = False, rFocus = [], rMods = []):
    
    qFocus = []
    qMods = []

    SEN = QPart.getQPartWithField(qParts, 'depenTag', 'SENTENCE')

    subjChildren = question.findChildrenDepenTag(SEN, 'SUBJECT')

    if len(subjChildren)<=0:
        """ this will get the subject which is nearest to the sentence """
        SUBJ = QPart.getQPartWithField(qParts, 'depenTag', 'SUBJECT')
        if not SUBJ:
            return False, False, hangisidirFC, hangisidirMC
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
    for modChild in reversed(modChildren):
        qMods.append(modChild)
        qMods.extend(question.tracebackFrom(modChild))

        
    """special hack for parts like 'Türkiyeden'"""
    subjects = QPart.getAllPartsWithField(qParts, 'depenTag', 'SUBJECT')
    if len(subjects) > 1:
        for subj in subjects:
            subjText = QPart.getPartField(subj, 'text')

            compl = re.compile(ur"Türkiye", re.UNICODE)

            if compl.search(subjText) != None:
                qMods.append(subj)


    return reversed(qFocus), reversed(qMods), hangisidirFC, hangisidirMC



def hangiBtwExpert(question, qParts, trainMode = False, rFocus = [], rMods = []):

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

    """ BEWARE: this part is highly mutative! """

    """ we first concentrate on hangiParent """
    hangiParent = question.findParent(HANGI)[0]

    """ UPWARDS TOWARDS SENTENCE """
    if QPart.getPartField(hangiParent, 'depenTag') == 'DERIV':
        while True:
            hangiParent = question.findParent(hangiParent)[0]
            if QPart.getPartField(hangiParent, 'depenTag') != 'DERIV':
                break

    if len(question.findChildren(hangiParent)) > 1:
        allChildren = question.tracebackFromFoldTamlama(hangiParent, True, True, True, False)
        """ eliminate child parts that are in focus"""
        for child in allChildren:
            if child in qFocus:
                allChildren.remove(child)
                continue

        qFocus.extend(allChildren)

    qFocus.append(hangiParent)

    if QPart.getPartField(hangiParent, 'depenTag') == 'CLASSIFIER':
        qFocus.extend(question.traceForwardFromFoldTamlama(hangiParent, True, True, False, True))
    else:
        qFocus.extend(question.traceForwardFromFoldTamlama(hangiParent, False, False, True, False))

    

   
    """ MOD EXTRACTION """

    """ Tricky...

    there are USUALLY 2 kinds of mods here:
    1) modifier of HANGI --- en çok hangi ...
    2) subjects, adjuncts and other modifiers attached to SENTENCE

    TODO 3) How about modifiers of focus parts other than HANGI -> ... hangi nadide ilin ....

    we dump all (2), then traverse upwards from HANGI for (1), then (3)
    """
    senChildrenDummy = question.findChildren(SEN)
    senChildren = question.findChildren(SEN)

    for child in senChildrenDummy:
        if QPart.getPartField(child, 'depenTag') == 'DERIV':
            senChildren.remove(child)
            senChildren.extend(question.findChildren(child))
            
    for child in senChildren:
        if child not in qFocus:
            modCandidates = question.tracebackFrom(child)
            
            """ excluding the parts before HANGI, in branch ...."""
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

    hangiMods = question.tracebackFromFoldTamlama(HANGI, False, False, True)

    qMods.extend(reversed(hangiMods))

    """ Also, if SENTENCE is not included in Focus, include it at the end of qMods"""
    if QPart.getPartField(qFocus[len(qFocus)-1], 'depenTag') != 'SENTENCE':
        qMods.append(SEN)
    
    return qFocus, qMods, hangiBtwFC, hangiBtwMC
