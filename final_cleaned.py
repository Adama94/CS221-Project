import sys
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
# future = True
# number of optimal lineups to generate
numLineups = 10000
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
# epsilon-greedy probability (higher is more deterministic)
# ep_greedy = 1.0
# number of iterations of each test
# numIters = 1
# number of movements needed (for full test suite)
# numEpGreedyTrials = 1

def parseArgs():
	flag = sys.argv[1]
	if flag == '-t':
		ep_greedy = float(sys.argv[4])
		numIters = int(sys.argv[3])
		numEpGreedyTrials = 1
	elif flag == '-f':
		ep_greedy = 1.0
		numIters = int(sys.argv[3])
		numEpGreedyTrials = 7
	future = False if sys.argv[2] == '0' else True
	return ep_greedy, numIters, numEpGreedyTrials, future

def futureProjections(ep_greedy, numIters, numEpGreedyTrials):
	csp, scores, projections = createCSPWithVariables(futureWeek, futureYear,future)
	addConstraints(csp, salaryCap)
	search = BacktrackingSearch()

	for i in range(0, numEpGreedyTrials):
		if i > 0:
			ep_greedy -= .2

		print 'BacktrackingSearch with epsilon-greedy value of %f' % ep_greedy
		for k in range(1,4):
			average = 0.0
			for j in range(0, numIters):
				search.solve(csp,numLineups,ep_greedy,k)
				computedProjections = []

				for assignment in search.allAssignments:
				    projection = computeFutureProjection(assignment,projections)
				    computedProjections.append(projection)
				average += float(max(computedProjections)) / float(numIters)

			print 'Average Max Projection with comparison index %d: %f' % (k, average)
		print '\n'

def pastPerformance(ep_greedy, numIters, numEpGreedyTrials):
	for i in range(0, numEpGreedyTrials):
		if i > 0:
			ep_greedy -= .2

		print 'BacktrackingSearch with epsilon-greedy value of %f' % ep_greedy
		for k in range(1, 4):
			average = 0.0
			for j in range(0,numIters):
				win = 0
				total = 0
				for w in evalWeeks:
					csp, scores, projections = createCSPWithVariables(w, evalYear, future)
					addConstraints(csp, salaryCap)
					search = BacktrackingSearch()
					search.solve(csp,numLineups,ep_greedy,k)
					win_from_week, total_from_week = printProjectedResults(search,scores,w,projections,percentLineupsUsed)
					win += win_from_week
					total += total_from_week
				average += float(win)/(total*float(numIters))
			print 'Average win percentage with comparison index %d: %f' % (k, average)
		print '\n'

if __name__ == '__main__':
	if len(sys.argv) <= 3:
		print 'usage (for one test): python final_cleaned.py -t [0 for Past or 1 for Future] [1 to 100 for number of iterations of the each test] [float between 0 and 1 for epsilon-greedy prob (higher is more deterministic]'
		print 'usage (for test suite): python final_cleaned.py -f [0 for Past or 1 for Future] [1 to 100 for number of iterations of the each test]'

	else:
		ep_greedy, numIters, numEpGreedyTrials, future = parseArgs()

		if future:
			futureProjections(ep_greedy, numIters, numEpGreedyTrials)
		else:
			pastPerformance(ep_greedy, numIters, numEpGreedyTrials)
			

