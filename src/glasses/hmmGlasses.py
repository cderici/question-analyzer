# -*- coding: utf-8 -*-

from question import *
from hmmLearner import *

import copy
import pprint

class Glass:

    reverse = True
    # probs. that a depen tag being a FOC, MOD or NON
    tagProbs = None

    wordProbs = None

    # initial probs. of tags being FOC, MOD or NON
    initFmnProbs = None

    # transition probs btw FOC, MOD and NON
    transitionProbs = None

    def __init__(self, questions, reverse=True):
        tagCounts, initFmnCounts, FmnCounts, wordCounts = hmmLearn(questions, reverse)
        self.reverse = reverse

        self.tagProbs = copy.deepcopy(tagCounts)
        self.wordProbs = copy.deepcopy(wordCounts)
        self.initFmnProbs = copy.deepcopy(initFmnCounts)
        self.transitionProbs = copy.deepcopy(FmnCounts)

        # computing initial probabilities from counts
        for fmn in initFmnCounts.keys():
            self.initFmnProbs[fmn] = initFmnCounts[fmn]/(len(questions)*1.0)

        # computing tagProbs from tagCounts
        for tag in tagCounts.keys():
            for fmn in tagCounts[tag].keys():
                self.tagProbs[tag][fmn] = tagCounts[tag][fmn]/(tagCounts[tag]['total']*1.0)

        # computing tagProbs from tagCounts
        for word in wordCounts.keys():
            for fmn in wordCounts[word].keys():
                self.wordProbs[word][fmn] = wordCounts[word][fmn]/(wordCounts[word]['total']*1.0)

        # computing transition probabilities
        for fmn in FmnCounts.keys():
            total = sum(FmnCounts[fmn].values())
            for fmn2 in FmnCounts[fmn].keys():
                self.transitionProbs[fmn][fmn2] = FmnCounts[fmn][fmn2]/(total*1.0)

    @staticmethod
    def hmmResultsToParts(hmmTriplets):
        parts = []
        for triplet in hmmTriplets:
            parts.append(triplet[2])

        return parts

    def printAllDebug(self):
        pp = pprint.PrettyPrinter(indent = 4)

        print("\n\n Tag Probs \n\n")
        pp.pprint(self.tagProbs)

        print("\n\n Init Fmn Probs \n\n")
        pp.pprint(self.initFmnProbs)

        print("\n\n Transition Probs \n\n")
        pp.pprint(self.transitionProbs)

        print("\n\n Word Probs \n\n")
        pp.pprint(self.wordProbs)
        print("\n hangi \n")
        print(self.wordProbs['hangi'])
        print("\n nedir \n")
        print(self.wordProbs['nedir'])
        print("\n denir \n")
        print(self.wordProbs['denir'])
        print("\n ne \n")
        print(self.wordProbs['ne'])
        print("\n verilir \n")
        print(self.wordProbs['verilir'])
        print("\n ka\xc3\xa7 \n")
        print(self.wordProbs['kaç'.decode('utf-8')])
        print("\n kim \n")
        print(self.wordProbs['kim'])
        print("\n kürede \n")
        print(self.wordProbs['küre'.decode('utf-8')])
        
    def computeFocusProbs(self, newQuestion):
        serialParts = serializeDepTree(newQuestion.questionParts, self.reverse)

        # HACK
        self.tagProbs = self.wordProbs

        mostProbableSequence = []
        
        for partIndex in range(0, len(serialParts)):
            part = serialParts[partIndex]
            #tag = QPart.getPartField(part, 'depenTag')
            tag = extractWord(newQuestion, part)
            
            if partIndex == 0: # start?
                focProb = self.initFmnProbs['FOC']*self.tagProbs[tag]['focus']
                modProb = self.initFmnProbs['MOD']*self.tagProbs[tag]['mod']
                nonProb = self.initFmnProbs['NON']*self.tagProbs[tag]['non']

                #print("\nS FOCPROB: " + str(focProb))
                #print("S MODPROB: " + str(modProb))
                #print("S NONPROB: " + str(nonProb))
                highestState = max(focProb, modProb, nonProb)

                if highestState == focProb:
                    mostProbableSequence.append(['FOC',focProb, part])
                elif highestState == modProb:
                    mostProbableSequence.append(['MOD',modProb, part])
                elif highestState == nonProb:
                    mostProbableSequence.append(['NON',nonProb, part])
                else:
                    raise RuntimeError("something is horribly wrong in the initial stage")

            else:
                # beware, nasty hack ahead
                prevState = mostProbableSequence[partIndex-1][0]
                prevProb = mostProbableSequence[partIndex-1][1]
                
                currentFocusProb = prevProb*self.tagProbs[tag]['focus']*self.transitionProbs[prevState]['FOC']

                #print("\nFOCPROB: " + str(currentFocusProb))
                currentModProb = prevProb*self.tagProbs[tag]['mod']*self.transitionProbs[prevState]['MOD']
                #print("MODPROB: " + str(currentModProb))
                currentNonProb = prevProb*self.tagProbs[tag]['non']*self.transitionProbs[prevState]['NON']
                #print("NONPROB: " + str(currentNonProb))
                highestState = max(currentFocusProb, currentModProb, currentNonProb)

                if highestState == currentFocusProb:
                    currentState = 'FOC'
                    currentProb = currentFocusProb
                elif highestState == currentModProb:
                    currentState = 'MOD'
                    currentProb = currentModProb
                elif highestState == currentNonProb:
                    currentState = 'NON'
                    currentProb = currentNonProb
                else:
                    raise RuntimeError("something is horribly wrong in middle stages")
                
                mostProbableSequence.append([currentState, currentProb, part])

        if self.reverse:
            mostProbableSequence.reverse()
        return mostProbableSequence
