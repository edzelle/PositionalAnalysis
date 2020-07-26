import requests
import numpy as np
from GetPostitionFromId import getPositionFromId
import configparser


startdateList = ["20190905","20190912","20190919","20190926","20191003","20191010","20191017","20191024","20191031","20191107","20191114","20191121","20191128","20191205","20191212","20191219","20191226"]
enddateList = ["20190911","20190918","20190925","20191002","20191009","20191016","20191023","20191030","20191106","20191113","20191120","20191127","20191204","20191211","20191218","20191225","20200102"]

i = 0
allStatCategories = {}
playerDictionary = {}
rowList = []
headers = []

config = configparser.ConfigParser()
config.read("./../properties.ini")

while(i < len(startdateList)):
    startdate = startdateList[i]
    enddate = enddateList[i]
    config.set("PARAMETERS", "startdate", startdate)
    config.set("PARAMETERS", "enddate", enddate)
    eventurl = config.get('PARAMETERS','eventurl')
    print(eventurl)
    eventResponse = requests.get(eventurl)

    if eventResponse.ok:
        events=eventResponse.json()
        print("data for dates %s - %s" % (startdate,enddate))
    else:
        print("Error fetching data from API\n")
        print("StartDate = %s, EndDate = %s" % (startdate,enddate))
        exit(0)


    games = events.get("events")
    competitionIds = []
    for game in games:
        competitionIds.append(game.get("id"))

    ## The list of game will be used to make API calls by modifying the gameurl
    for competitionId in competitionIds:
        eventId = competitionId
        config.set('PARAMETERS', 'eventId', eventId)
        gameurl = config.get('PARAMETERS','gameurl')
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
            for j in range(3):
                statCategory = team['statistics'][j]
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
                        athleteDict["pos"] = getPositionFromId(athleteDict["id"])
                    else:
                        athleteDict = playerDictionary[displayName]
                    athleteDict[statCategoryName] = statLine
                    playerDictionary[displayName] = athleteDict
    ## create data output
    if i == 0:
        headers.extend(["playerName","playerId","week","pos"])
        for category in sorted(allStatCategories.keys()):
            headers.extend(allStatCategories[category])
    for player in playerDictionary.keys():
        statDict = playerDictionary[player]
        id = playerDictionary[player]["id"]
        pos = playerDictionary[player]["pos"]
        row = [player,id,i+1,pos]
        if "passing" not in statDict.keys():
            row.extend(np.zeros(len(allStatCategories["passing"])))
        else:
            row.extend(statDict["passing"])
        if "receiving" not in statDict.keys():
            row.extend(np.zeros(len(allStatCategories["receiving"])))
        else:
            row.extend(statDict["receiving"])
        if "rushing" not in statDict.keys():
            row.extend(np.zeros(len(allStatCategories["rushing"])))
        else:
            row.extend(statDict["rushing"])
        rowList.append(row)
    i += 1

import pandas as pd


df = pd.DataFrame(rowList, columns=headers)

df.to_csv(config['PATHS']['raw_data'])
