# -*- coding: utf-8 -*-
__author__ = 'Rico'
import sqlite3


# TODO connection als Parameter übergeben
# TODO funktionsnamen klein geschrieben

def sql_connect():
    connection = sqlite3.connect("users.db")
    connection.text_factory = lambda x: str(x, 'utf-8', "ignore")
    cursor = connection.cursor()
    cursor.execute("SELECT rowid, * FROM users")
    temp_list = [[]]*0

    result = cursor.fetchall()
    for r in result:
        temp_list.append(list(r))
    return temp_list


def sql_getUser(user_id):
    connection = sqlite3.connect("users.db")
    connection.text_factory = lambda x: str(x, 'utf-8', "ignore")
    cursor = connection.cursor()
    cursor.execute("SELECT rowid, * FROM users WHERE userID='" + str(user_id) + "';")

    result = cursor.fetchall()
    return result[0]


def sql_getAllUsers():
    connection = sqlite3.connect("users.db")
    connection.text_factory = lambda x: str(x, 'utf-8', "ignore")
    cursor = connection.cursor()
    cursor.execute("SELECT rowid, * FROM users;")

    return cursor.fetchall()


def sql_write(user_id, lang_id, first_name, last_name, username):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", (str(user_id), str(lang_id), str(first_name), str(last_name), str(username), "0", "0", "0", "0"))
    connection.commit()


# Um Werte zu ändern
def sql_insert(string_value, value, user_id):
    print("SQL_Insert: " + string_value + " | " + str(value) + " | " + str(user_id))
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET " + str(string_value) + "='" + str(value) + "' WHERE userID='" + str(user_id) + "';")
    connection.commit()


def check_if_user_saved(user_id):
    connection = sqlite3.connect("users.db")
    connection.text_factory = lambda x: str(x, 'utf-8', "ignore")
    cursor = connection.cursor()
    cursor.execute("SELECT rowid, * FROM users WHERE userID='" + str(user_id) + "';")

    result = cursor.fetchall()
    if len(result) > 0:
        return result[0]
    else:
        return -1


def get_playing_users(last_played):
    connection = sqlite3.connect("users.db")
    connection.text_factory = lambda x: str(x, 'utf-8', "ignore")
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE lastPlayed>='" + str(last_played) + "';")

    result = cursor.fetchall()
    return result[0]
