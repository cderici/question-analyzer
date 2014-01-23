

def prepareTenFoldIndexes(questions):
    indexes = []
    
    setLength = len(questions)

    chunkSize = setLength/10

    cIndexStart = 0

    for i in range(1, setLength+1):
        if (i % chunkSize) == 0:
            if ((setLength-i) < chunkSize): # very last chunk
                indexes.append([cIndexStart, setLength])
                break
            else:
                indexes.append([cIndexStart, i])
                cIndexStart = i

    return indexes
