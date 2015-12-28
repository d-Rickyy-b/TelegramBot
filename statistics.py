__author__ = 'Rico'
from sql_handler import sql_insert, sql_getUser


def set_game_won(user_id):
    games_won = int(sql_getUser(user_id)[7]) + 1
    sql_insert("gamesWon", str(games_won), user_id)


def add_game_played(user_id):
    games_played = int(sql_getUser(user_id)[6]) + 1
    # last_played = int(sql_getUser(user_id)[9])
    sql_insert("gamesPlayed", str(games_played), user_id)
    # sql_insert("lastPlayed", str(last_played), user_id)
    # todo last played
