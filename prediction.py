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
        team_elo[team] = base_elo
        return team_elo[team]

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
    new_loser_rank=loser_rank-(new_winner_rank-winner_rank)
    return new_winner_rank, new_loser_rank

def build_dataSet(all_data):
    print("Building data set..")
    X=[]
    for index, row in all_data.iterrows():
        Wteam=row['WTeam']
        Lteam=row['LTeam']
        team1_elo=get_elo(Wteam)
        team2_elo=get_elo(Lteam)
        if row['WLoc'] == 'H':
            team1_elo += 100
        else:
            team2_elo += 100
        team1_features = [team1_elo]
        team2_features = [team2_elo]

        for key, value in team_stats.loc[Wteam].iteritems():
            team1_features.append(value)
        for key, value in team_stats.loc[Lteam].iteritems():
            team2_features.append(value)
        if random.random() > 0.5:
            X.append(team1_features + team2_features)
            y.append(0)
        else:
            X.append(team2_features + team1_features)
            y.append(1)
        new_winner_rank, new_loser_rank = calc_elo(Wteam, Lteam)
        team_elo[Wteam] = new_winner_rank
        team_elo[Lteam] = new_loser_rank
    return np.nan_to_num(X), np.array(y)

def predict_winner(team_1, team_2, model):
    features = []

    features.append(get_elo(team_1))
    for key, value in team_stats.loc[team_1].iteritems():
        features.append(value)
    features.append(get_elo(team_2)+100)
    for key, value in team_stats.loc[team_2].iteritems():
        features.append(value)
    features = np.nan_to_num(features)
    return model.predict_proba([features])


if __name__ == '__main__':

    Mstat = pd.read_csv(folder + '/15-16Miscellaneous_Stat.csv')
    Ostat = pd.read_csv(folder + '/15-16Opponent_Per_Game_Stat.csv')
    Tstat = pd.read_csv(folder + '/15-16Team_Per_Game_Stat.csv')

    team_stats = initialize_data(Mstat, Ostat, Tstat)

    result_data = pd.read_csv(folder + '/2015-2016_result.csv')
    X, y = build_dataSet(result_data)

    print("Fitting on %d game samples.." % len(X))

    model = linear_model.LogisticRegression()
    model.fit(X, y)
    print("Doing cross_validation..")
    print(cross_val_score(model, X, y, cv = 10, scoring='accuracy', n_jobs=-1).mean())

    print('Predicting on new schedle..')
    schedule1617 = pd.read_csv(folder + '/16-17Schedule.csv')
    result = []
    for index, row in schedule1617.iterrows():
        team1 = row['Vteam']
        team2 = row['Hteam']
        pred = predict_winner(team1, team2, model)
        prob = pred[0][0]
        if prob > 0.5:
            winner = team1
            loser = team2
            result.append([winner, loser, prob])
        else:
            winner = team2
            loser = team1
            result.append([winner, loser, 1-prob])

    with open('16-17Result.csv','wb') as f:
        writer = csv.writer(f)
        writer.writerow(['win', 'lose', 'probability'])
        writer.writerows(result)