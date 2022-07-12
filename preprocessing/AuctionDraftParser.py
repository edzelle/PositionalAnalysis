import configparser
import requests
import pandas as pd
import matplotlib.pyplot as plt
import sys

sys.path.append('./..')

import secrets

#import numpy as np
#from sklearn.linear_model import LinearRegression


def mapToColor(a):
    if a == 'B':
        return 'blue'
    else:
        return 'red'

config = configparser.ConfigParser()
config.read("./../properties.ini")



config.set('PARAMETERS','year', '2021')

espn_s2 = secrets.espn_s2
SWID = secrets.SWID

cookies = {'espn_s2': espn_s2    , 'SWID': SWID}

xffHeader = "{\"players\":{\"limit\":350,\"sortPercOwned\":{\"sortAsc\":false,\"sortPriority\":1}}}"

auctionResultsUrl = config.get('PARAMETERS', 'wreck_league_auction')
auctionResultsResponse = requests.get(auctionResultsUrl, cookies = cookies)

if auctionResultsResponse.ok:
    auctionResultsResponseData = auctionResultsResponse.json()
else:
    print("Error fetching data from API\n")

draftedPlayers = []
for player in auctionResultsResponseData['draftDetail']['picks']:
    draftedPlayers.append([player['playerId'], player['bidAmount']])

headers = {'X-Fantasy-Filter': xffHeader}

playerRankUrl = config.get('PARAMETERS', 'wreck_league_player_rankings')
playerRankResponse = requests.get(playerRankUrl, cookies = cookies, headers = headers)

if playerRankResponse.ok:
    playerRankResponseData = playerRankResponse.json()
else:
    print("Error fetching data from API\n")

playerList = []
for player in playerRankResponseData['players']:
    row = [player['id'], player['player']['fullName'], player['player']['defaultPositionId'], player['ratings']['0']['positionalRanking'], player['ratings']['0']['totalRanking']]
    playerList.append(row)

df_left = pd.DataFrame(playerList, columns = ['id','name','positionId','positionRank','overallRank'])

df_right = pd.DataFrame(draftedPlayers, columns = ['id','bidAmount'])

df = df_left.merge(df_right, on='id', how='left')

df['bidAmount'] = df['bidAmount'].fillna(1)

df.sort_values("bidAmount", ascending=False, inplace=True)

pickNumber = []

bidValues = list(df['bidAmount'])

i = 0
count = 1
rank = 1
while i < len(bidValues):
    if i != len(bidValues) - 1 and bidValues[i] == bidValues[i+1]:
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

'''

df2 = df_right.merge(df_left, on='id', how='left')

df2 = df2[(df2['overallRank'] < 150)]



pickNumber = list(range(1,len(df2)+1))

df2['pickNumber'] = pickNumber

overallRank = list(df2['overallRank'])
labels = []
i = 0
while i < len(df2):
    if pickNumber[i] + 6 <= overallRank[i]:
        labels.append('B')
    else:
        labels.append('L')
    i += 1

df2['label'] = labels
'''

x = list(df['bidAmount'])
y = overallRank
c = [mapToColor(i) for i in labels]

'''
model = LinearRegression()
model.fit(x, y)

x_new = np.linspace(0, 30, 100)
y_new = model.predict(x_new[:, np.newaxis])
ax = plt.axes()
ax.plot(x_new, y_new)
'''
plt.scatter(x, y, c=c, alpha=0.5)



plt.show()
