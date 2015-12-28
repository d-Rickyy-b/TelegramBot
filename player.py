__author__ = 'Rico'
from sql_handler import sql_insert
from time import time


class player(object):

    kartenwert = 0
    aktuellekarte = 0
    anzahl_karten = 0
    has_ace = False

    def give_player_card(self, wert):
        self.kartenwert += wert
        self.anzahl_karten += 1

    def give_ace(self):
        self.has_ace = True

    def __init__(self, user_id, first_name):
        sql_insert("lastPlayed", int(time()), user_id)
        self.anzahl_karten = 0
        self.user_id = user_id
        self.name = first_name
