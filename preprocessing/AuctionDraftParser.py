import configparser
import requests
import pandas as pd
import matplotlib.pyplot as plt
import sys

try:  # SciPy >= 0.19
    from scipy.special import comb, logsumexp
except ImportError:
    from scipy.misc import comb, logsumexp  # noqa

sys.path.append('./..')

import secrets

import numpy as np
from sklearn.linear_model import LinearRegression

def plot_player_rank_as_a_function_of_auction_values(x,y,c):
    X = np.array(x).reshape(-1, 1)

    Y = np.array(y).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, Y)

    x_new = np.linspace(0, 100, 200)
    y_new = model.predict(x_new[:, np.newaxis])
    ax = plt.axes()
    ax.plot(x_new, y_new, label='Correlation = ' + str(model.score(X, Y)))
    plt.xlabel('Auction Price')
    plt.ylabel('End of Season Rank')
    plt.title('Player Rank as a function of Auction Price')
    plt.legend()
    plt.scatter(x, y, c=c, alpha=0.5, label='Correlation = ' + str(model.score(X, Y)))

    plt.savefig('./../Resources/Plots/Player Rank as a function of Auction Price')

    plt.show()

def plot_positional_correlation(df_pos, title):
    x = list(df_pos['bidAmount'])
    y = list(df_pos['positionRank'])

    X = np.array(x).reshape(-1, 1)

    Y = np.array(y).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, Y)

    yhat = model.predict(X)
    SS_Residual = sum((Y - yhat) ** 2)
    SS_Total = sum((Y - np.mean(Y)) ** 2)
    r_squared = 1 - (float(SS_Residual)) / SS_Total

    x_new = np.linspace(0, int(max(x)), 100)
    y_new = model.predict(x_new[:, np.newaxis])
    ax = plt.axes()
    ax.plot(x_new, y_new, label='Correlation = ' + str(r_squared))
    plt.xlabel('Auction Price')
    plt.ylabel('Position Rank of Season Rank')
    plt.title(title)
    plt.legend()
    plt.scatter(x, y, alpha=0.5, label='Correlation = ' + str(model.score(X, Y)))

    plt.savefig('./../Resources/Plots/'+title)
    plt.show()

def mapToColor(a):
    if a == 'B':
        return 'blue'
    else:
        return 'red'

def getAuctionResults(cookies):
    auctionResultsUrl = config.get('PARAMETERS', 'wreck_league_auction')
    auctionResultsResponse = requests.get(auctionResultsUrl, cookies=cookies)

    if auctionResultsResponse.ok:
        auctionResultsResponseData = auctionResultsResponse.json()
        return auctionResultsResponseData

    else:
        print("Error fetching data from API\n")

def parseAuctionDataResponse(auctionResultsResponseData, draftedPlayers):
    for player in auctionResultsResponseData['draftDetail']['picks']:
        draftedPlayers.append([player['playerId'], player['bidAmount']])

def getPlayerRankResults(cookies, headers):
    playerRankUrl = config.get('PARAMETERS', 'wreck_league_player_rankings')
    playerRankResponse = requests.get(playerRankUrl, cookies=cookies, headers=headers)

    if playerRankResponse.ok:
        playerRankResponseData = playerRankResponse.json()
        return playerRankResponseData
    else:
        print("Error fetching data from API\n")

def parsePlayerRankResponse(playerRankResponseData, playerList, year):
    for player in playerRankResponseData['players']:
        posId = player['player']['defaultPositionId']
        if (posId == 1):
            if (player['ratings']['0']['positionalRanking'] > 24):
                continue
        elif (posId == 2):
            if (player['ratings']['0']['positionalRanking'] > 36):
                continue
        elif (posId == 3):
            if (player['ratings']['0']['positionalRanking'] > 36):
                continue
        elif (posId == 4):
            if (player['ratings']['0']['positionalRanking'] > 15):
                continue
        elif (posId == 5):
            if (player['ratings']['0']['positionalRanking'] > 35):
                continue
        row = [player['id'], player['player']['fullName'], player['player']['defaultPositionId'],
               player['ratings']['0']['positionalRanking'], player['ratings']['0']['totalRanking'], year]
        playerList.append(row)

def createDataFrame(playerList, draftedPlayers):
    df_left = pd.DataFrame(playerList, columns=['id', 'name', 'positionId', 'positionRank', 'overallRank', 'year'])
    df_right = pd.DataFrame(draftedPlayers, columns=['id', 'bidAmount'])
    df = df_left.merge(df_right, on='id', how='left')
    df['bidAmount'] = df['bidAmount'].fillna(1)
    df.sort_values("bidAmount", ascending=False, inplace=True)

    pickNumber = []
    bidValues = list(df['bidAmount'])

    i = 0
    count = 1
    rank = 1
    while i < len(bidValues):
        if i != len(bidValues) - 1 and bidValues[i] == bidValues[i + 1]:
            count += 1
        else:
            pickNumber.extend([rank] * count)
            rank += count
            count = 1
        i += 1

    df['pickNumber'] = pickNumber

    overallRank = list(df['overallRank'])
    labels = []
    i = 0
    while i < len(df):
        if pickNumber[i] + 6 <= overallRank[i]:
            labels.append('B')
        else:
            labels.append('L')
        i += 1

    df['label'] = labels
    return df, overallRank, labels

config = configparser.ConfigParser()
config.read("./../properties.ini")
espn_s2 = secrets.espn_s2
SWID = secrets.SWID
cookies = {'espn_s2': espn_s2, 'SWID': SWID}
xffHeader = "{\"players\":{\"limit\":350,\"sortPercOwned\":{\"sortAsc\":false,\"sortPriority\":1}}}"
headers = {'X-Fantasy-Filter': xffHeader}



df = pd.DataFrame()
for year in ['2021', '2019']:
    config.set('PARAMETERS', 'year', year)
    draftedPlayers = []
    playerList = []

    # Get Auction Data from API
    auctionResultsResponseData = getAuctionResults(cookies)
    # Parse Auction Data Response
    parseAuctionDataResponse(auctionResultsResponseData, draftedPlayers)
    # Get Player Rank Data from API
    playerRankResponseData = getPlayerRankResults(cookies, headers)
    # Parse Player Rank Data Response
    parsePlayerRankResponse(playerRankResponseData, playerList, year)

    year_df, overallRank, labels = createDataFrame(playerList, draftedPlayers)
    if (df.columns.size > 0):
        df = df.append((year_df))
    else:
        df = year_df

qbs = df.loc[df['positionId'] == 1]
rbs = df.loc[df['positionId'] == 2]
wrs = df.loc[df['positionId'] == 3]
tes = df.loc[df['positionId'] == 4]
ks = df.loc[df['positionId'] == 5]




x = list(df['bidAmount'])
y = list(df['overallRank'])
c = [mapToColor(i) for i in list(df['label'])]


plot_player_rank_as_a_function_of_auction_values(x, y, c)
plot_positional_correlation(qbs, "QB Position Rank as a function of Auction Price")
plot_positional_correlation(rbs, "RB Position Rank as a function of Auction Price")
plot_positional_correlation(wrs, "WR Position Rank as a function of Auction Price")
plot_positional_correlation(tes, "TE Position Rank as a function of Auction Price")
plot_positional_correlation(ks, "K Position Rank as a function of Auction Price")


df.to_csv("./../Resources/2019-2021-player-draft-results-and-labels.csv")