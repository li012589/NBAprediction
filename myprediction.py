import pandas as pd
import math
import random
import numpy as np
from sklearn import linear_model
from sklearn.model_selection import cross_val_score

baseElo = 1600
teamElo = {}
X = []
y = []
folder = 'data'

def readData(Mstat, Ostat, Tstat):
    dataSet = Mstat.drop(['Rk','Arena'], axis=1)
    tmp = Ostat.drop(['Rk','G','MP'],axis=1)
    dataSet = pd.merge(dataSet,tmp,how='left',on='Team')
    tmp = Tstat.drop(['Rk','G','MP'],axis=1)
    dataSet = pd.merge(dataSet,tmp,how='left',on='Team')
    return dataSet.set_index('Team',drop=False)

def initElo(dataSet):
    for team in dataSet['Team']:
        teamElo[team]=baseElo

def eloCalc(resultDF):
    for index, row in resultDF.iterrows():
        winTeam=row['WTeam']
        loseTeam=row['LTeam']
        winTeamRank=teamElo[winTeam]
        loseTeamRank=teamElo[loseTeam]
        if row['WLoc'] == 'H':
            winTeamRank += 100
        else:
            loseTeamRank +=100
        if winTeamRank < 2100:
            k=32
        elif winTeamRank >=2100 and winTeamRank <2400:
            k=24
        else:
            k=16
        odd=1/(1+math.pow(10,(loseTeamRank-winTeamRank)/400))
        newWinTeamRank=round(winTeamRank+k*(1-odd))
        newLoseTeamRank=loseTeamRank-(newWinTeamRank-winTeamRank)
        teamElo[winTeam]=newWinTeamRank
        teamElo[loseTeam]=newLoseTeamRank

def buildDateSet(dataSet,csvResult):
    X=[]
    y=[]
    for index, row in csvResult.iterrows():
        winTeam = row['WTeam']
        loseTeam = row['LTeam']
        line1=[]
        line2=[]
        for index, key in dataSet.loc[winTeam].iteritems():
            line1.append(key)
        for index, key in dataSet.loc[loseTeam].iteritems():
            line2.append(key)
        if random.random()>0.5:
            X.append(line1+line2)
            y.append(0)
        else:
            X.append(line2+line1)
            y.append(0)
            
    return X,y

def main():
    Mstat = pd.read_csv(folder + '/15-16Miscellaneous_Stat.csv')
    Ostat = pd.read_csv(folder + '/15-16Opponent_Per_Game_Stat.csv')
    Tstat = pd.read_csv(folder + '/15-16Team_Per_Game_Stat.csv')
    schedule = pd.read_csv(folder + '/16-17Schedule.csv')
    csvResult = pd.read_csv(folder + '/2015-2016_result.csv')

    dataSet = readData(Mstat, Ostat, Tstat)
    #print dataSet
    initElo(dataSet)
    eloCalc(csvResult)
    X,y=buildDateSet(dataSet,csvResult)

if __name__ == '__main__':
    main()
