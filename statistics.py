__author__ = 'Rico'
from datetime import datetime

from sql_handler import sql_insert, sql_get_user


def set_game_won(user_id):
    games_won = int(sql_get_user(user_id)[7]) + 1
    sql_insert("gamesWon", str(games_won), user_id)


def add_game_played(user_id):
    games_played = int(sql_get_user(user_id)[6]) + 1
    sql_insert("gamesPlayed", str(games_played), user_id)


def get_stats(percentage):
    text = ""
    perc = int(percentage//10+1)
    for x in range(perc):
        text += "🏆"
    for x in range (10-perc):
        text += "🔴"
    return text


def get_user_stats(user_id):
    user = sql_get_user(user_id)
    played_games = 1
    if int(user[6]) > 0:
        played_games = user[6]
    statistics_string = "Here are your statistics  📊:\n\nPlayed Games: " + str(user[6]) + "\nWon Games : " + str(user[7]) + \
                        "\nLast Played: " + datetime.fromtimestamp(int(user[9])).strftime('%d.%m.%y %H:%M') + " CET" + \
                        "\n\n" + get_stats(round(float(user[7]) / float(played_games), 4) * 100) + "\n\nWinning rate: " + \
                        '{percent:.2%}'.format(percent=float(user[7]) / float(played_games))
    return statistics_string