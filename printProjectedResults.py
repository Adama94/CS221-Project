import numpy as np

def computeFutureProjection(assignment,projections):
    projection = 0
    for position in assignment:        
        player = assignment[position][0]  
        if player in projections:      
            projection += projections[player]
    return projection


def printProjectedResults(search,scores,week,projections,percentLineupsUsed):

    def computeProjection(assignment):
        projection = 0
        for position in assignment:        
            player = assignment[position][0]  
            if player in projections:      
                projection += projections[player]
        return projection

    def computeScore(assignment):
        score = 0
        for position in assignment:        
            player = assignment[position][0]        
            score += scores[player]
        return score

    computedScores = []
    computedProjections = []
    for assignment in search.allAssignments:
        score = computeScore(assignment)
        projection = computeProjection(assignment)
        computedScores.append(score)
        computedProjections.append(projection)

    computedProjections = np.array(computedProjections)
    s = len(computedProjections)
    maxIndices = computedProjections.argsort()[:-int(s*percentLineupsUsed)]

    sumTop = 0
    sumBottom = 0
    for i in range(s):
        if i in maxIndices:
            sumTop += computedScores[i]
        else:
            sumBottom += computedScores[i]
    print 'Week %s' % week
    print "The max score was %f" % max(computedScores)
    print "The min score was %f" % min(computedScores)
    print "The average score was %f" % np.average(computedScores)
    print sumBottom/(s-len(maxIndices)),sumTop/(len(maxIndices))


    numWinners = 0
    for i in maxIndices: 
        if computedScores[i] >= 111.21:
            numWinners += 1            
    print "The number of winners was %d out of %d" % (numWinners, len(maxIndices))
    return numWinners