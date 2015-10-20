from sklearn import linear_model
import numpy as np
import nflgame

# clf = linear_model.LinearRegression(normalize=True)

# week1 = np.array([19, 20, 16])
# week2 = np.array([26, 25, 29])

# clf.fit([week1, week2], [19, 28])

# print clf.coef_

# print np.dot(week1, clf.coef_)
# print np.dot(week2, clf.coef_)

# games = nflgame.games(2015, week=6)
# print games

# players = nflgame.combine_game_stats(games)
# print players.rushing()

# for p in players.rushing().sort('rushing_yds').limit(5):
# 	print type(p)
# 	msg = '%s %d carries for %d yards and %d TDs'
# 	print msg % (p, p.rushing_att, p.rushing_yds, p.rushing_tds)

def computeScore(player, week, year):
	playerObject = nflgame.find(player)
	stats = playerObject[0].stats(year, week)
	score = 0
	score += (stats.passing_yds * .04)
	score += (stats.rushing_yds * .1)
	score += (stats.passing_tds * 4)
	score += (stats.rushing_tds * 6)
	score += (stats.passing_int * -2)
	score += (stats.receiving_yds * .1)
	score += (stats.receiving_tds * 6)
	score += (stats.receiving_rec * .5)
	score += (stats.kickret_tds * 6)
	score += (stats.puntret_tds * 6)
	score += (stats.fumbles * -2)
	score += (stats.fumbles_rec_tds * 6)
	score += (stats.receiving_twopta * 2)
	score += (stats.rushing_twopta * 2)
	score += (stats.passing_twopta * 2)
	print stats.passing_yds
	print stats.passing_tds
	return score

predictions = []
actual = []
for i in range(6):
	score = computeScore("peyton manning", i + 1, 2015)	
	if i == 0:
		predictions.append(0)
	else:
		predictions.append(actual[i - 1])
	actual.append(score)

predictions = predictions[1:]
print actual
actual = actual[1:]


# peyton_manning = [16.8, 16, 17, 17.7, 16.8, 16.6]
# peyton_manning_actual = [5, 20, 18, 8, 6, 9]
# normalizedScores = [abs(peyton_manning[i] - peyton_manning_actual[i]) / peyton_manning_actual[i] for i in range(6)]


error = [abs((predictions[i] - actual[i])) for i in range(5)]
print np.average(error)


