import configparser
import requests
import numpy as np
import pandas as pd

config = configparser.ConfigParser()
config.read("./../properties.ini")


years = ["2013","2014","2015","2016","2017","2018","2019"]

winningscore = []
losingscore = []
tiedscores = []
for year in years:
    config.set('PARAMETERS','year',year)
    matchupUrl = config.get('PARAMETERS','wreck_league_matchup')
    matchupResponse = requests.get(matchupUrl)

    if matchupResponse.ok:
        matchups = matchupResponse.json()
        print("matchups data for year %s" % year)
    else:
        print("Error fetching data from API\n")
        print("Year = %s" % year)
        continue

    schedule = matchups[0]['schedule']
    for game in schedule:
        homescore = game['home']['totalPoints']
        awayscore = game['away']['totalPoints']
        if homescore > awayscore:
            winningscore.append(homescore)
            losingscore.append(awayscore)
        elif awayscore > homescore:
            winningscore.append(awayscore)
            losingscore.append(homescore)
        else:
            tiedscores.append(homescore)

df = pd.DataFrame(np.transpose([winningscore,losingscore]), columns = ['winningscore','losingscore'])
df.to_csv(config['PATHS']['matchup_data'])