import pandas as pd
import numpy as np
import requests


startdate = "20190905"
enddate = "20190911"

eventId = ""

gameurl = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event=%s" (eventId)
eventurl = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=%s-%s" (startdate,enddate)

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

for competitionId in competitionIds:
    eventId = competitionId
    gameResponse = requests.get(gameurl)
    ## Continue with logic to parse response for stats