class QPart:

    # a part of the question is a list of 10 elements
    # CAUTION: this class does NOT represent it

    children = [];

    @staticmethod
    def getPartField(qPart, whichField):

        partIndex = 0

        if whichField == 'depenID':
            partIndex = 0
        elif whichField == 'text':
            partIndex = 1
        elif whichField == 'morphRoot':
            partIndex = 2
        elif whichField == 'POStag':
            partIndex = 3
        elif whichField == 'POSDetail':
            partIndex = 4
        elif whichField == 'morphDetail':
            partIndex = 5
        elif whichField == 'rootID':
            partIndex = 6
        elif whichField == 'depenTag':
            partIndex = 7
        else:
            partIndex = -1

        if partIndex == -1:
            print("Not understood")
            return false

        else:
            return qPart[partIndex]

    # getQuestionPart : question symbol -> part
    @staticmethod
    def getQPartWithField(questionParts, whichField, desiredFieldVal):

        # it should start from the end
        for part in reversed(questionParts):
            if desiredFieldVal == QPart.getPartField(part, whichField):
                return part # CAUTION: we are returning the whole part, not just a field

        return False

    @staticmethod
    def getAllPartsWithField(questionParts, whichField, desiredFieldVal):
        desiredParts = []

        for part in reversed(questionParts):
            if desiredFieldVal == QPart.getPartField(part, whichField):

                desiredParts.append(part)

        return desiredParts

    
class Question:
    ##Raw question text
    questionText = '';

    ##Dependency parsed question parts
    questionParts = [];

    ##Root of the parts -- Always (.) period
    root = None;

    ##Focus of the question
    focus = '';

    ##LAT of the question
    lat = '';

    def __init__(self, qText= '', qParts = []):
        self.questionText = qText;
        self.questionParts = qParts;

        self.findRoot();

    def findRoot(self):
        temp = [a for a in self.questionParts if a[1] == '.'];

        if(len(temp) == 1):
            self.root = temp[0];
        else:
            self.root = None;

    # otherThan means that 'find parent of this EXCEPT ...'
    # in case of more than one children:
    # returns a list like [leftmost-item rightmost-item] in visualization
    def findChildren(self, node, otherThan = False):
        return [part for part in self.questionParts if (part[6] == node[0] and ((not otherThan) or part[7] != otherThan[7]))];


    """ find the children of node with depenTags tag"""
    def findChildrenDepenTag(self, node, tag):
        return [part for part in self.questionParts if (part[6] == node[0] and part[7] == tag)];

    def findParent(self, node):
        temp = [part for part in self.questionParts if part[0] == node[6]];

        if(len(temp) == 1):
            return temp;
        else:
            return [];

    def findRelations(self, relationText):
        return [part for part in self.questionParts if part[7] == relationText];


    """
    TRACING STUFF
    """

    def tracebackFromFoldTamlama(self, part, includePOSS=True, includeCLASS=True, includeMODIF=False, includeSEN=False):
        return self.traceFromFoldTamlama('back', part, includePOSS, includeCLASS, includeMODIF, includeSEN)

    def traceForwardFromFoldTamlama(self, part, includePOSS=True, includeCLASS=True, includeMODIF=False, includeSEN=False):
        return self.traceFromFoldTamlama('forward', part, includePOSS, includeCLASS, includeMODIF, includeSEN)

    def tracebackFrom(self, part):
        return self.traceFrom('back', part)

    def traceForwardFrom(self, part):
        return self.traceFrom('forward', part)
    

    def traceFromFoldTamlama(self, direction, part, includePOSS=True, includeCLASS=True, includeMODIF=False, includeSEN=False):
        """
        traces back from the given part, and continues only if it sees
        parts with the depenTag POSSESSOR or CLASSIFIER

        TODO REFACTOR the 'children' 'child', they may be parents
        """
        if direction == 'back':
            currentChildren = self.findChildren(part)
        elif direction == 'forward':
            currentChildren = self.findParent(part)

        if currentChildren == []:
            return []

        else:
            """ TODO: below part can be refactored with findChildrenDepenTag """
            tamlamaChildren = []
            for child in reversed(currentChildren):
                
                childTag = QPart.getPartField(child, 'depenTag')
                
                if includeSEN and childTag == 'SENTENCE':
                    tamlamaChildren.append(child)
                    break

                """ if it is DERIV, go on in any case """
                if childTag == 'DERIV':
                    tamlamaChildren.append(child)
                    continue

                if includePOSS and childTag == 'POSSESSOR':
                    tamlamaChildren.append(child)
                    continue

                elif includeCLASS and childTag == 'CLASSIFIER':
                    tamlamaChildren.append(child)
                    continue

                elif includeMODIF and childTag == 'MODIFIER':
                    tamlamaChildren.append(child)
                    continue


            children = []

            if tamlamaChildren != []:
                for child in tamlamaChildren:
                    childBranch = [child]
                    childBranch.extend(self.traceFromFoldTamlama(direction, child, includePOSS, includeCLASS, includeMODIF, includeSEN))
                    
                    children.extend(childBranch)

            return children

    def traceFrom(self, direction, part):
        """
        traces back from the given part, and returns a list of parts
        it resembles to moving upwards in visualized tree

        Remember: lists and the functions operating on lists are MUTATIVE!!

        TODO: REFACTOR 'children' 'child', they may be parents
        """

        if direction == 'back':
            currentChildren = self.findChildren(part)
        elif direction == 'forward':
            currentChildren = self.findParent(part)


        if currentChildren == []:
            return []
        else:

            children = []

            """ go for every possible child, and go upwards on each of
            them, return the results as a single ordered list (from
            left->right in visualization"""
            for child in reversed(currentChildren):

                partsOnBranch = [child]
                
                partsOnBranch.extend(self.traceFrom(direction, child))
                
                children.extend(partsOnBranch)
            
            return children

