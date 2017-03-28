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
    return dataSet

def initElo(dataSet):
    for team in dataSet['Team']:
        teamElo[team]=baseElo

def eloCalu(resultDF):
    for index, row in resultDF.iterrows():
        pass

def main():
    Mstat = pd.read_csv(folder + '/15-16Miscellaneous_Stat.csv')
    Ostat = pd.read_csv(folder + '/15-16Opponent_Per_Game_Stat.csv')
    Tstat = pd.read_csv(folder + '/15-16Team_Per_Game_Stat.csv')
    schedule = pd.read_csv(folder + '/16-17Schedule.csv')
    csvResult = pd.read_csv(folder + '/2015-2016_result.csv')

    dataSet = readData(Mstat, Ostat, Tstat)
    initElo(dataSet)
    eloCalu(csvResult)


if __name__ == '__main__':
    main()
