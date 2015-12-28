# -*- coding: utf-8 -*-
__author__ = 'Rico'
from player import player
from messageSender import sendmessage, hide_keyboard
from language import translation
from statistics import add_game_played, set_game_won
from sql_handler import sql_insert

class blackJack(object):
    symbole = ["♥", "♦", "♣", "♠"]
    werteInt = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
    keyboard_language = [
        ["Deutsch 🇩🇪", "English 🇺🇸"],
        ["Português 🇧🇷", "Nederlands 🇳🇱"]]

    game_running = False
    aktuelleKarte_dealer = 0
    anzahl_karten_dealer = 0
    spieler = []*0
    stapel = []
    game_type = 0  # 0 ist für normale Chats, 1 für Gruppen
    spieler_an_der_reihe = 0
    BOT_TOKEN = ""

    # Adds Player to the Game
    def add_player(self, user_id, first_name, message_id, silent=None):
        if not self.game_running:
            self.spieler.append(player(user_id, first_name))
            if silent is None:
                sendmessage(self.chat_id, translation("playerJoined", self.lang_id).format(first_name), self.BOT_TOKEN,
                            message_id=message_id, keyboard=self.keyboard_not_running)

    def get_index_by_user_id(self, user_id):
        i = 0
        for user in self.spieler:
            if user.user_id == user_id:
                return i
            i += 1
        return -1

    def naechster_spieler(self):
        if (self.spieler_an_der_reihe + 1) < len(self.spieler):
            self.spieler_an_der_reihe += 1
            sendmessage(self.chat_id, translation("overview", self.lang_id)+"\n\n" +
                        self.get_player_overview(show_points=True) + "\n" +
                        translation("nextPlayer", self.lang_id).format(self.spieler[self.spieler_an_der_reihe].name), self.BOT_TOKEN)
        else:
            self.spieler_an_der_reihe = -1
            self.dealers_turn()

# ---------------------------------- test -----------------------------------------#

    def give_player_two(self, index):
        p = self.spieler[index]
        for x in range(2):
            karte = self.stapel[0]
            self.stapel.pop(0)
            kartenwert = self.werteInt[karte % 13]
            p.give_player_card(kartenwert)

# ---------------------------------- give player one -----------------------------------------#

    # Gibt dem Spieler eine Karte
    def givePlayerOne(self, first_name):
        karte = self.stapel[0]
        self.stapel.pop(0)
        kartenwert = self.werteInt[karte % 13]
        p_index = self.spieler_an_der_reihe
        p = self.spieler[p_index]

        if (p.kartenwert + kartenwert) > 21 and p.has_ace is True:
            sendmessage(self.chat_id, "Ace is counted as 1 afterwards -> Soft Hand", self.BOT_TOKEN)
            p.has_ace = False
            p.kartenwert -= 10

        if kartenwert == 1 and p.kartenwert > 10:
            sendmessage(self.chat_id, "Ace is counted as 1 -> Soft Hand", self.BOT_TOKEN)
        elif kartenwert == 1 and p.kartenwert <= 10:
            kartenwert = 11
            p.give_ace()
            sendmessage(self.chat_id, "Ace is counted as 11 -> Hard Hand", self.BOT_TOKEN)

        if self.game_type == "0":
            sp_mp_text = translation("playerDraws1", self.lang_id).format(str(self.getKartenName(karte)))
        else:
            sp_mp_text = translation("playerDrew", self.lang_id).format(first_name, str(self.getKartenName(karte)))

        p.give_player_card(kartenwert)
        sendmessage(self.chat_id, sp_mp_text + "\n" + translation("cardvalue", self.lang_id).format(str(p.kartenwert)), self.BOT_TOKEN, self.keyboard_running)

        if p.kartenwert == 21:
            sendmessage(self.chat_id, first_name + " hat 21 Punkte.", self.BOT_TOKEN)
            self.naechster_spieler()
        elif p.kartenwert > 21:
            if self.game_type == "1":
                sendmessage(self.chat_id, translation("playerBusted", self.lang_id).format(p.name), self.BOT_TOKEN)
            self.naechster_spieler()

    # Gibt dem Dealer eine Karte
    def dealers_turn(self, i=0):
        output_text = translation("croupierDrew", self.lang_id) + "\n\n"
        while self.kartenwert_dealer <= 16:
            karte = self.stapel[0]
            self.kartenwert_dealer += self.werteInt[karte % 13]
            self.stapel.pop(0)
            self.anzahl_karten_dealer += 1
            if i == 0:
                output_text += self.getKartenName(karte)
            else:
                output_text += " , " + self.getKartenName(karte)
            i += 1
        output_text += "\n\n" + translation("cardvalueDealer", self.lang_id) + " " + str(self.kartenwert_dealer)
        sendmessage(self.chat_id, output_text, self.BOT_TOKEN)
        self.auswertung(self.lang_id)

    # Erstellt einen Stapel
    def create_stapel(self):
        from random import shuffle
        stapel = list(range(1, 52))
        shuffle(stapel)
        self.stapel = stapel[:]

    def getKartenName(self, karte):
        symbol = self.symbole[karte//13]
        wert = self.value_str[karte % 13]
        string = "|"+symbol+" "+wert+"|"
        return string

    def start_game(self, message_id):
        self.game_running = True
        sendmessage(self.chat_id, translation("gameBegins", self.lang_id) + "\n" +
                    translation("gameBegins2", self.lang_id) + "\n\n" + self.get_player_overview(), self.BOT_TOKEN,
                    keyboard=self.keyboard_running, message_id=message_id)
        i = 0
        for p in self.spieler:
            #self.give_player_two(i)
            #self.givePlayerOne()
            add_game_played(p.user_id)
            i += 1

# ---------------------------------- Auswertung -----------------------------------------#

    def auswertung(self, lang_id):
        list_21 = [[]]*0
        list_busted = [[]]*0
        list_lower_21 = [[]]*0

        for player in self.spieler:
            tmplist = []*0
            kw = player.kartenwert
            tmplist.extend((kw, player.name, player.anzahl_karten, player.user_id))
            if kw > 21:
                list_busted.append(tmplist)
            elif kw == 21:
                list_21.append(tmplist)
            elif kw < 21:
                list_lower_21.append(tmplist)

        if self.kartenwert_dealer > 21:
            list_busted.append([self.kartenwert_dealer, "Dealer", self.anzahl_karten_dealer])
        elif self.kartenwert_dealer == 21:
            list_21.append([self.kartenwert_dealer, "Dealer", self.anzahl_karten_dealer])
        elif self.kartenwert_dealer < 21:
            list_lower_21.append([self.kartenwert_dealer, "Dealer", self.anzahl_karten_dealer])

        list_21 = sorted(list_21, key=lambda x: x[0], reverse=True)
        list_lower_21 = sorted(list_lower_21, key=lambda x: x[0], reverse=True)
        list_busted = sorted(list_busted, key=lambda x: x[0], reverse=True)

        if self.kartenwert_dealer > 21:
            for player in list_21:
                set_game_won(player[3])
            for player in list_lower_21:
                set_game_won(player[3])
            # Alle mit 21 > Punkte >= 0 haben Einsatz x 1,5 gewonnen.
            # Alle mit 21 haben Einsatz mal 2 gewonnen
            # Alle mit 21 und Kartenanzahl = 2 haben Einsatz mal 3 gewonnen
        elif self.kartenwert_dealer == 21:  # unterscheidung zwischen blackjack und 21
            for player in list_21:
                if player[1] != "Dealer":
                    set_game_won(player[3])
            # Alle mit 21 > Punkte >= 0 haben verloren .
            # Alle mit 21 haben Einsatz gewonnen
            # Alle mit 21 und Kartenanzahl = 2 haben Einsatz mal 2 gewonnen
            # todo wenn Dealer Blackjack hat:
            # Alle mit BlackJack haben Einsatz gewonnen.
            # Alle anderen haben verloren
        elif self.kartenwert_dealer < 21:
            for player in list_21:
                set_game_won(player[3])
            for player in list_lower_21:
                if player[0] > self.kartenwert_dealer:
                    set_game_won(player[3])
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

        sendmessage(self.chat_id, string, self.BOT_TOKEN)

        self.game_handler_object.gl_remove(self.chat_id)

# ---------------------------------- Get Player overview -----------------------------------------#

    def get_player_overview(self, show_points=None, text="", i=0, x=0, dealer=False):  # show_points ist um Punkte anzuzeigen
        for user in self.spieler:
            if i == self.spieler_an_der_reihe:
                text += "▶️"
            else:
                text += "👤"
            if show_points is True and (i < self.spieler_an_der_reihe or self.spieler_an_der_reihe == -1 or x == 1337):
                text += (user.name + " - [" + str(self.spieler[i].kartenwert) + "]\n")
            else:
                text += (user.name + "\n")
            i += 1
        if dealer is True:
            text += ("🎩Dealer - [" + str(self.kartenwert_dealer) + "]")
        return text

# ---------------------------------- Change Language -----------------------------------------#

    def change_language(self, lang_id, message_id, user_id):
        sendmessage(self.chat_id, translation("langChanged", lang_id), self.BOT_TOKEN, keyboard=[[translation("keyboardItemOneMore", lang_id), translation("keyboardItemNoMore", lang_id)], [translation("keyboardItemStart", lang_id)]], message_id=message_id)
        sql_insert("languageID", lang_id, user_id)
        self.lang_id = lang_id

        self.keyboard_running = [[translation("keyboardItemOneMore", lang_id), translation("keyboardItemNoMore",lang_id)],[translation("keyboardItemStop", lang_id)]]
        self.keyboard_not_running = [[translation("keyboardItemOneMore", lang_id), translation("keyboardItemNoMore",lang_id)],[translation("keyboardItemStart", lang_id)]]
        self.keyboard_join = [[translation("join", lang_id), translation("keyboardItemStart", lang_id)]]


# ---------------------------------- Analyzing -----------------------------------------#

    # Nachrichten werden hier analysiert und bearbeitet. Die Funktionen werden von hier aus gestartet
    def analyze_message(self, command, user_id, first_name, message_id):
        if str(command).startswith(translation("startCmd", self.lang_id)):
            if self.game_type == "1":  # wenn Spiel ein Gruppenchat ist
                if len(self.spieler) >= 1:  # todo >=2 #wenn genügend Spieler dabei sind
                    if self.game_running is False:  # wenn das Spiel noch nicht läuft
                        if user_id == self.spieler[0].user_id:  # Wenn der Spielersteller starten schreibt
                            self.start_game(message_id)
                        else:
                            sendmessage(self.chat_id, translation("onlyGameCreator", self.lang_id), self.BOT_TOKEN, message_id=message_id)
                    else:
                        sendmessage(self.chat_id, translation("alreadyAGame", self.lang_id), self.BOT_TOKEN, message_id=message_id)
                else:
                    sendmessage(self.chat_id, translation("notEnoughPlayers", self.lang_id), self.BOT_TOKEN, message_id=message_id)
            else:  # Wenn Spiel ein einzelChat ist
                if self.game_running is False:  # wenn das Spiel noch nicht läuft
                    self.game_running = True
                else:
                    sendmessage(self.chat_id, translation("alreadyAGame", self.lang_id), self.BOT_TOKEN, message_id=message_id)

        elif str(command).startswith(translation("onemore", self.lang_id)):
            if self.game_running is True:
                print("Players: " + str(len(self.spieler)) + " | " + str(self.spieler_an_der_reihe))
                if user_id == self.spieler[self.spieler_an_der_reihe].user_id:
                    self.givePlayerOne(first_name)
                else:
                    sendmessage(self.chat_id, translation("notYourTurn", self.lang_id).format(first_name), self.BOT_TOKEN, message_id=message_id)
            else:
                sendmessage(self.chat_id, translation("noGame", self.lang_id), self.BOT_TOKEN, message_id=message_id)

        elif str(command).startswith(translation("nomore", self.lang_id)):
            if user_id == self.spieler[self.spieler_an_der_reihe].user_id:
                self.naechster_spieler()

        elif str(command).startswith(translation("join", self.lang_id)) and self.game_type == "1":
            # todo one time keyboard
            if self.get_index_by_user_id(user_id) == -1:
                self.add_player(user_id, first_name, message_id)
            else:
                sendmessage(self.chat_id, translation("alreadyJoined", self.lang_id).format(first_name), self.BOT_TOKEN, message_id=message_id, keyboard=self.keyboard_join)

            if len(self.spieler) == 4:
                self.start_game(message_id)

        elif str(command).startswith("stop"):
            self.game_handler_object.gl_remove(self.chat_id)

        elif str(command).startswith("hide"):
            hide_keyboard(self.chat_id, self.BOT_TOKEN)

        elif str(command).startswith("players"):
            sendmessage(self.chat_id, "Es sind " + str(len(self.spieler)) + " beigetreten.", self.BOT_TOKEN, message_id=message_id)

        elif str(command).startswith("language"):
            sendmessage(self.chat_id, translation("langSelect", self.lang_id), self.BOT_TOKEN, keyboard=self.keyboard_language, message_id=message_id)
        elif str(command).startswith("deutsch"):
            self.change_language("de", message_id, user_id)
        elif str(command).startswith("english"):
            self.change_language("en", message_id, user_id)
        elif str(command).startswith("português"):
            self.change_language("br", message_id, user_id)
        elif str(command).startswith("nederlands"):
            self.change_language("nl", message_id, user_id)
        else:
            print("No matches!")

    # Wird beim ersten aufrufen ausgeführt
    def __init__(self, chat_id, user_id, lang_id, game_type, first_name, g_h, message_id, BOT_TOKEN):
        self.game_handler_object = g_h
        self.chat_id = chat_id
        self.create_stapel()
        self.spieler = []*0
        self.kartenwert_dealer = 0
        self.lang_id = lang_id
        self.BOT_TOKEN = BOT_TOKEN
        self.value_str = [translation("ace", lang_id), "2", "3", "4", "5", "6", "7", "8", "9", "10",
                          translation("jack", lang_id), translation("queen", lang_id), translation("king", lang_id)]

        self.keyboard_running = [[translation("keyboardItemOneMore", lang_id), translation("keyboardItemNoMore",lang_id)],[translation("keyboardItemStop", lang_id)]]
        self.keyboard_not_running = [[translation("keyboardItemOneMore", lang_id), translation("keyboardItemNoMore",lang_id)],[translation("keyboardItemStart", lang_id)]]
        self.keyboard_join = [[translation("join", lang_id), translation("keyboardItemStart", lang_id)]]

        self.add_player(user_id, first_name, message_id, silent=True)
        self.game_type = game_type

        if chat_id == user_id:
            self.game_running = True
            add_game_played(user_id)
            sendmessage(self.chat_id, translation("gameBegins", lang_id), self.BOT_TOKEN, keyboard=self.keyboard_running,
                        message_id=message_id)
        else:
            sendmessage(chat_id, translation("newRound", lang_id), self.BOT_TOKEN, keyboard=self.keyboard_join, message_id=message_id)


    def __del__(self):
        for spieler in self.spieler:
            self.spieler.pop()
        hide_keyboard(self.chat_id, self.BOT_TOKEN, translation("gameEnded", self.lang_id))