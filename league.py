import random
import pandas as pd
import imgkit
import datetime as dt
import data, twitter

INITIAL_DATE = dt.datetime(2020, 4, 14, 14, 0, 0)
# INITIAL_DATE = dt.datetime.now()

# CREATE THE TEAMS DAFRAME
def initialize_teams():
    teams = pd.DataFrame(index=data.TEAMS, columns=["Escudo", "Twitter", "Pts", "J", "V", "E", "D", "GP", "GC", "S"])
    teams["Escudo"] = data.CRESTS
    teams["Twitter"] = data.TWITTERS
    teams.iloc[:, 2:7] = 0
    return teams


# CREATE THE FIXTURES DATAFRAME
def initialize_fixtures():
    fixtures = pd.DataFrame(columns = ["Matchday", "Local", "HScore", "AScore", "Visitante", "Result"])
    fixtures["Matchday"] = data.MATCHDAYS
    fixtures["Local"] = data.HOME
    fixtures["Visitante"] = data.AWAY
    fixtures.iloc[:, 2:4] = 0
    return fixtures


# SIMULATES A MATCH
def match(home, away):
    home_score = random.choice(data.HOME_SCORES)
    away_score = random.choice(data.AWAY_SCORES)
    return home_score, away_score


# ADD ALL MATCHES RESULTS TO THE FIXTURES DATAFRAME
def initialize_scores(fixtures):
    home_goals = []
    away_goals = []
    results = []
    for i, row in fixtures.iterrows():
        h, a = match(row["Local"], row["Visitante"])
        home_goals.append(h)
        away_goals.append(a)
        if h > a:
            results.append("h")
        elif a > h:
            results.append("a")
        else:
            results.append("d")
    fixtures["HScore"] = home_goals
    fixtures["AScore"] = away_goals
    fixtures["Result"] = results
    return fixtures


# GENERATE A PNG IMAGE OF THE STANDINGS
def generate_standing_image(standing, matchday_number):
    file = open("standings/{}.html".format(matchday_number), "w")
    file.write('<meta charset="UTF-{}">\n'.format(8))
    file.write(data.CSS)
    file.write(standing.to_html(index=True))
    file.close()
    options = {'format': 'jpg', 'width': 420, 'disable-smart-width': ''}
    imgkit.from_file('standings/{}.html'.format(matchday_number), 'standings/{}.jpg'.format(matchday_number), options=options)
    return 'standings/{}.jpg'.format(matchday_number)


# CALCULATE THE STANDINGS FOR A ROUND AND CREATE A PNG FILE
def generate_standings(matchday_number, teams):
    for i, row in teams.iterrows():
        home_games = fixtures[(fixtures["Matchday"] <= matchday_number) & (fixtures["Local"] == i)]
        away_games = fixtures[(fixtures["Matchday"] <= matchday_number) & (fixtures["Visitante"] == i)]
        row["V"] = (home_games["Result"] == "h").sum() + (away_games["Result"] == "a").sum()
        row["E"] = (home_games["Result"] == "d").sum() + (away_games["Result"] == "d").sum()
        row["D"] = (home_games["Result"] == "a").sum() + (away_games["Result"] == "h").sum()
        row["GP"] = home_games["HScore"].sum() + away_games["AScore"].sum()
        row["GC"] = home_games["AScore"].sum() + away_games["HScore"].sum()
        row["Pts"] = row["V"]*3 + row["E"]
        row["S"] = row["GP"] - row["GC"]
        row["J"] = row["V"] + row["E"] + row["D"]
    teams =  teams.sort_values(["Pts", "V", "S", "GP"], ascending=False)
    standing = teams.drop(["Escudo", "Twitter"], axis=1)
    standing_img = generate_standing_image(standing, matchday_number)
    standing_msg = "Classificação:"
    return standing_msg, standing_img


# GENERATE A PNG FILE OF A MATCH
def generate_match_score_img(teams, match, matchday, match_number):
    with open("scores/{}-{}.html".format(match["Local"], match["Visitante"]), "w") as file:
        file.write('<meta charset="UTF-8">\n')
        file.write(data.SCORE_HTML.format(round=matchday, game=match_number, home_src="../{}".format(teams.loc[match["Local"]]["Escudo"]), away_src="../{}".format(teams.loc[match["Visitante"]]["Escudo"]), home_score=match["HScore"], away_score=match["AScore"], home_team=match["Local"], away_team=match["Visitante"], home_twitter=teams.loc[match["Local"]]["Twitter"], away_twitter=teams.loc[match["Visitante"]]["Twitter"]))
        file.close()
    options = {'format': 'jpg', 'width': 1440, 'disable-smart-width': ''}
    imgkit.from_file("scores/{}-{}.html".format(match["Local"], match["Visitante"]), "scores/{}-{}.jpg".format(match["Local"], match["Visitante"]), options=options)
    return "scores/{}-{}.jpg".format(match["Local"], match["Visitante"])


# GENERATE AND TWEET THE SCORE OF A MATCH
def generate_match_score(teams, match, matchday, match_number):
    match_score_msg = ""
    match_score_msg += "Rodada {} - Jogo {}\n\n".format(matchday, match_number)
    match_score_msg += "{} {} - {} {}".format(teams.loc[match["Local"]]["Twitter"], match["HScore"], match["AScore"], teams.loc[match["Visitante"]]["Twitter"])
    match_score_img = generate_match_score_img(teams, match, matchday, match_number)
    return match_score_msg, match_score_img


# GENERATE A PNG FILE OF THE NEXT MATCH
def generate_next_match_score_img(teams, next_match, matchday, next_match_number):
    with open("next-match/{}-{}.html".format(next_match["Local"], next_match["Visitante"]), "w") as file:
        file.write('<meta charset="UTF-8">\n')
        file.write(data.NEXT_MATCH_HTML.format(round=matchday, game=next_match_number, home_src="../{}".format(teams.loc[next_match["Local"]]["Escudo"]), away_src="../{}".format(teams.loc[next_match["Visitante"]]["Escudo"]), home_team=next_match["Local"], away_team=next_match["Visitante"], home_twitter=teams.loc[next_match["Local"]]["Twitter"], away_twitter=teams.loc[next_match["Visitante"]]["Twitter"]))
        file.close()
    options = {'format': 'jpg', 'width': 1440, 'disable-smart-width': ''}
    imgkit.from_file("next-match/{}-{}.html".format(next_match["Local"], next_match["Visitante"]), "next-match/{}-{}.jpg".format(next_match["Local"], next_match["Visitante"]), options=options)
    return "next-match/{}-{}.jpg".format(next_match["Local"], next_match["Visitante"])


# GENERATE AND TWEET THE NEXT MATCH
def generate_next_match(teams, next_match, matchday, next_match_number):
    next_match_msg = ""
    next_match_msg += "Próximo Jogo\n\n"
    next_match_msg += "{} - {}".format(teams.loc[next_match["Local"]]["Twitter"], teams.loc[next_match["Visitante"]]["Twitter"])
    next_match_img = generate_next_match_score_img(teams, next_match, matchday, next_match_number)
    return next_match_msg, next_match_img


# GENERATE THE IMAGE OF THE NEXT MATCHDAY
def generate_next_matchday_img(next_matchday, next_matchday_number):
    file = open("next-matchday/{}.html".format(next_matchday_number), "w")
    file.write('<meta charset="UTF-{}">\n'.format(8))
    file.write(data.CSS)
    file.write(next_matchday.to_html(index=False))
    file.close()
    options = {'format': 'jpg', 'width': 420, 'disable-smart-width': ''}
    imgkit.from_file('next-matchday/{}.html'.format(next_matchday_number), 'next-matchday/{}.jpg'.format(next_matchday_number), options=options)
    return 'next-matchday/{}.jpg'.format(next_matchday_number)


# GENERATE AND TWEET THE NEXT MATCHDAY
def generate_next_matchday(teams, next_matchday, next_matchday_number):
    next_matchday_msg = "Próxima Rodada:"
    next_matchday["X"] = "X"
    next_matchday = next_matchday[["Local", "X", "Visitante"]]
    next_matchday_img = generate_next_matchday_img(next_matchday, next_matchday_number)
    return next_matchday_msg, next_matchday_img


# SIMULATES THE LEAGUE
def generate_messages(fixtures, teams):
    tweets = pd.DataFrame(columns=["type", "msg", "img", "datetime", "sent"])
    for i in range(38):
        matchday = fixtures.loc[fixtures["Matchday"] == i+1, ["Local", "HScore", "AScore", "Visitante"]]
        for j in range(10):
            match = matchday.iloc[j]
            match_score_msg, match_score_img = generate_match_score(teams, match, i+1, j+1)
            tweets = tweets.append({"type": "sc", "msg": match_score_msg, "img": match_score_img, "datetime": (INITIAL_DATE + dt.timedelta(days=i, hours=j)), "sent": False}, ignore_index=True)
            if j < 9:
                next_match = matchday.iloc[j+1]
                next_match_msg, next_match_img = generate_next_match(teams, next_match, i+1, j+2)
                tweets = tweets.append({"type": "nm", "msg": next_match_msg, "img": next_match_img, "datetime": (INITIAL_DATE + dt.timedelta(days=i, hours=j, minutes=5)), "sent": False}, ignore_index=True)
        standing_msg, standing_img = generate_standings(i+1, teams)
        tweets = tweets.append({"type": "st", "msg": standing_msg, "img": standing_img, "datetime": (INITIAL_DATE + dt.timedelta(days=i, hours=9, minutes=5)), "sent": False}, ignore_index=True)
        if i < 37:
            next_matchday = fixtures.loc[fixtures["Matchday"] == i+2, ["Local", "Visitante"]]
            next_matchday_msg, next_matchday_img = generate_next_matchday(teams, next_matchday, i+2)
            tweets = tweets.append({"type": "nmd", "msg": next_matchday_msg, "img": next_matchday_img, "datetime": (INITIAL_DATE + dt.timedelta(days=i, hours=9, minutes=10)), "sent": False}, ignore_index=True)
    return tweets


if __name__ == "__main__":
    teams = initialize_teams()
    fixtures = initialize_fixtures()
    fixtures = initialize_scores(fixtures)
    tweets = generate_messages(fixtures, teams)
    tweets.to_csv("schedule.csv", index=False)
