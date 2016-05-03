__author__ = 'Rico'
from time import time

from sql_handler import sql_insert


class Player(object):
    cardvalue = 0
    number_of_cards = 0
    has_ace = False

    def give_card(self, wert):
        self.cardvalue += wert
        self.number_of_cards += 1

    def give_ace(self):
        self.has_ace = True

    def __init__(self, user_id, first_name):
        sql_insert("lastPlayed", int(time()), user_id)
        self.number_of_cards = 0
        self.user_id = user_id
        self.first_name = first_name
        self.cardvalue = 0
