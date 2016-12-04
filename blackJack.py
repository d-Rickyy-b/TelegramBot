# -*- coding: utf-8 -*-
__author__ = 'Rico'
import datetime
import time

from cardDeck import CardDeck
from messageSenderAdapter import MessageSenderAdapter
from player import Player
from dealer import Dealer
from sql_handler import sql_insert
from statistics import add_game_played, set_game_won


class BlackJack(object):
    GROUP_CHAT = 1
    PRIVATE_CHAT = 0
    keyboard_language = [
        ["Deutsch 🇩🇪", "English 🇺🇸"],
        ["Português 🇧🇷", "Русский 🇷🇺", "Nederlands 🇳🇱"],
        ["Esperanto 🌍", "Español 🇪🇸"]]

    game_running = False

    current_player = 0

    # Adds Player to the Game
    def add_player(self, user_id, first_name, message_id, silent=None):
        if not self.game_running:
            self.players.append(Player(user_id, first_name, self.deck))
            self.join_message_ids.append(message_id)
            if silent is None:
                self.message_adapter.send_new_message(self.chat_id, self.translate("playerJoined").format(first_name), message_id=message_id)

    def get_index_by_user_id(self, user_id):
        i = 0
        for user in self.players:
            if user.user_id == user_id:
                return i
            i += 1
        return -1

    def get_user_by_user_id(self, user_id):
        for user in self.players:
            if user.get_userid() == user_id:
                return user

        return None

    def next_player(self):
        if (self.current_player + 1) < len(self.players):
            self.current_player += 1
            self.message_adapter.send_new_message(self.chat_id, self.translate("overview") + "\n\n" + self.get_player_overview(show_points=True) + "\n" +
                                                  self.translate("nextPlayer").format(self.players[self.current_player].first_name), message_id=self.join_message_ids[self.current_player],
                                                  keyboard=self.keyboard_running)
            self.players_first_turn()
        else:
            self.current_player = -1
            self.dealers_turn()

        # ---------------------------------- give Player one -----------------------------------------#

    # gives player one card
    def give_player_one(self):
        card = self.deck.pick_one_card()
        cardvalue = self.deck.get_card_value(card)
        player_index = self.current_player
        user = self.players[player_index]

        if self.game_type == self.PRIVATE_CHAT:
            player_drew = self.translate("playerDraws1").format(str(self.deck.get_card_name(card)))
        else:
            player_drew = self.translate("playerDrew").format(user.first_name, str(self.deck.get_card_name(card)))

        self.message_adapter.set_metadata(keyboard=self.keyboard_running)
        self.message_adapter.add_to_message(player_drew)

        if (user.cardvalue + cardvalue) > 21 and user.has_ace is True:
            self.message_adapter.add_to_message("\n" + self.translate("softHandLater") + "\n")
            user.has_ace = False
            user.cardvalue -= 10

        if cardvalue == 1 and user.cardvalue > 10:
            self.message_adapter.add_to_message("\n" + self.translate("softHand") + "\n")
        elif cardvalue == 1 and user.cardvalue <= 10:
            cardvalue = 11
            user.give_ace()
            self.message_adapter.add_to_message("\n" + self.translate("hardHand") + "\n")

        user.give_card(card, cardvalue)
        self.message_adapter.add_to_message("\n" + self.translate("cardvalue").format(str(user.cardvalue)))

        if user.cardvalue < 21:
            self.message_adapter.send_joined_message()
        else:
            if user.has21():
                self.message_adapter.add_to_message("\n\n" + user.first_name + " " + self.translate("got21"))
            elif user.has_busted():
                if self.game_type == self.GROUP_CHAT:
                    self.message_adapter.add_to_message("\n\n" + self.translate("playerBusted").format(user.first_name))

            self.message_adapter.send_joined_message()
            self.next_player()

    def players_first_turn(self):
        player_index = self.current_player
        user = self.players[player_index]
        # ziehe 2 Karten
        for i in range(2):
            card = self.deck.pick_one_card()
            cardvalue = self.deck.get_card_value(card)

            if cardvalue == 1 and user.cardvalue <= 10:
                cardvalue = 11
                user.give_ace()

            user.give_card(card, cardvalue)
            # addiere Karten zu Kartenwert

        # TODO prüfe ob Wert = 21 -> BlackJack
        # TODO wenn nicht, ist Wert > 21 (zwei Asse?)
        # Nachricht schicken
        cards_string = user.get_cards_string()
        self.message_adapter.send_new_message(self.chat_id, str(self.translate("yourCardsAre")).format(user.first_name, "\n" + cards_string + "\n", str(user.cardvalue)))

    # Gives the dealer cards
    def dealers_turn(self, i=0):
        output_text = self.translate("croupierDrew") + "\n\n"
        while self.dealer.get_cardvalue() <= 16:
            card = self.deck.pick_one_card()
            cardvalue = self.deck.get_card_value(card)
            self.dealer.give_card(card, cardvalue)

        for card in self.dealer.cards:
            if i == 0:
                output_text += self.deck.get_card_name(card)
            else:
                output_text += " , " + self.deck.get_card_name(card)
            i += 1

        output_text += "\n\n" + self.translate("cardvalueDealer") + " " + str(self.dealer.get_cardvalue())
        self.message_adapter.send_new_message(self.chat_id, output_text)
        self.evaluation()

    def dealers_first_turn(self):
        card = self.deck.pick_one_card()
        cardvalue = self.deck.get_card_value(card)
        self.dealer.give_card(cardvalue, cardvalue)
        text = ""

        if self.game_type == self.PRIVATE_CHAT:
            text += self.translate("gameBegins") + "\n"

        text += "\n*" + self.translate("dealersCards") + "*\n\n" + self.deck.get_card_name(card) + ", | -- |"
        self.message_adapter.add_to_message(text)
        self.message_adapter.set_metadata(parse_mode="Markdown")
        self.message_adapter.send_joined_message()

    # Only in multiplayer
    def start_game(self, message_id):
        self.game_running = True
        self.message_adapter.set_metadata(keyboard=self.keyboard_running, message_id=message_id)
        self.message_adapter.add_to_message(self.translate("gameBegins") + "\n" + self.translate("gameBegins2") + "\n\n" + self.get_player_overview())
        self.dealers_first_turn()
        for p in self.players:
            add_game_played(p.user_id)
        self.players_first_turn()

        # ---------------------------------- Auswertung -----------------------------------------#

    def evaluation(self):
        list_21 = []
        list_busted = []
        list_lower_21 = []

        for user in self.players:
            cv = user.get_cardvalue()

            if cv > 21:
                list_busted.append(user)
            elif cv == 21:
                list_21.append(user)
            elif cv < 21:
                list_lower_21.append(user)

        if self.dealer.get_cardvalue() > 21:
            list_busted.append(self.dealer)
        elif self.dealer.get_cardvalue() == 21:
            list_21.append(self.dealer)
        elif self.dealer.get_cardvalue() < 21:
            list_lower_21.append(self.dealer)

        list_21 = sorted(list_21, key=lambda x: x.get_cardvalue(), reverse=True)
        list_lower_21 = sorted(list_lower_21, key=lambda x: x.get_cardvalue(), reverse=True)
        list_busted = sorted(list_busted, key=lambda x: x.get_cardvalue(), reverse=True)

        if self.dealer.get_cardvalue() > 21:
            for user in list_21:
                set_game_won(user.get_userid())
            for user in list_lower_21:
                set_game_won(user.get_userid())
            # Alle mit 21 > Punkte >= 0 haben Einsatz x 1,5 gewonnen.
            # Alle mit 21 haben Einsatz mal 2 gewonnen
            # Alle mit 21 und Kartenanzahl = 2 haben Einsatz mal 3 gewonnen
        elif self.dealer.get_cardvalue() == 21:  # todo unterscheidung zwischen blackjack und 21
            for user in list_21:
                if user.get_first_name() != self.translate("dealerName"):
                    set_game_won(user.get_userid())
                    # Alle mit 21 > Punkte >= 0 haben verloren . || Alle mit 21 haben Einsatz gewonnen || Alle mit 21 und Kartenanzahl = 2 haben Einsatz mal 2 gewonnen
                    # todo wenn Dealer Blackjack hat: || Alle mit BlackJack haben Einsatz gewonnen. || Alle anderen haben verloren
        elif self.dealer.get_cardvalue() < 21:
            for user in list_21:
                set_game_won(user.get_userid())
            for user in list_lower_21:
                if user.get_cardvalue() > self.dealer.get_cardvalue():
                    set_game_won(user.get_userid())
                    # print(str(user.get_userid()) + " you've got " + )
                    # Alle mit Dealer > Punkte haben verloren.
                    # Alle mit Dealer = Punkte erhalten Einsatz
                    # Alle mit 21 > Punkte > Dealer haben Einsatz x 1,5 gewonnen.
                    # Alle mit 21 haben Einsatz mal 2 gewonnen
                    # Alle mit 21 und Kartenanzahl = 2 haben Einsatz mal 3 gewonnen
                    # 7er Drilling 3/2 Gewinn (Einsatz x 1,5)

        final_message = self.translate("playerWith21") + "\n"
        for user in list_21:
            final_message += str(user.get_cardvalue()) + " - " + user.get_first_name() + "\n"

        final_message += "\n" + self.translate("playerLess21") + "\n"
        for user in list_lower_21:
            final_message += str(user.get_cardvalue()) + " - " + user.get_first_name() + "\n"

        final_message += "\n" + self.translate("playerOver21") + "\n"
        for user in list_busted:
            final_message += str(user.get_cardvalue()) + " - " + user.get_first_name() + "\n"

        self.message_adapter.send_new_message(self.chat_id, final_message)
        self.game_handler_object.gl_remove(self.chat_id)

    # ---------------------------------- Get Player overview -----------------------------------------#

    def get_player_overview(self, show_points=False, text="", i=0, dealer=False):
        for user in self.players:
            if i == self.current_player:
                text += "▶️"
            else:
                text += "👤"
            if show_points is True and (i < self.current_player or self.current_player == -1):
                text += (user.first_name + " - [" + str(self.players[i].cardvalue) + "]\n")
            else:
                text += (user.first_name + "\n")
            i += 1
        if dealer is True:
            text += ("🎩" + self.translate("dealerName") + " - [" + str(self.dealer.get_cardvalue()) + "]")
        return text

    # ---------------------------------- Change Language -----------------------------------------#

    def change_language(self, lang_id, message_id, user_id):
        self.message_adapter.send_new_message(self.chat_id, self.translate("langChanged"),
                                              keyboard=[[self.translate("keyboardItemOneMore"), self.translate("keyboardItemNoMore")], [self.translate("keyboardItemStart")]],
                                              message_id=message_id)
        sql_insert("languageID", lang_id, user_id)
        self.lang_id = lang_id

        self.keyboard_running = [[self.translate("keyboardItemOneMore"), self.translate("keyboardItemNoMore")], [self.translate("keyboardItemStop")]]
        self.keyboard_not_running = [[self.translate("keyboardItemStart")]]


    # ---------------------------------- Analyzing -----------------------------------------#

    # Messages are analyzed here. Most function calls come from here
    def analyze_message(self, command, user_id, first_name, message_id):
        command = str(command)
        print("analyze_message - " + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        if command.startswith("start") or command.startswith(self.translate("startCmd")):
            if self.game_type == self.GROUP_CHAT:
                if len(self.players) >= 1:  # todo >=2 # when there are enough players
                    if self.game_running is False:  # If the game isn't running yet
                        if user_id == self.players[0].user_id:  # Only start game when the creator sends the start command
                            self.start_game(message_id)
                        else:
                            self.message_adapter.send_new_message(self.chat_id, self.translate("onlyGameCreator"), message_id=message_id)
                    else:
                        self.message_adapter.send_new_message(self.chat_id, self.translate("alreadyAGame"), keyboard=self.keyboard_running, message_id=message_id)
                else:
                    self.message_adapter.send_new_message(self.chat_id, self.translate("notEnoughPlayers"), message_id=message_id)
            else:  # When game is singleplayer
                self.message_adapter.send_new_message(self.chat_id, self.translate("alreadyAGame"), keyboard=self.keyboard_running, message_id=message_id)

        elif str(command).startswith(self.translate("onemore")):
            if self.game_running is True:
                if user_id == self.players[self.current_player].user_id:
                    self.give_player_one()
                else:
                    self.message_adapter.send_new_message(self.chat_id, self.translate("notYourTurn").format(first_name), message_id=message_id)
            else:
                self.message_adapter.send_new_message(self.chat_id, self.translate("noGame"), message_id=message_id)

        elif command.startswith(self.translate("nomore")):
            if user_id == self.players[self.current_player].user_id:
                self.next_player()

        elif self.game_type == self.GROUP_CHAT and command.startswith(self.translate("join")):
            # todo one time keyboard
            if self.get_index_by_user_id(user_id) == -1:
                self.add_player(user_id, first_name, message_id)
            else:
                self.message_adapter.send_new_message(self.chat_id, self.translate("alreadyJoined").format(first_name), message_id=message_id)

            if len(self.players) == 5:
                self.start_game(message_id)

        elif command.startswith("stop") or command.startswith(self.translate("stopCmd")):
            if user_id == self.players[0].user_id:
                self.game_handler_object.gl_remove(self.chat_id)

        elif command.startswith("hide"):
            self.message_adapter.hide_keyboard(self.chat_id)
        else:
            print("No matches!")

    # When game is being initialized
    def __init__(self, chat_id, user_id, lang_id, game_type, first_name, gamehandler, message_id, bot):
        from language import translation
        print("BlackJack_init - " + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        self.game_handler_object = gamehandler
        self.message_adapter = MessageSenderAdapter(bot, chat_id)
        self.chat_id = chat_id
        self.players = []
        self.join_message_ids = []
        self.card_list_dealer = []
        self.lang_id = lang_id
        self.deck = CardDeck(lang_id)
        translate = lambda string: translation(string, lang_id)
        self.translate = translate
        self.value_str = [translate("ace"), "2", "3", "4", "5", "6", "7", "8", "9", "10",
                          translate("jack"), translate("queen"), translate("king")]

        self.keyboard_running = [[translate("keyboardItemOneMore"), translate("keyboardItemNoMore")], [translate("keyboardItemStop")]]
        self.keyboard_not_running = [[translate("keyboardItemStart")]]

        # Add creator of the game to the "players" list
        self.add_player(user_id, first_name, message_id, silent=True)
        self.game_type = int(game_type)

        self.dealer = Dealer(self.translate("dealerName"), self.deck)

        if self.game_type == self.PRIVATE_CHAT:
            self.game_running = True
            add_game_played(user_id)
            self.message_adapter.set_metadata(keyboard=self.keyboard_running, message_id=message_id)
            self.dealers_first_turn()
            self.players_first_turn()
        else:
            self.message_adapter.send_new_message(chat_id, translate("newRound"), message_id=message_id, keyboard=self.keyboard_not_running)

    # When game is being ended - single and multiplayer
    def __del__(self):
        self.message_adapter.hide_keyboard(self.chat_id, self.translate("gameEnded"))
