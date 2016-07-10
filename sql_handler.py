# -*- coding: utf-8 -*-
__author__ = 'Rico'
import sqlite3


def sql_get_db_connection():
    connection = sqlite3.connect("users.db")
    connection.text_factory = lambda x: str(x, 'utf-8', "ignore")
    return connection.cursor()


def sql_connect():
    cursor = sql_get_db_connection()
    cursor.execute("SELECT rowid, * FROM users")
    temp_list = [[]]*0

    result = cursor.fetchall()
    for r in result:
        temp_list.append(list(r))
    return temp_list


def sql_get_user(user_id):
    cursor = sql_get_db_connection()
    cursor.execute("SELECT rowid, * FROM users WHERE userID='" + str(user_id) + "';")

    result = cursor.fetchall()
    if len(result)>0:
        return result[0]
    else:
        return[]*0

def sql_get_all_users():
    cursor = sql_get_db_connection()
    cursor.execute("SELECT rowid, * FROM users;")
    return cursor.fetchall()


def sql_write(user_id, lang_id, first_name, last_name, username):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", (str(user_id), str(lang_id), str(first_name), str(last_name), str(username), "0", "0", "0", "0"))
    connection.commit()


def sql_insert(string_value, value, user_id):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET " + str(string_value) + "='" + str(value) + "' WHERE userID='" + str(user_id) + "';")
    connection.commit()


def check_if_user_saved(user_id):
    cursor = sql_get_db_connection()
    cursor.execute("SELECT rowid, * FROM users WHERE userID=?;",[str(user_id)])

    result = cursor.fetchall()
    if len(result) > 0:
        return result[0]
    else:
        return -1


def get_playing_users(last_played):
    cursor = sql_get_db_connection()
    cursor.execute("SELECT COUNT(*) FROM users WHERE lastPlayed>=?;", [str(last_played)])

    result = cursor.fetchone()
    return result[0]


def get_last_players_list():
    cursor = sql_get_db_connection()
    cursor.execute("SELECT * FROM users ORDER BY lastPlayed DESC LIMIT 10;")
    result = cursor.fetchall()

    return_text = ""

    for r in result:
        return_text += r[0] + " | " + r[2] + " | " + r[3] + " | @" + r[4] + " | Spiele: " + r[5] + " | Gew: " + r[6] + " (" + r[1] + ")\n"
    return return_text


def user_data_changed(user_id, first_name, last_name, username):
    cursor = sql_get_db_connection()
    cursor.execute("SELECT * FROM users WHERE userID='" + str(user_id) + "';")

    result = cursor.fetchone()
    print(result)
    if str(result[0][2]) == first_name and str(result[0][3]) == last_name and str(result[0][3]) == username:
        print("alles richtig")
        return False

    return True


def set_user_data(user_id, first_name, last_name, username):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET first_name='" + str(first_name) + "', last_name='" + str(last_name) + "', username='" + str(username) + "' WHERE userID='" + str(user_id) + "';")
    connection.commit()
