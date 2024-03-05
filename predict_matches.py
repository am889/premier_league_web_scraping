import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,precision_score
matches=pd.read_csv("premier_league_matches.csv")
# print(matches.dtypes)
matches['date'] = pd.to_datetime(matches['date'], format="%Y-%m-%d")
matches['venue_code']= matches["venue"].astype("category").cat.codes
matches['opp_code']= matches["opponent"].astype("category").cat.codes
matches["hour"]=matches["time"].str.replace(":.+","",regex=True).astype("int")
matches["day_code"]=matches["date"].dt.dayofweek
matches["target"]=(matches["result"]=="W").astype("int")
rf= RandomForestClassifier(n_estimators=50,min_samples_split=10,random_state=1)
train=matches[matches["date"]<'2023-01-01']
test=matches[matches["date"]>'2023-01-01']
predictor=["venue_code","opp_code","hour","day_code"]
rf.fit(train[predictor],train["target"])
preds= rf.predict(test[predictor])
acc = accuracy_score(test["target"],preds)
compined=pd.DataFrame(dict(actual=test["target"],prediction=preds))
t=pd.crosstab(index=compined['actual'],columns=compined["prediction"])
matches["team"] = matches["team"].str.strip()
group_matches=matches.groupby("team")
precision=precision_score(test["target"],preds)
print(precision)
group=group_matches.get_group("Liverpool")
def rolling_averages(group,cols,new_cols):
    group=group.sort_values("date")
    rolling_stats= group[cols].rolling(3,closed='left').mean()
    group[new_cols]=rolling_stats
    group= group.dropna(subset=new_cols)
    return group

cols= ["gf","ga","sh","sot","dist","fk","pk","pkatt"]
new_cols = [f"{c}_rolling" for c in cols]
matches_rolling= matches.groupby("team").apply(lambda x: rolling_averages(x,cols,new_cols))
matches_rolling=matches_rolling.droplevel("team")
matches_rolling.index=range(matches_rolling.shape[0])

def make_prediction(data,predictor):
    train=data[data["date"]<'2023-01-01']
    test=data[data["date"]>'2023-01-01']
    predictor=["venue_code","opp_code","hour","day_code"]
    rf.fit(train[predictor],train["target"])
    preds= rf.predict(test[predictor])
    # acc = accuracy_score(test["target"],preds)
    compined=pd.DataFrame(dict(actual=test["target"],prediction=preds))
    precision=precision_score(test["target"],preds)
    # t=pd.crosstab(index=compined['actual'],columns=compined["prediction"])
    return compined,precision

compined, precision =make_prediction(matches_rolling,predictor+new_cols)
print(precision)
compined =compined.merge(matches_rolling[["date","team","opponent","result"]],left_index=True,right_index=True)
print(compined)
class MissingDict(dict):
    __missing__ = lambda self,key:key
mapvalues={
    "Brighton and Hove Albion":"Brighton",
    "Manchester United":"Manchester Utd",
    "Newcastle United":"Newcastle Utd",
    "Tottenham Hotspur":"Tottenham",
    "West Ham United":"West Ham",
    "Wolverhampton-Wanderers":"Wolves"
}
mapping=MissingDict(**mapvalues)
compined["new_team"]=compined["team"].map(mapping)
merged=compined.merge(compined,left_on=["date","new_team"],right_on=["date","opponent"])
# merged[(merged["predicted_x"]==1)&(merged["predicted_y"]==0)]["actual_x"].value_counts()

# print(s)
# print(matches_rolling)
# print(matches.shape)
# print(matches["team"].value_counts())
# liverpool_matches = matches[matches["team"].str.contains("Liverpool", case=False)]
# print("Liverpool Matches:")
# print(liverpool_matches)
