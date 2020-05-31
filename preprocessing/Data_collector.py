import requests
from preprocessing.PlayerDictionary import PlayerDictionary


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
playerDictionary = PlayerDictionary()
for competitionId in competitionIds:
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
        allStatCategories=[]
        for i in range(3):
            statCategory = team['statistics'][i]
            statCategoryName = statCategory['name']
            players = statCategory['athletes']
            columnHeaders = statCategory['labels']
            allStatCategories.append(columnHeaders)
            for athlete in players:
                playerDictionary.__setitem__(self,)
                ## Get athlete data and save to the correct playerDictionary sub dictionary

