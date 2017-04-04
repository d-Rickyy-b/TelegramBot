__author__ = 'Rico'
from time import time

from database.db_wrapper import DBwrapper


class Player(object):
    def give_card(self, card, value):
        self.cards.append(card)
        self.cardvalue += value
        self.number_of_cards += 1

    def give_ace(self):
        self.has_ace = True

    def has21(self):
        return self.cardvalue == 21

    def has_busted(self):
        return self.cardvalue > 21

    def get_cards_string(self):
        cards_string = ""
        for i, card in enumerate(self.cards):
            cards_string += self.deck.get_card_name(card)
            if i+1 < len(self.cards):
                cards_string += ", "
        return cards_string

    def get_first_name(self):
        return self.first_name

    def get_cardvalue(self):
        return self.cardvalue

    def get_userid(self):
        return self.user_id

    def __init__(self, user_id, first_name, deck):
        db = DBwrapper.get_instance()
        db.insert("lastPlayed", int(time()), user_id)
        self.number_of_cards = 0
        self.user_id = user_id
        self.first_name = first_name
        self.cardvalue = 0
        self.has_ace = False
        self.cards = []
        self.deck = deck
