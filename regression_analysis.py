import math
import numpy as np
import statsmodels.api as sm
import scipy
import csv
import urllib
import datetime
import os
import collections
import operator
from collections import defaultdict
import random


def asianHandicap(probabilityMatrix):
	asianHandicap = {}
	homeProb = 0
	drawProb = 0
	awayProb = 0
	homeProbExactlyOne = 0
	homeProbExactlyTwo = 0
	awayProbExactlyOne = 0
	awayProbExactlyTwo = 0
	for i in range(0, 5):
		for j in range(0, 5):
			# print(str(probabilityMatrix[i][j]) + ', ', end=" ")
			if i > j:
				homeProb += probabilityMatrix[i][j]
			if i < j:
				awayProb += probabilityMatrix[i][j]
			if i == j:
				drawProb += probabilityMatrix[i][j]
			if i - j == 1:
				homeProbExactlyOne += probabilityMatrix[i][j]
			if i - j == 2:
				homeProbExactlyTwo += probabilityMatrix[i][j]
			if j - i == 1:
				awayProbExactlyOne += probabilityMatrix[i][j]
			if j - i == 2:
				awayProbExactlyTwo += probabilityMatrix[i][j]
			# print("\n")
	if homeProb > awayProb:
		asianHandicap['0'] = [round((1 - drawProb) / homeProb, 2),
							  round(1 / (1 - (1 / ((1 - drawProb) / homeProb))), 2)]
		asianHandicap['0.5'] = [round(1 / homeProb, 2), round(1 / (1 - homeProb), 2)]
	for handicap, odds in asianHandicap.items():
		print(handicap, odds)


def average(someList):
	answer = sum(someList) / len(someList)
	return answer


def pois(x, mean):
	result = ((mean ** x) * math.exp(- mean)) / math.factorial(x)
	return result


def bivpois(x, y, lambda1, lambda2, lambda3):
	extraProbabilityDraws = pois(0, x) * pois(0, y)
	if x == 0 or y == 0:
		probabilityMatrix = [[0 for i in range(x + 1)] for j in range(y + 1)]
		probabilityMatrix[x][y] = math.exp(- lambda3) * pois(x, lambda1) * pois(y, lambda2)
	else:
		probabilityMatrix = [[0 for i in range(x + 1)] for j in range(y + 1)]
		probabilityMatrix[0][0] = (1 - extraProbabilityDraws) * math.exp(-lambda1 - lambda2 - lambda3)
		for i in range(1, x + 1):
			probabilityMatrix[i][0] = (probabilityMatrix[i - 1][0] * lambda1) / (i)
		for j in range(1, y + 1):
			probabilityMatrix[0][j] = (probabilityMatrix[0][j - 1] * lambda2) / (j)
		for j in range(1, y + 1):
			for i in range(1, x + 1):
				probabilityMatrix[i][j] = (lambda1 * probabilityMatrix[i - 1][j] + lambda3 * probabilityMatrix[i - 1][j - 1]) / (i)
	probabilityMatrix[0][0] = probabilityMatrix[0][0] + pois(0, x) * pois(0, y)


	#print(extraProbabilityDraws)
	return probabilityMatrix


def covariance(homeGoals, awayGoals):
	averageHomeGoals = sum(homeGoals) / len(homeGoals)
	averageAwayGoals = sum(awayGoals) / len(awayGoals)
	covariance = 0
	for i in range(len(homeGoals)):
		covariance += (homeGoals[i] - averageHomeGoals) * (awayGoals[i] - averageAwayGoals)
	covariance = covariance / (len(homeGoals) - 1)
	return covariance


def nilNilProb(homeTeam, awayTeam):
	with open('E0.csv') as csvfile:
		count = 0
		nilNil = 0
		reader = csv.DictReader(csvfile)
		for row in reader:
			for team in top6:
				if row['HomeTeam'] == homeTeam and row['AwayTeam'] == team:
					count += 1
					if row['FTHG'] == '0' and row['FTAG'] == '0':
						nilNil += 1
				if row['HomeTeam'] == team and row['AwayTeam'] == homeTeam:
					count += 1
					if row['FTHG'] == '0' and row['FTAG'] == '0':
						nilNil += 1
				if row['HomeTeam'] == awayTeam and row['AwayTeam'] == team:
					count += 1
					if row['FTHG'] == '0' and row['FTAG'] == '0':
						nilNil += 1
				if row['HomeTeam'] == team and row['AwayTeam'] == awayTeam:
					count += 1
					if row['FTHG'] == '0' and row['FTAG'] == '0':
						nilNil += 1

	return nilNil / count


def predictor(probabilityMatrix):
	x = random.random()
	running_total = 0
	home_goals = 10
	away_goals = 10
	score = []
	for i in range(0, 5):
		for j in range(0, 5):
			# print(str(probabilityMatrix[i][j]) + ', ', end =" ")
			running_total += probabilityMatrix[i][j]
			if running_total > x:
				home_goals = i
				away_goals = j
				break
		if home_goals != 10 and away_goals != 10:
			break
	if home_goals == 10 and away_goals == 10:
		home_goals = 0
		away_goals = 0
	score = [home_goals, away_goals]
	return score

def ranking_metric(homeTeam, awayTeam, ranking_dict):

	ranking_metric = (ranking_dict[homeTeam]-ranking_dict[awayTeam])/100

	return ranking_metric

def attack_grayson_rating(team, goalsFor, goalsAgainst, shotsFor, shotsAgainst, SoTFor, SoTAgainst, numberOfGames):
	GR = []
	TSR = []
	SoT_per_shot = []
	goalsForNew = goalsFor[team][-numberOfGames:]
	goalsAgainstNew = goalsAgainst[team][-numberOfGames:]
	shotsForNew = shotsFor[team][-numberOfGames:]
	shotsAgainstNew = shotsAgainst[team][-numberOfGames:]
	SoTForNew = SoTFor[team][-numberOfGames:]
	SoTAgainstNew = SoTAgainst[team][-numberOfGames:]
	for i in range(numberOfGames):
		if shotsForNew[i] == 0:
			SoT_per_shot.append(0)
		else:
			SoT_per_shot.append(SoTForNew[i]/shotsForNew[i])
	if sum(SoTForNew) == 0:
		goalConversion = 0
	else:
		goalConversion = sum(goalsForNew)/(sum(SoTForNew))
	if sum(SoTAgainstNew) == 0:
		goalConceded = 0
	else:
		goalConceded = sum(goalsAgainstNew)/sum(SoTAgainstNew)
	for i in range(numberOfGames):
		TSR.append(shotsForNew[i]/(shotsForNew[i]+shotsAgainstNew[i]))
	for i in range(numberOfGames):
		if goalsForNew[i]+goalsAgainstNew[i] == 0:
			GR.append(0)
		else:
			GR.append(goalsForNew[i]/(goalsForNew[i]+goalsAgainstNew[i]))
	TSoTR = sum(SoTForNew)/(sum(SoTForNew)+sum(SoTAgainstNew))
	#TSOTt = sum(SoTForNew)/sum(shotsForNew) + (sum(shotsAgainstNew)-sum(SoTAgainstNew))/sum(shotsAgainstNew)
	#PDO = 1000*(sum(goalsForNew)/sum(SoTForNew) + (sum(SoTAgainstNew)-sum(goalsAgainstNew))/sum(SoTAgainstNew))
	#rating = (0.5 + ((TSR-0.5)*math.pow(0.732,0.5)))*(1 + ((TSOTt-1)*math.pow(0.166,0.5)))*(1000 + ((PDO - 1000)*math.pow(0.176,0.5)))
	return average(TSR), average(SoT_per_shot), sum(goalsForNew)/sum(SoTForNew), average(GR)

def defence_grayson_rating(team, goalsFor, goalsAgainst, shotsFor, shotsAgainst, SoTFor, SoTAgainst, numberOfGames):
	GR_against = []
	TSR_against = []
	SoT_per_shot = []
	goalsForNew = goalsFor[team][-numberOfGames:]
	goalsAgainstNew = goalsAgainst[team][-numberOfGames:]
	shotsForNew = shotsFor[team][-numberOfGames:]
	shotsAgainstNew = shotsAgainst[team][-numberOfGames:]
	SoTForNew = SoTFor[team][-numberOfGames:]
	SoTAgainstNew = SoTAgainst[team][-numberOfGames:]
	for i in range(numberOfGames):
		if shotsAgainstNew[i] == 0:
			SoT_per_shot.append(0)
		else:
			SoT_per_shot.append(SoTAgainstNew[i]/shotsAgainstNew[i])
	if sum(SoTForNew) == 0:
		goalConversion = 0
	else:
		goalConversion = sum(goalsForNew)/(sum(SoTForNew))
	if sum(SoTAgainstNew) == 0:
		goalConceded = 0
	else:
		goalConceded = sum(goalsAgainstNew)/sum(SoTAgainstNew)
	for i in range(numberOfGames):
		TSR_against.append(shotsAgainstNew[i]/(shotsForNew[i]+shotsAgainstNew[i]))
	for i in range(numberOfGames):
		if goalsForNew[i]+goalsAgainstNew[i] == 0:
			GR_against.append(0)
		else:
			GR_against.append(goalsAgainstNew[i]/(goalsForNew[i]+goalsAgainstNew[i]))
	TSoTR = sum(SoTForNew)/(sum(SoTForNew)+sum(SoTAgainstNew))
	#TSOTt = sum(SoTForNew)/sum(shotsForNew) + (sum(shotsAgainstNew)-sum(SoTAgainstNew))/sum(shotsAgainstNew)
	#PDO = 1000*(sum(goalsForNew)/sum(SoTForNew) + (sum(SoTAgainstNew)-sum(goalsAgainstNew))/sum(SoTAgainstNew))
	#rating = (0.5 + ((TSR-0.5)*math.pow(0.732,0.5)))*(1 + ((TSOTt-1)*math.pow(0.166,0.5)))*(1000 + ((PDO - 1000)*math.pow(0.176,0.5)))
	return average(TSR_against), sum(goalsAgainstNew)/sum(SoTAgainstNew), average(goalsAgainstNew), average(GR_against)

def reg_m(y, x):
    ones = np.ones(len(x[0]))
    X = sm.add_constant(np.column_stack((x[0], ones)))
    for ele in x[1:]:
        X = sm.add_constant(np.column_stack((ele, X)))
    results = sm.OLS(y, X).fit()
    return results

teams = set()

rateform_dict = {}

'''with open('rsquared.csv', 'w') as csvfile:
	csvfile.write('Rsquared')
	csvfile.write(',')
	csvfile.write('Number of Preceding Games')
	csvfile.write(',')
	csvfile.write('Number of Games in Sample')
	csvfile.write('\n')'''

with open('alldata.csv') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		teams.add(row['HomeTeam'])

for team in teams:
	rateform_dict[team] = 1000


'''with open('alldata.csv') as csvfile:
	for team in teams:
		goals = []
		shotsOnTarget = []
		shotsOnTargetFaced = []
		goals = []
		goalsConc = []
		shots = []
		shotsFaced = []
		reader = csv.DictReader(csvfile)
		csvfile.seek(0)
		for row in reader:
			totalHomeGoals.append((float(row['FTHG'])))
			totalAwayGoals.append((float(row['FTAG'])))
			if row['HomeTeam'] == team:
				shotsOnTarget.append(float(row['HST']))
				shotsOnTargetFaced.append(float(row['AST']))
				goals.append((float(row['FTHG'])))
				goalsConc.append((float(row['FTAG'])))
				shots.append((float(row['HS'])))
				shotsFaced.append((float(row['AS'])))
				#TSR[team].append(float(row['HS'])/(float(row['HS'])+float(row['AS'])))
				#TsoTt[team].append(float(row['HST'])/float(row['HS'])-(float(row['AST']))/float(row['AS']))
			if row['AwayTeam'] == team:
				shotsOnTarget.append(float(row['AST']))
				shotsOnTargetFaced.append(float(row['HST']))
				goals.append((float(row['FTAG'])))
				goalsConc.append((float(row['FTHG'])))
				shots.append((float(row['AS'])))
				shotsFaced.append((float(row['HS'])))
				#TSR[team].append(float(row['AS'])/(float(row['HS'])+float(row['AS'])))
				#TsoTt[team].append(float(row['AST'])/float(row['AS'])-(float(row['HST']))/float(row['HS']))
		if len(goals) != 0:
			shotsOnTargetDict[team] = shotsOnTarget
			shotsOnTargetFacedDict[team] = shotsOnTargetFaced
			goalsDict[team] = goals
			goalsConcDict[team] = goalsConc
			shotsDict[team] = shots
			shotsFacedDict[team] = shotsFaced'''

with open('alldata.csv') as csvfile:

		ranking_dict_new = { 'Man City': 0, 'Liverpool': 0, 'Chelsea': 0, 'Arsenal': 0, 'Everton': 0, 'Tottenham': 0, 'Man United': 0, 'Southampton': 0, 'Stoke': 0, 'Newcastle': 0, 'Crystal Palace': 0, 'Swansea': 0, 'West Ham': 0, 'Sunderland': 0, 'Aston Villa': 0, 'Hull': 0, 'West Brom': 0, 'Leicester': 0, 'QPR': 0, 'Burnley': 0}
		dates = []
		totalHomeGoalsNewSeason = []
		totalAwayGoalsNewSeason = []
		teamPoints = defaultdict(list)
		homeShotsOnTargetDictNewSeason = defaultdict(list)
		awayShotsOnTargetDictNewSeason = defaultdict(list)
		homeShotsOnTargetFacedDictNewSeason = defaultdict(list)
		awayShotsOnTargetFacedDictNewSeason = defaultdict(list)
		homeGoalsDictNewSeason = defaultdict(list)
		awayGoalsDictNewSeason = defaultdict(list)
		homeGoalsConcDictNewSeason = defaultdict(list)
		awayGoalsConcDictNewSeason = defaultdict(list)
		combinedParameters = defaultdict(list)
		flags = 0
		flag = 0
		draws = 0

		with open('rsquared.csv', 'a') as csvfile2:
			z = 38
			totalHomeGoals = []
			totalAwayGoals = []
			store_x = []
			store_y = []
			TsoTt = defaultdict(list)
			TsoTtaverage = defaultdict(list)
			totalTeamPoints = defaultdict(list)
			homeShotsOnTargetDict = defaultdict(list)
			homeShotsOnTargetFacedDict = defaultdict(list)
			homeGoalsDict = defaultdict(list)
			homeGoalsConcDict = defaultdict(list)
			homeShotsDict = defaultdict(list)
			homeShotsFacedDict = defaultdict(list)
			awayShotsOnTargetDict = defaultdict(list)
			awayShotsOnTargetFacedDict = defaultdict(list)
			awayGoalsDict = defaultdict(list)
			awayGoalsConcDict = defaultdict(list)
			awayShotsDict = defaultdict(list)
			awayShotsFacedDict = defaultdict(list)
			averageTeamPoints = defaultdict(list)
			expected = [[],[],[],[],[],[],[],[]]
			actual = []
			goals = []
			shotsOnTarget = []
			shotsOnTargetFaced = []
			goals = []
			goalsConc = []
			shots = []
			shotsFaced = []
			reader = csv.DictReader(csvfile)
			csvfile.seek(0)
			for row in reader:
				total = 0
				homeProb = 0
				awayProb = 0
				drawProb = 0
				win = 0
				homeTeam = row['HomeTeam']
				awayTeam = row['AwayTeam']

				if len(homeGoalsDict[homeTeam]) > z and len(awayGoalsDict[awayTeam]) > z:
					attack_home_rating1, attack_home_rating2, attack_home_rating3, attack_home_rating4 = attack_grayson_rating(homeTeam, homeGoalsDict, homeGoalsConcDict, homeShotsDict, homeShotsFacedDict, homeShotsOnTargetDict, homeShotsOnTargetFacedDict, z)
					attack_away_rating1, attack_away_rating2, attack_away_rating3, attack_away_rating4 = attack_grayson_rating(awayTeam, awayGoalsDict, awayGoalsConcDict, awayShotsDict, awayShotsFacedDict, awayShotsOnTargetDict, awayShotsOnTargetFacedDict, z)
					defence_home_rating1, defence_home_rating2, defence_home_rating3, defence_home_rating4 = defence_grayson_rating(homeTeam, homeGoalsDict, homeGoalsConcDict, homeShotsDict, homeShotsFacedDict, homeShotsOnTargetDict, homeShotsOnTargetFacedDict, z)
					defence_away_rating1, defence_away_rating2, defence_away_rating3, defence_away_rating4 = defence_grayson_rating(awayTeam, awayGoalsDict, awayGoalsConcDict, awayShotsDict, awayShotsFacedDict, awayShotsOnTargetDict, awayShotsOnTargetFacedDict, z)
					expected[0].append(attack_home_rating1)
					expected[1].append(attack_home_rating2)
					expected[2].append(attack_home_rating3)
					expected[3].append(defence_away_rating1)
					expected[4].append(defence_away_rating2)
					expected[5].append(defence_away_rating3)
					expected[6].append(attack_home_rating4)
					expected[7].append(defence_away_rating4)
					actual.append(float(row['FTHG']))
					expected[0].append(attack_away_rating1)
					expected[1].append(attack_away_rating2)
					expected[2].append(attack_away_rating3)
					expected[3].append(defence_home_rating1)
					expected[4].append(defence_home_rating2)
					expected[5].append(defence_home_rating3)
					expected[6].append(attack_away_rating4)
					expected[7].append(defence_home_rating4)
					actual.append(float(row['FTAG']))
					'''csvfile2.write(str(home_rating))
					csvfile2.write(',')
					csvfile2.write(str(row['FTHG']))
					csvfile2.write('\n')
					csvfile2.write(str(away_rating))
					csvfile2.write(',')
					csvfile2.write(str(row['FTAG']))
					csvfile2.write('\n')'''

				if row['FTHG'] > row['FTAG']:
					rateform_dict[homeTeam] = rateform_dict[homeTeam] + 0.05*rateform_dict[awayTeam]
					rateform_dict[awayTeam] = rateform_dict[awayTeam] - 0.05*rateform_dict[awayTeam]
				if row['FTHG'] < row['FTAG']:
					rateform_dict[awayTeam] = rateform_dict[awayTeam] + 0.06*rateform_dict[homeTeam]
					rateform_dict[homeTeam] = rateform_dict[homeTeam] - 0.06*rateform_dict[homeTeam]
				if row['FTHG'] == row['FTAG']:
					rateform_dict[awayTeam] = rateform_dict[awayTeam] - 0.05*rateform_dict[awayTeam] + (0.06*rateform_dict[homeTeam] + 0.05*rateform_dict[awayTeam])/2
					rateform_dict[homeTeam] = rateform_dict[homeTeam] - 0.06*rateform_dict[homeTeam] + (0.06*rateform_dict[homeTeam] + 0.05*rateform_dict[awayTeam])/2
				# print(x, probableHomeGoals)
				# print(y, probableAwayGoals)'''
				homeShotsOnTargetDict[homeTeam].append(float(row['HST']))
				homeShotsOnTargetFacedDict[homeTeam].append(float(row['AST']))
				homeGoalsDict[homeTeam].append((float(row['FTHG'])))
				homeGoalsConcDict[homeTeam].append((float(row['FTAG'])))
				homeShotsDict[homeTeam].append((float(row['HS'])))
				homeShotsFacedDict[homeTeam].append((float(row['AS'])))

				awayShotsOnTargetDict[awayTeam].append(float(row['AST']))
				awayShotsOnTargetFacedDict[awayTeam].append(float(row['HST']))
				awayGoalsDict[awayTeam].append((float(row['FTAG'])))
				awayGoalsConcDict[awayTeam].append((float(row['FTHG'])))
				awayShotsDict[awayTeam].append((float(row['AS'])))
				awayShotsFacedDict[awayTeam].append((float(row['HS'])))

				homeTeam, homeGoalsDict, homeGoalsConcDict, homeShotsDict, homeShotsFacedDict, homeShotsOnTargetDict, homeShotsOnTargetFacedDict, z
				
print(reg_m(actual, expected).summary())		




