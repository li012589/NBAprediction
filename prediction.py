import pandas as pd
import math
import csv
import random
import numpy as np
from sklearn import linear_model
from sklearn.model_selection import cross_val_score

base_elo = 1600
team_elo = {}
team_stats = {}
X = []
y = []
folder = 'data'

def initialize_data(Mstat, Ostat, Tstat):
    new_Mstat = Mstat.drop(['Rk','Arena'],axis=1)
    new_Ostat = Ostat.drop(['Rk','G','MP'], axis=1)
    new_Tstat = Tstat.drop(['Rk','G','MP'], axis=1)

    team_stats1 = pd.merge(new_Mstat, new_Ostat, how='left', on='Team')
    team_stats1 = pd.merge(team_stats1, new_Tstat, how='left', on='Team')
    return team_stats1.set_index('Team', inplace=False, drop=True)

def get_elo(team):
    try:
        return team_elo[team]
    except:
        team_elo[team] = baee_elo

def calc_elo(win_team, lose_team):
    winner_rank = get_elo(win_team)
    loser_rank = get_elo(lose_team)
    rank_diff = winner_rank - loser_rank
    exp = (rank_diff*-1)/400
    odds=1/(1+math.pow(10,exp))
    if winner_rank < 21000:
        k=32
    elif winner_rank >= 2100 and winner_rank< 2400:
        k=24
    else:
        k=16
    new_winner_rank=round(winner_rank+(k*(1-odds)))
    new_loser_rank=lose_team-(new_winner_rank-winner_rank)
    return new_winner_rank, new_loser_rank

def build_dataSet(all_data):
    print("Building data set..")
    x=[]
    skip=0
    for index, row in all_data.iterrows():
        Wteam=row['Wteam']
        Lteam=row['Lteam']
        team1_elo=get_elo(Wteam)
        team2_elo=get_elo(Lteam)
        if row['WLoc'] == 'H':
            team1_elo += 100
        else:
            team2_elo +=100
        team1_features = [team1_elo]
        team2_features = [team2_elo]

        for key, value in team_stats.loc[Wteam].iteritems():
            team1_features.append(value)
        for key, value in team_stats.loc[Lteam].iteritems():
            team2_features.append(value)
        