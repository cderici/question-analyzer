class QPart:

    children = [];

    @staticmethod
    def getPartPart(qPart, whichPart):

        partIndex = 0

        if whichPart == 'depenID':
            partIndex = 0
        elif whichPart == 'text':
            partIndex = 1
        elif whichPart == 'morphRoot':
            partIndex = 2
        elif whichPart == 'POStag':
            partIndex = 3
        elif whichPart == 'POSDetail':
            partIndex = 4
        elif whichPart == 'morphDetail':
            partIndex = 5
        elif whichPart == 'rootID':
            partIndex = 6
        elif whichPart == 'depenTag':
            partIndex = 7
        else:
            partIndex = -1

        if partIndex == -1:
            print "Not understood"
            return false

        else:
            return qPart[partIndex]
    
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

    def findChildren(self, node):
        return [part for part in self.questionParts if part[6] == node[0]];

    def findParent(self, node):
        temp = [part for part in self.questionParts if part[0] == node[6]];

        if(len(temp) == 1):
            return temp[0];
        else:
            return None;

    def findRelations(self, relationText):
        return [part for part in self.questionParts if part[7] == relationText];
