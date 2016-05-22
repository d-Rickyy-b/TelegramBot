__author__ = 'Rico'
from time import time

from sql_handler import sql_insert


class Player(object):
    def give_card(self, value):
        self.cardvalue += value
        self.number_of_cards += 1

    def give_ace(self):
        self.has_ace = True

    def __init__(self, user_id, first_name):
        sql_insert("lastPlayed", int(time()), user_id)
        self.number_of_cards = 0
        self.user_id = user_id
        self.first_name = first_name
        self.cardvalue = 0
        self.has_ace = False
        # self.cards = []*0 # TODO might be added in the future
