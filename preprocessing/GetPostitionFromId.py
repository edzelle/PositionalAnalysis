import requests
def getPositionFromId( id ):
    positionUrl = "https://site.web.api.espn.com/apis/common/v3/sports/football/nfl/athletes/%s" % (id)

    eventResponse = requests.get(positionUrl)

    if eventResponse.ok:
        player = eventResponse.json()
    else:
        print("Error fetching data from API")
        exit(0)

    id = player["athlete"]["position"]["abbreviation"]
    return id