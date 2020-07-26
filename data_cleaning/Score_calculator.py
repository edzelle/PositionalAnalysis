import pandas as pd
import configparser

config = configparser.ConfigParser()
config.read("./../properties.ini")

raw_data = config['PATHS']['raw_data']
df = pd.read_csv(raw_data)

df2 = df.drop(df.columns[[0,1,2,3,4,5,10,11,12]], axis=1)
standard = [.04,0,4,-2,0,.1,0,6,0,0,0,.1,0,6,0]
ppr = [.04,0,4,-2,1,.1,0,6,0,0,0,.1,0,6,0]
halfppr = [.04,0,4,-2,.5,.1,0,6,0,0,0,.1,0,6,0]
wreck = [.02,0,3,0,0,.04,0,6,0,0,0,.04,0,6,0]
tdonly = [0,0,3,0,0,0,0,6,0,0,0,0,0,6,0]

dotStandard = df2.dot(standard)
dotPpr = df2.dot(ppr)
dotHalfPpr = df2.dot(halfppr)
dotWreck = df2.dot(wreck)
dotTdOnly = df2.dot(tdonly)

df["standard"] = dotStandard
df["ppr"] = dotPpr
df["half_ppr"] = dotHalfPpr
df["wreck"] = dotWreck
df["td_only"] = dotTdOnly

df.to_csv(config['PATHS']['score_data'])