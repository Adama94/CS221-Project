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
future = True
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
ep_greedy = 0


if __name__ == '__main__':
	if len(sys.argv) <= 2:
		print 'usage (for one test): python final_cleaned.py -t [0 for Past or 1 for Future]'
		print 'usage (for test suite): python final_cleaned.py -f [0 for Past or 1 for Future]'

	elif sys.argv[1] == '-t':
		future = False if sys.argv[2] == '0' else True
		if future:
			csp, scores, projections = createCSPWithVariables(futureWeek, futureYear,future)
			addConstraints(csp, salaryCap)
			search = BacktrackingSearch()
			search.solve(csp,numLineups,ep_greedy)
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
				search.solve(csp,numLineups,ep_greedy)
				win_from_week, total_from_week = printProjectedResults(search,scores,w,projections,percentLineupsUsed)
				win += win_from_week
				total += total_from_week
			print 'Total winners: %s, total lineups entered: %s, win percentage: %s' % (win, total, float(win)/total)

	elif sys.argv[1] == '-f':
		# Full test suite
		future = False if sys.argv[2] == '0' else True
		numIters = 10
		if future:
			csp, scores, projections = createCSPWithVariables(futureWeek, futureYear,future)
			addConstraints(csp, salaryCap)
			search = BacktrackingSearch()

			for i in range(0, 6):
				if i == 6:
					ep_greedy = -1
				else:
					ep_greedy = 1 - i*.2

				average = 0.0
				for j in range(0, numIters):
					search.solve(csp,numLineups,ep_greedy)
					computedProjections = []

					for assignment in search.allAssignments:
					    projection = computeFutureProjection(assignment,projections)
					    computedProjections.append(projection)
					average += float(max(computedProjections)) / float(numIters)

				print 'BacktrackingSearch with epsilon-greedy value of %f' % ep_greedy
				print 'Average: %f\n' % average
		else:
			for i in range(0, 6):
				if i == 6:
					ep_greedy = -1
				else:
					ep_greedy = 1 - i*.2
				average = 0.0
				for j in range(0,numIters):
					win = 0
					total = 0
					for w in evalWeeks:
						csp, scores, projections = createCSPWithVariables(w, evalYear, future)
						addConstraints(csp, salaryCap)
						search = BacktrackingSearch()
						search.solve(csp,numLineups,ep_greedy)
						win_from_week, total_from_week = printProjectedResults(search,scores,w,projections,percentLineupsUsed)
						win += win_from_week
						total += total_from_week
					average += float(win)/(total*float(numIters))
				print 'BacktrackingSearch with epsilon-greedy value of %f' % ep_greedy
				print 'Average win percentage: %f' % average
				print '\n'

