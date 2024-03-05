import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

years = list(range(2024, 2021, -1))
all_matches = []
standings_url = "https://fbref.com/en/comps/9/premier-league-stats"

for year in years:
    data = requests.get(standings_url)
    soup = BeautifulSoup(data.text, 'html.parser')
    standings_table = soup.select('table.stats_table')[0]
    links = [l.get("href") for l in standings_table.find_all('a')]
    links = [l for l in links if '/squads/' in l]
    team_urls = [f"https://fbref.com{l}" for l in links]
    
    previous_season = soup.select("a.prev")[0].get("href")
    standings_url = f"https://fbref.com{previous_season}"
    
    for team_url in team_urls:
        team_name = team_url.split("/")[-1].replace("-Stats", " ")
        team_data = []
        
        data_team = requests.get(team_url)
        matches = pd.read_html(data_team.text, match="Scores & Fixtures")[0]
        soup_team = BeautifulSoup(data_team.text, 'html.parser')
        links_team = [l.get("href") for l in soup_team.find_all('a')]
        links_team = [l for l in links_team if l and 'all_comps/shooting/' in l]
        
        if not links_team:  # Check if links list is empty
            continue
            
        data_shooting = requests.get(f"https://fbref.com{links_team[0]}")
        shooting = pd.read_html(data_shooting.text, match="Shooting")[0]
        shooting.columns = shooting.columns.droplevel()
        
        try:
            team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")
        except ValueError:
            continue
            
        team_data = team_data[team_data["Comp"] == "Premier League"]
        team_data["Season"] = year
        team_data["Team"] = team_name
        all_matches.append(team_data)
        time.sleep(10)
    
match_df = pd.concat(all_matches)
match_df.columns = [c.lower() for c in match_df.columns]
match_df.to_csv("premier_league_matches.csv", index=False)  # Specify the file path here
