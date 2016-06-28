import math
import numpy
import scipy
import csv
import urllib
import datetime
import os
import collections
import operator
from collections import defaultdict

def asianHandicap(probabilityMatrix):
	asianHandicap = {}
	homeProb = 0
	drawProb = 0
	awayProb = 0
	homeProbExactlyOne = 0
	homeProbExactlyTwo = 0
	awayProbExactlyOne = 0
	awayProbExactlyTwo = 0
	for i in range(0,5):
		for j in range(0,5):
			#print(str(probabilityMatrix[i][j]) + ', ', end=" ")
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
		#print("\n")
	if homeProb > awayProb:
		asianHandicap['0'] = [round((1-drawProb)/homeProb, 2), round(1/(1-(1/((1-drawProb)/homeProb))), 2)]
		asianHandicap['0.5'] = [round(1/homeProb, 2), round(1/(1-homeProb), 2)]
	for handicap, odds in asianHandicap.items():
		print(handicap, odds)
 
def average(someList):
	answer = sum(someList)/len(someList)
	return answer

def pois(x, mean):
	result = ((mean ** x) * math.exp(- mean))/math.factorial(x)
	return result

def bivpois(x, y, lambda1, lambda2, lambda3):
	extraProbabilityDraws = pois(0, x)*pois(0, y) + pois(1, x)*pois(1, y) + pois(2, x)*pois(2, y) + pois(3, x)*pois(3, y)
	if x == 0 or y == 0:
		probabilityMatrix = [ [ 0 for i in range(x+1) ] for j in range(y+1) ]
		probabilityMatrix[x][y] = math.exp( - lambda3) * pois(x, lambda1) * pois(y, lambda2)
	else:
		probabilityMatrix = [ [ 0 for i in range(x+1) ] for j in range(y+1) ]
		probabilityMatrix[0][0] = (1-extraProbabilityDraws)*math.exp(-lambda1 - lambda2 - lambda3)
		for i in range(1, x+1):
			probabilityMatrix[i][0] = (probabilityMatrix[i-1][0] * lambda1)/(i)
		for j in range(1, y+1):
			probabilityMatrix[0][j] = (probabilityMatrix[0][j-1] * lambda2)/(j)
		for j in range(1, y+1):
			for i in range(1,x+1):
				probabilityMatrix[i][j] = (lambda1 * probabilityMatrix[i-1][j] + lambda3 * probabilityMatrix[i-1][j-1])/(i)
	probabilityMatrix[0][0] = probabilityMatrix[0][0] + pois(0, x)*pois(0, y)
	probabilityMatrix[1][1] = probabilityMatrix[1][1] + pois(1, x)*pois(1, y)
	probabilityMatrix[2][2] = probabilityMatrix[2][2] + pois(2, x)*pois(2, y)
	probabilityMatrix[3][3] = probabilityMatrix[3][3] + pois(3, x)*pois(3, y)				

	return probabilityMatrix

def covariance(homeGoals, awayGoals):
	averageHomeGoals = sum(homeGoals)/len(homeGoals) 
	averageAwayGoals = sum(awayGoals)/len(awayGoals) 
	covariance = 0
	for i in range(len(homeGoals)):
		covariance += (homeGoals[i] - averageHomeGoals)*(awayGoals[i] - averageAwayGoals)
	covariance = covariance/(len(homeGoals)-1)
	return covariance

def nilNilProb(homeTeam, awayTeam):
	with open('E0.csv') as csvfile:
		count = 0
		nilNil = 0
		reader = csv.DictReader(csvfile)
		for row in reader:
			for team in top6:
				if row['HomeTeam'] == homeTeam and row['AwayTeam'] == team:
					count+=1
					if row['FTHG'] == '0' and row['FTAG'] == '0':
						nilNil+=1
				if row['HomeTeam'] == team and row['AwayTeam'] == homeTeam:
					count+=1
					if row['FTHG'] == '0' and row['FTAG'] == '0':
						nilNil+=1
				if row['HomeTeam'] == awayTeam and row['AwayTeam'] == team:
					count+=1
					if row['FTHG'] == '0' and row['FTAG'] == '0':
						nilNil+=1
				if row['HomeTeam'] == team and row['AwayTeam'] == awayTeam:
					count+=1
					if row['FTHG'] == '0' and row['FTAG'] == '0':
						nilNil+=1

	return nilNil/count

'''#download new data
def downloadData():
	from urllib import request
	response = request.urlopen("http://www.football-data.co.uk/mmz4281/1516/E0.csv")
	downloadValues = response.read()
	csvstr = str(downloadValues).strip("b'")
	lines = csvstr.split("\\r\\n")
	f = open("download.csv", "w")
	for line in lines:
	   f.write(line + "\n")
	f.close()
downloadData()

#update data
with open('download.csv') as csvfile:
	fieldnames = ['Div','Date','HomeTeam','AwayTeam','FTHG','FTAG','FTR','HTHG','HTAG','HTR','Referee','HS','AS','HST','AST','HF','AF','HC','AC','HY','AY','HR','AR','B365H','B365D','B365A','BWH','BWD','BWA','IWH','IWD','IWA','LBH','LBD','LBA','PSH','PSD','PSA','WHH','WHD','WHA','VCH','VCD','VCA','Bb1X2','BbMxH','BbAvH','BbMxD','BbAvD','BbMxA','BbAvA','BbOU','BbMx>2.5','BbAv>2.5','BbMx<2.5','BbAv<2.5','BbAH','BbAHh','BbMxAHH','BbAvAHH','BbMxAHA','BbAvAHA']
	downloadReader = csv.DictReader(csvfile)
	downloadWriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
	with open('E0.csv') as csvfile:
		mainReader = csv.DictReader(csvfile)
		for mainRow in mainReader:
			lastDate = mainRow['Date']
		lastDate = datetime.datetime.strptime(lastDate, '%d/%m/%y')
	with open('E0.csv', 'a') as csvfile:
		mainWriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
		for downloadRow in downloadReader:
			if datetime.datetime.strptime(downloadRow['Date'], '%d/%m/%y') > lastDate:
				mainWriter.writerow(downloadRow)'''




for year in range(2010, 2014):

	teams = set()
	dates = []
	totalHomeGoals = []
	totalAwayGoals = []
	tenElevenHomeAttackParameters = {}
	tenElevenHomeDefenseParameters = {}
	tenElevenAwayAttackParameters = {}
	tenElevenAwayDefenseParameters = {}
	combinedParameters = {}
	amountBetted = 0
	totalAmountWon = 0
	amountOfBets = 0
	flags = 0
	draws = 0
	errorsquared = []
	oddsBet = []
	oddsCalculated = []
	with open('backtest.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			teams.add(row['HomeTeam'])


	with open('backtest.csv') as csvfile:
		for team in teams:
			totalHomeGoals = []
			totalAwayGoals = []
			homeGoals = []
			awayGoals = []
			homeGoalsConc = []
			awayGoalsConc = []
			reader = csv.DictReader(csvfile)
			csvfile.seek(0)
			for row in reader:
				if datetime.datetime.strptime(row['Date'], "%d/%m/%y") > datetime.datetime(year, 6, 1) and datetime.datetime.strptime(row['Date'], "%d/%m/%y") < datetime.datetime(year+1, 6, 1):
					totalHomeGoals.append(float(row['FTHG']))
					totalAwayGoals.append(float(row['FTAG']))
					if row['HomeTeam'] == team:
						homeGoals.append(float(row['FTHG']))
						homeGoalsConc.append(float(row['FTAG']))
					if row['AwayTeam'] == team:
						awayGoals.append(float(row['FTAG']))
						awayGoalsConc.append(float(row['FTHG']))
			if len(homeGoals) != 0:
				tenElevenHomeAttackParameters[team] = average(homeGoals)/average(totalHomeGoals)
				tenElevenHomeDefenseParameters[team] = average(homeGoalsConc)/average(totalAwayGoals)
				tenElevenAwayAttackParameters[team] = average(awayGoals)/average(totalAwayGoals)
				tenElevenAwayDefenseParameters[team] = average(awayGoalsConc)/average(totalHomeGoals)
				combinedParameters[team] = tenElevenHomeAttackParameters[team]+tenElevenAwayAttackParameters[team]-tenElevenHomeDefenseParameters[team]-tenElevenAwayDefenseParameters[team]
				
		
	with open('backtest.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		csvfile.seek(0)
		for row in reader:
			total = 0
			homeProb = 0
			awayProb = 0
			drawProb = 0
			win = 0
			if datetime.datetime.strptime(row['Date'], "%d/%m/%y") > datetime.datetime(year+1, 6, 1) and datetime.datetime.strptime(row['Date'], "%d/%m/%y") < datetime.datetime(year+2, 6, 1):
				homeTeam = row['HomeTeam']
				awayTeam = row['AwayTeam']
				if homeTeam in tenElevenHomeAttackParameters and awayTeam in tenElevenAwayAttackParameters:
					x = tenElevenHomeAttackParameters[homeTeam]*tenElevenAwayDefenseParameters[awayTeam]
					y = tenElevenAwayAttackParameters[awayTeam]*tenElevenHomeDefenseParameters[homeTeam]
					probabilityMatrix = bivpois(6, 6, x, y, covariance(totalHomeGoals, totalAwayGoals))
					for i in range(0,5):
						for j in range(0,5):
							#print(str(probabilityMatrix[i][j]) + ', ', end=" ")
							total += probabilityMatrix[i][j]
							if i > j:
								homeProb += probabilityMatrix[i][j]
							if i < j:
								awayProb += probabilityMatrix[i][j]
							if i == j:
								drawProb += probabilityMatrix[i][j]
						#print("\n")
					if 1/drawProb < float(row['B365D']):
						#print('DRAW', amountOfBets, 1/homeProb, row['B365H'], 1/drawProb, row['B365D'], 1/awayProb, row['B365A'])
						draws += 1
					if 1/homeProb < float(row['B365H']) and 1/awayProb < float(row['B365A']):
						#print('FLAG', amountOfBets)
						flags+=1
					if 1/homeProb < float(row['B365H']) and 1/homeProb < 3:
						amountOfBets += 1
						amountBet = 5/(float(row['B365H'])-1)
						amountBetted += amountBet
						oddsBet.append(float(row['B365H']))
						oddsCalculated.append(float(1/homeProb))
						if float(row['FTHG']) > float(row['FTAG']):
							win = float(row['B365H'])*amountBet - amountBet
							totalAmountWon += win
						else:
							totalAmountWon += -amountBet
							win = -amountBet
						#print('HOME', homeTeam, awayTeam, 1/homeProb, row['B365H'], amountBetted, totalAmountWon, win)
					if 1/awayProb < float(row['B365A']) and 1/awayProb < 3:
						amountOfBets += 1
						amountBet = 5/(float(row['B365A'])-1)
						amountBetted += amountBet
						oddsBet.append(float(row['B365A']))
						oddsCalculated.append(float(1/awayProb))
						if float(row['FTHG']) < float(row['FTAG']):
							win = float(row['B365A'])*amountBet - amountBet
							totalAmountWon += win
						else:
							totalAmountWon += -amountBet
							win = -amountBet
						#print('AWAY', homeTeam, awayTeam, 1/awayProb, row['B365A'], amountBetted, totalAmountWon, win)
					mostProbable = 0
					probableHomeGoals = 0
					probableAwayGoals = 0
					for i in range(0,5):
						for j in range(0,5):
							if probabilityMatrix[i][j] > mostProbable:
								mostProbable = probabilityMatrix[i][j]
								probableHomeGoals = i
								probableAwayGoals = j
					errorsquared.append((float(row['FTHG']) - float(probableHomeGoals))*(float(row['FTHG']) - float(probableHomeGoals)))
					errorsquared.append((float(row['FTAG']) - float(probableAwayGoals))*(float(row['FTAG']) - float(probableAwayGoals)))
					#print(homeTeam, awayTeam, 1/homeProb, row['B365H'], amountBetted, amountWon)
	roi = totalAmountWon/amountBetted
	print(year+1, '-', year+2,roi, amountOfBets, flags, draws, amountBetted*roi, average(oddsBet), average(oddsCalculated))
	print(numpy.sqrt(average(errorsquared)))

