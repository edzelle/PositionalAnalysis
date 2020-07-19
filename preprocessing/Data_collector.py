import requests
import numpy as np


startdate = "20190905"
enddate = "20190911"

eventurl = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=%s-%s" % (startdate, enddate)

eventResponse = requests.get(eventurl)

if eventResponse.ok:
    events=eventResponse.json()
else:
    print("Error fetching data from API")
    exit(0)


games = events.get("events")
competitionIds = []
for game in games:
    competitionIds.append(game.get("id"))

## The list of game will be used to make API calls by modifying the gameurl
allStatCategories = {}
for competitionId in competitionIds:
    playerDictionary = {}
    eventId = competitionId
    gameurl = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event=%s" % eventId
    gameResponse = requests.get(gameurl)
    if gameResponse.ok:
        gameStats = gameResponse.json()
    else:
        print("Error fetching game data with game id = %s using request string \n %s" % (eventId,gameurl) )
        continue

    ## Continue with logic to parse response for stats
    teamStats = gameStats['boxscore']['players'] ## List type with players from both teams
    for team in teamStats:
        teamName = team['team']['abbreviation']
        for i in range(3):
            statCategory = team['statistics'][i]
            statCategoryName = statCategory['name']
            players = statCategory['athletes']
            columnHeaders = statCategory['labels']
            allStatCategories[statCategoryName] = columnHeaders
            for athlete in players:
                statLine = []
                displayName = athlete["athlete"]["displayName"]
                statLine.extend(athlete["stats"])
                athleteDict = {}
                if displayName not in list(playerDictionary.keys()):
                    athleteDict["id"] = athlete["athlete"]["id"]
                else:
                    athleteDict = playerDictionary[displayName]
                athleteDict[statCategoryName] = statLine;
                playerDictionary[displayName] = athleteDict
## create data output
headers = []
headers.extend(["playerName","playerId","week"])
for category in allStatCategories.keys():
    headers.extend(allStatCategories[category])
import pandas as pd
rowList = []
for player in playerDictionary.keys():
    statDict = playerDictionary[player]
    id = playerDictionary[player]["id"]
    row = [player,id,1]
    if "passing" not in statDict.keys():
        row.extend(np.zeros(len(allStatCategories["passing"])))
    else:
        row.extend(statDict["passing"])
    if "rushing" not in statDict.keys():
        row.extend(np.zeros(len(allStatCategories["rushing"])))
    else:
        row.extend(statDict["rushing"])
    if "receiving" not in statDict.keys():
        row.extend(np.zeros(len(allStatCategories["receiving"])))
    else:
        row.extend(statDict["receiving"])
    rowList.append(row)

df = pd.DataFrame(rowList, columns=headers)
