# -*- coding: utf-8 -*-
__author__ = 'Rico'
import datetime
import time

from player import player
from messageSender import hide_keyboard
from language import translation
from statistics import add_game_played, set_game_won
from sql_handler import sql_insert
from messageSenderAdapter import messageSenderAdapter


class blackJack(object):
    symbole = ["♥", "♦", "♣", "♠"]
    werteInt = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
    keyboard_language = [
        ["Deutsch 🇩🇪", "English 🇺🇸"],
        ["Português 🇧🇷", "Nederlands 🇳🇱"]]

    game_running = False
    anzahl_karten_dealer = 0
    players = []*0
    join_ids = []*0
    stapel = []
    game_type = 0  # 0 ist für normale Chats, 1 für Gruppen
    current_player = 0

    # Adds Player to the Game
    def add_player(self, user_id, first_name, message_id, silent=None):
        if not self.game_running:
            self.players.append(player(user_id, first_name))
            self.join_ids.append(message_id)
            if silent is None:
                self.message_adapter.sendmessage(self.chat_id, translation("playerJoined", self.lang_id).format(first_name), self.bot,
                                                 message_id=message_id)  # , keyboard=self.keyboard_not_running # removed

    def get_index_by_user_id(self, user_id):
        i = 0
        for user in self.players:
            if user.user_id == user_id:
                return i
            i += 1
        return -1

    def next_player(self):
        if (self.current_player + 1) < len(self.players):
            self.current_player += 1
            self.message_adapter.sendmessage(self.chat_id, translation("overview", self.lang_id) + "\n\n" +
                        self.get_player_overview(show_points=True) + "\n" +
                        translation("nextPlayer", self.lang_id).format(self.players[self.current_player].name), self.bot, message_id=self.join_ids[self.current_player], keyboard=self.keyboard_running)
        else:
            self.current_player = -1
            self.dealers_turn()

# ---------------------------------- give player one -----------------------------------------#

    # Gibt dem Spieler eine Karte
    def give_player_one(self, first_name):
        card = self.stapel[0]
        self.stapel.pop(0)
        cardvalue = self.werteInt[card % 13]
        p_index = self.current_player
        user = self.players[p_index]

        if self.game_type == "0":
            sp_mp_text = translation("playerDraws1", self.lang_id).format(str(self.get_card_name(card)))
        else:
            sp_mp_text = translation("playerDrew", self.lang_id).format(first_name, str(self.get_card_name(card)))

        self.message_adapter.set_metadata(keyboard=self.keyboard_running)
        self.message_adapter.add_to_message(sp_mp_text)

        if (user.cardvalue + cardvalue) > 21 and user.has_ace is True:
            self.message_adapter.add_to_message("\n" + translation("softHandLater", self.lang_id) + "\n")
            user.has_ace = False
            user.cardvalue -= 10

        if cardvalue == 1 and user.cardvalue > 10:
            self.message_adapter.add_to_message("\n" + translation("softHand", self.lang_id) + "\n")
        elif cardvalue == 1 and user.cardvalue <= 10:
            cardvalue = 11
            user.give_ace()
            self.message_adapter.add_to_message("\n" + translation("hardHand", self.lang_id) + "\n")

        user.give_card(cardvalue)
        self.message_adapter.add_to_message("\n" + translation("cardvalue", self.lang_id).format(str(user.cardvalue)))

        if user.cardvalue == 21:
            self.message_adapter.add_to_message("\n\n" + first_name + " " + translation("got21", self.lang_id))
            self.message_adapter.send_joined_message()
            self.next_player()
        elif user.cardvalue > 21:
            if self.game_type == "1":
                self.message_adapter.add_to_message("\n\n" + translation("playerBusted", self.lang_id).format(user.name))
            self.message_adapter.send_joined_message()
            self.next_player()

        self.message_adapter.send_joined_message()

    # Gibt dem Dealer eine Karte
    def dealers_turn(self, i=0):
        output_text = translation("croupierDrew", self.lang_id) + "\n\n"
        while self.kartenwert_dealer <= 16:
            karte = self.stapel[0]
            self.kartenwert_dealer += self.werteInt[karte % 13]
            self.stapel.pop(0)
            self.anzahl_karten_dealer += 1
            self.karten_list_dealer.append(karte)

        print(self.anzahl_karten_dealer)
        for card in self.karten_list_dealer:
            if i == 0:
                output_text += self.get_card_name(card)
            else:
                output_text += " , " + self.get_card_name(card)
            i += 1

        output_text += "\n\n" + translation("cardvalueDealer", self.lang_id) + " " + str(self.kartenwert_dealer)
        self.message_adapter.sendmessage(self.chat_id, output_text, self.bot)
        self.auswertung(self.lang_id)

    def dealers_first_turn(self):
        karte = self.stapel[0]
        self.kartenwert_dealer += self.werteInt[karte % 13]
        self.stapel.pop(0)
        self.anzahl_karten_dealer += 1
        self.karten_list_dealer.append(karte)
        text = ""

        if self.game_type=="0":
            text += translation("gameBegins", self.lang_id) + "\n"

        text += "\n*" + translation("dealersCards", self.lang_id) + "*\n\n" + self.get_card_name(karte) + ", | -- |"  # Todo take from language file
        self.message_adapter.add_to_message(text)
        self.message_adapter.send_joined_message()
        #sendmessage(self.chat_id, text, self.bot, keyboard=self.keyboard_running) #game starts now

    # Erstellt einen Stapel
    def create_stapel(self):
        from random import shuffle
        stapel = list(range(1, 52))
        shuffle(stapel)
        self.stapel = stapel[:]

    def get_card_name(self, karte):
        symbol = self.symbole[karte//13]
        wert = self.value_str[karte % 13]
        string = "|"+symbol+" "+wert+"|"
        return string

    #Only in multiplayer
    def start_game(self, message_id):
        self.game_running = True
        # sendmessage(self.chat_id, translation("gameBegins", self.lang_id) + "\n" +
        #            translation("gameBegins2", self.lang_id) + "\n\n" + self.get_player_overview(), self.bot,
        #            keyboard=self.keyboard_running, message_id=message_id)
        self.message_adapter.set_metadata(keyboard=self.keyboard_running, message_id=message_id)
        self.message_adapter.add_to_message(translation("gameBegins", self.lang_id) + "\n" + translation("gameBegins2", self.lang_id) + "\n\n" + self.get_player_overview())
        self.dealers_first_turn()
        for p in self.players:
            add_game_played(p.user_id)

# ---------------------------------- Auswertung -----------------------------------------#

    def auswertung(self, lang_id):
        list_21 = [[]]*0
        list_busted = [[]]*0
        list_lower_21 = [[]]*0

        for user in self.players:
            tmplist = []*0
            kw = user.cardvalue
            tmplist.extend((kw, user.name, user.number_of_cards, user.user_id))
            if kw > 21:
                list_busted.append(tmplist)
            elif kw == 21:
                list_21.append(tmplist)
            elif kw < 21:
                list_lower_21.append(tmplist)

        if self.kartenwert_dealer > 21:
            list_busted.append([self.kartenwert_dealer, translation("dealerName", self.lang_id), self.anzahl_karten_dealer])
        elif self.kartenwert_dealer == 21:
            list_21.append([self.kartenwert_dealer, translation("dealerName", self.lang_id), self.anzahl_karten_dealer])
        elif self.kartenwert_dealer < 21:
            list_lower_21.append([self.kartenwert_dealer, translation("dealerName", self.lang_id), self.anzahl_karten_dealer])

        list_21 = sorted(list_21, key=lambda x: x[0], reverse=True)
        list_lower_21 = sorted(list_lower_21, key=lambda x: x[0], reverse=True)
        list_busted = sorted(list_busted, key=lambda x: x[0], reverse=True)

        if self.kartenwert_dealer > 21:
            for user in list_21:
                set_game_won(user[3])
            for user in list_lower_21:
                set_game_won(user[3])
            # Alle mit 21 > Punkte >= 0 haben Einsatz x 1,5 gewonnen.
            # Alle mit 21 haben Einsatz mal 2 gewonnen
            # Alle mit 21 und Kartenanzahl = 2 haben Einsatz mal 3 gewonnen
        elif self.kartenwert_dealer == 21:  # todo unterscheidung zwischen blackjack und 21
            for user in list_21:
                if user[1] != translation("dealerName", self.lang_id):  #09.02.2016 -> "Dealer" removed
                    set_game_won(user[3])
            # Alle mit 21 > Punkte >= 0 haben verloren . || Alle mit 21 haben Einsatz gewonnen || Alle mit 21 und Kartenanzahl = 2 haben Einsatz mal 2 gewonnen
            # todo wenn Dealer Blackjack hat: || Alle mit BlackJack haben Einsatz gewonnen. || Alle anderen haben verloren
        elif self.kartenwert_dealer < 21:
            for user in list_21:
                set_game_won(user[3])
            for user in list_lower_21:
                if user[0] > self.kartenwert_dealer:
                    set_game_won(user[3])
            # Alle mit Dealer > Punkte haben verloren.
            # Alle mit Dealer = Punkte erhalten Einsatz
            # Alle mit 21 > Punkte > Dealer haben Einsatz x 1,5 gewonnen.
            # Alle mit 21 haben Einsatz mal 2 gewonnen
            # Alle mit 21 und Kartenanzahl = 2 haben Einsatz mal 3 gewonnen
            # 7er Drilling 3/2 Gewinn (Einsatz x 1,5)

        string = translation("playerWith21", lang_id) + "\n"
        for lst in list_21:
            string += str(lst[0]) + " - " + str(lst[1]) + "\n"

        string += "\n" + translation("playerLess21", lang_id) + "\n"
        for lst in list_lower_21:
            string += str(lst[0]) + " - " + str(lst[1]) + "\n"

        string += "\n" + translation("playerOver21", lang_id) + "\n"
        for lst in list_busted:
            string += str(lst[0]) + " - " + str(lst[1]) + "\n"

        self.message_adapter.sendmessage(self.chat_id, string, self.bot)
        self.game_handler_object.gl_remove(self.chat_id)

# ---------------------------------- Get Player overview -----------------------------------------#

    def get_player_overview(self, show_points=None, text="", i=0, x=0, dealer=False):  # show_points ist um Punkte anzuzeigen
        for user in self.players:
            if i == self.current_player:
                text += "▶️"
            else:
                text += "👤"
            if show_points is True and (i < self.current_player or self.current_player == -1 or x == 1337):
                text += (user.name + " - [" + str(self.players[i].cardvalue) + "]\n")
            else:
                text += (user.name + "\n")
            i += 1
        if dealer is True:
            text += ("🎩" + translation("dealerName", self.lang_id) + " - [" + str(self.kartenwert_dealer) + "]")
        return text

# ---------------------------------- Change Language -----------------------------------------#

    def change_language(self, lang_id, message_id, user_id):
        self.message_adapter.sendmessage(self.chat_id, translation("langChanged", lang_id), self.bot,
                                         keyboard=[[translation("keyboardItemOneMore", lang_id), translation("keyboardItemNoMore", lang_id)], [translation("keyboardItemStart", lang_id)]],
                                         message_id=message_id)
        sql_insert("languageID", lang_id, user_id)
        self.lang_id = lang_id

        self.keyboard_running = [[translation("keyboardItemOneMore", lang_id), translation("keyboardItemNoMore",lang_id)],[translation("keyboardItemStop", lang_id)]]
        self.keyboard_not_running = [[translation("keyboardItemStart", lang_id)]]


# ---------------------------------- Analyzing -----------------------------------------#

    # Nachrichten werden hier analysiert und bearbeitet. Die Funktionen werden von hier aus gestartet
    def analyze_message(self, command, user_id, first_name, message_id):
        print("analyze_message - " + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        if str(command).startswith(translation("startCmd", self.lang_id)) or str(command).startswith("start"):
            if self.game_type == "1":  # wenn Spiel ein Gruppenchat ist
                if len(self.players) >= 1:  # todo >=2 #wenn genügend Spieler dabei sind
                    if self.game_running is False:  # wenn das Spiel noch nicht läuft
                        if user_id == self.players[0].user_id:  # Wenn der Spielersteller starten schreibt
                            self.start_game(message_id)
                        else:
                            self.message_adapter.sendmessage(self.chat_id, translation("onlyGameCreator", self.lang_id), self.bot, message_id=message_id)
                    else:
                        self.message_adapter.sendmessage(self.chat_id, translation("alreadyAGame", self.lang_id), self.bot, keyboard=self.keyboard_running, message_id=message_id)
                else:
                    self.message_adapter.sendmessage(self.chat_id, translation("notEnoughPlayers", self.lang_id), self.bot, message_id=message_id)
            else:  # When game is singleplayer
                self.message_adapter.sendmessage(self.chat_id, translation("alreadyAGame", self.lang_id), self.bot, keyboard=self.keyboard_running, message_id=message_id)

        elif str(command).startswith(translation("onemore", self.lang_id)):
            if self.game_running is True:
                if user_id == self.players[self.current_player].user_id:
                    self.give_player_one(first_name)
                else:
                    self.message_adapter.sendmessage(self.chat_id, translation("notYourTurn", self.lang_id).format(first_name), self.bot, message_id=message_id)
            else:
                self.message_adapter.sendmessage(self.chat_id, translation("noGame", self.lang_id), self.bot, message_id=message_id)

        elif str(command).startswith(translation("nomore", self.lang_id)):
            if user_id == self.players[self.current_player].user_id:
                self.next_player()

        elif str(command).startswith(translation("join", self.lang_id)) and self.game_type == "1":
            # todo one time keyboard
            if self.get_index_by_user_id(user_id) == -1:
                self.add_player(user_id, first_name, message_id)
            else:
                self.message_adapter.sendmessage(self.chat_id, translation("alreadyJoined", self.lang_id).format(first_name), self.bot, message_id=message_id)

            if len(self.players) == 5:
                self.start_game(message_id)

        elif str(command).startswith(translation("stopCmd", self.lang_id)) or str(command).startswith("stop"):
            if user_id == self.players[0].user_id:  # TODO neu 04.03.16, gut so?
                self.game_handler_object.gl_remove(self.chat_id)

        elif str(command).startswith("hide"):
            hide_keyboard(self.chat_id, self.bot)

        elif str(command).startswith("language") and not self.game_running:
            self.message_adapter.sendmessage(self.chat_id, translation("langSelect", self.lang_id), self.bot, keyboard=self.keyboard_language, message_id=message_id)
        elif str(command).startswith("deutsch") and not self.game_running:
            self.change_language("de", message_id, user_id)
        elif str(command).startswith("english") and not self.game_running:
            self.change_language("en", message_id, user_id)
        elif str(command).startswith("português") and not self.game_running:
            self.change_language("br", message_id, user_id)
        elif str(command).startswith("nederlands") and not self.game_running:
            self.change_language("nl", message_id, user_id)
        else:
            print("No matches!")

    # When game is being initialized
    def __init__(self, chat_id, user_id, lang_id, game_type, first_name, gamehandler, message_id, bot):
        print("BlackJack_init - " + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        self.game_handler_object = gamehandler
        self.message_adapter = messageSenderAdapter(bot, chat_id)
        self.chat_id = chat_id
        self.players = []*0
        self.join_ids = []*0
        self.kartenwert_dealer = 0
        self.karten_list_dealer = []*0
        self.lang_id = lang_id
        self.bot = bot
        self.create_stapel()
        self.value_str = [translation("ace", lang_id), "2", "3", "4", "5", "6", "7", "8", "9", "10",
                          translation("jack", lang_id), translation("queen", lang_id), translation("king", lang_id)]

        self.keyboard_running = [[translation("keyboardItemOneMore", lang_id), translation("keyboardItemNoMore",lang_id)],[translation("keyboardItemStop", lang_id)]]
        self.keyboard_not_running = [[translation("keyboardItemStart", lang_id)]]

        self.add_player(user_id, first_name, message_id, silent=True)
        self.game_type = game_type

        #if it is no groupchat
        if chat_id == user_id:
            self.game_running = True
            add_game_played(user_id)
            self.message_adapter.set_metadata(keyboard=self.keyboard_running, message_id=message_id)
            self.dealers_first_turn()
        else: # if it is a groupchat:
            self.message_adapter.sendmessage(chat_id, translation("newRound", lang_id), self.bot, message_id=message_id, keyboard=self.keyboard_not_running)


    #When game is being ended - single and multiplayer
    def __del__(self):
        for player in self.players:
            self.players.pop()
        hide_keyboard(self.chat_id, self.bot, translation("gameEnded", self.lang_id))