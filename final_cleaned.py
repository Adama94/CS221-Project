import csv
import numpy as np
import random
from printProjectedResults import printProjectedResults, computeFutureProjection
from createCSP import createCSPWithVariables, addConstraints
from BacktrackSearch import BacktrackingSearch
from getSalaries import getSalariesAndPositions, getFutureSalariesAndPositions
from getProjections import getProjections


# specify whether you want to evaluate our algorithm on past data (False)
# or use it to generate optimal lineups for a future week (True)
future = True
# number of optimal lineups to generate
numLineups = 50000
# once lineups are generated, what percentage to submit given their projected scores
percentLineupsUsed = .5
# this variable doesn't actually get used; fix this where it is hardcoded in solve of BacktrackingSearch
salaryCap = 60000
# week to generate lineups for
futureWeek = 13
# year to generate lineups for
futureYear = 2015
# week to evaluate lineups for
evalWeeks = range(1,10)
# year to evaluate lineups for
evalYear = 2015



if future:
	future = True
	csp, scores, projections = createCSPWithVariables(futureWeek, futureYear,future)
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
	for w in evalWeeks:
	    csp, scores, projections = createCSPWithVariables(w, evalYear, future)
	    addConstraints(csp, salaryCap)
	    search = BacktrackingSearch()
	    search.solve(csp,numLineups)
	    win += printProjectedResults(search,scores,w,projections,percentLineupsUsed)
	    total += int(numLineups*percentLineupsUsed)
	print 'Total winners: %s, total lineups entered: %s, win percentage: %s' % (win, total, float(win)/total)









