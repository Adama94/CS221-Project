import csv
import numpy as np
import random
from printProjectedResults import printProjectedResults, computeFutureProjection
from createCSP import createCSPWithVariables, addConstraints
from BacktrackSearch import BacktrackingSearch
from CSP import CSP
from getSalaries import getSalariesAndPositions, getFutureSalariesAndPositions
from getProjections import getProjections



future = True
numLineups = 10000
percentLineupsUsed = .5
if future:
	future = True
	csp, scores, projections = createCSPWithVariables(13, 2015,future)
	salaryCap = 60000
	addConstraints(csp, salaryCap)
	search = BacktrackingSearch()
	search.solve(csp,numLineups)
	computedProjections = []

	for assignment in search.allAssignments:
	    projection = computeFutureProjection(assignment,projections)
	    computedProjections.append(projection)
	maxAssignment = search.allAssignments[np.argmax(computedProjections)]
	print maxAssignment, max(computedProjections)
else:
	win = 0
	total = 0
	for w in range(1,10):
	    csp, scores, projections = createCSPWithVariables(w, 2015,future)
	    salaryCap = 60000
	    addConstraints(csp, salaryCap)
	    search = BacktrackingSearch()
	    search.solve(csp,numLineups)
	    win += printProjectedResults(search,scores,w,projections,percentLineupsUsed)
	    total += int(numLineups*percentLineupsUsed)
	print 'Total winners: %s, total lineups entered: %s, win percentage: %s' % (win, total, float(win)/total)









