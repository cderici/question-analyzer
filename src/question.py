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
            print "Not understood"
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

    def findParent(self, node):
        temp = [part for part in self.questionParts if part[0] == node[6]];

        if(len(temp) == 1):
            return temp[0];
        else:
            return None;

    def findRelations(self, relationText):
        return [part for part in self.questionParts if part[7] == relationText];



    def tracebackFromFoldTamlama(self, part):
        """
        traces back from the given part, and continues only if it sees
        parts with the same depenTag with the given part
        """

        currentChildren = self.findChildren(part)

        if currentChildren == []:
            return [], part

        else:
            tamlamaChild = None
            for child in reversed(currentChildren):
                if (QPart.getPartField(child, 'depenTag') == 'POSSESSOR' 
                    or 
                    QPart.getPartField(child, 'depenTag') == 'CLASSIFIER'):
                    tamlamaChild = child
                    break

            children = []

            lastChild = part

            if tamlamaChild != None:
                children.append(tamlamaChild)
            
                grandTamlamaChildren, lastChild = self.tracebackFromFoldTamlama(tamlamaChild)

                children.extend(grandTamlamaChildren)

            return children, lastChild

    def tracebackFrom(self, part):
        """
        traces back from the given part, and returns a list of parts
        it resembles to moving upwards in visualized tree

        CAUTION: if the given part has more than one children, then
        it chooses to trace the rightmost one (in the visualization)
        TODO: add onlyRight parameter
        """
        currentChildren = self.findChildren(part)

        if currentChildren == []:
            return []
        else:
            lastChildIndex = len(currentChildren)-1

            lastChild = currentChildren[lastChildIndex]

            grandChildren = self.tracebackFrom(lastChild)

            if grandChildren == None:
                print lastChild
                raise RuntimeError("Remember: lists and the functions operating on lists are MUTATIVE!!")


            children = [lastChild]

            children.extend(grandChildren)
            
            return children

