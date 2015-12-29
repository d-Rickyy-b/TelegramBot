# -*- coding: utf-8 -*-
__author__ = 'Rico'

from blackJack import blackJack
from messageSender import sendmessage, hide_keyboard
from language import translation
from game_handler import game_handler
from update_handler import getUpdates
import datetime
import threading
from sql_handler import sql_connect, sql_insert, check_if_user_saved, sql_getUser


class main(object):
    BOT_TOKEN = "<your_bot_token_here>"

    unAnsweredMessages = [[]]*0
    offset = 0
    users = sql_connect()  # List, where userdata is stored in
    # feedback_users = []
    game_handler = game_handler()
    game_handler.gl_create()
    GameList = game_handler.GameList

    keyboard_language = [
        ["Deutsch 🇩🇪", "English 🇺🇸"],
        ["Português 🇧🇷", "Nederlands 🇳🇱"]]

    def set_language(self, user_id, lang_id):
        sql_insert("languageID", lang_id, user_id) # TODO language in gruppen

    # returns the Time string to a unix timestamp
    def get_time(self, unixtime): # no usage found
        return datetime.datetime.fromtimestamp(int(unixtime)).strftime("%d.%m.%Y %H:%M:%S")

    def addToGameList(self, chat_id, user_id, lang_id, game_type, first_name, message_id):
        bj = blackJack(chat_id, user_id, lang_id, game_type, first_name, self.game_handler, message_id, self.BOT_TOKEN)
        self.GameList.append(bj)

    def setMessageAnswered(self):
        self.offset = self.unAnsweredMessages[0][1]
        self.unAnsweredMessages.pop(0)
        print("Un-Answered Messages: " + str(len(self.unAnsweredMessages)))

    def send_lang_changed_message(self, chat_id, message_id, lang_id, user_id):
        sendmessage(chat_id, translation("langChanged", lang_id), self.BOT_TOKEN, message_id=message_id, keyboard=[[translation("keyboardItemOneMore", lang_id), translation("keyboardItemNoMore", lang_id)], [translation("keyboardItemStart", lang_id)]])
        self.set_language(user_id, lang_id)
        self.setMessageAnswered()

    def update_adapter(self):
        templist = getUpdates(self.offset, self.BOT_TOKEN)

        if templist is not None:
            self.unAnsweredMessages.append(templist)

        self.analyze_messages()

        threading.Timer(1, self.update_adapter).start()

    def getCurrentGames(self):
        print("Aktuelle Spiele: " + str(len(self.GameList)))

    def getIndexByChatID(self, chat_id, i=0):
        for x in self.GameList:
            if x.chat_id == chat_id:
                return i
            i += 1
        return -1

    def send_update_message(self, text):
        sendmessage(24421134, text, self.BOT_TOKEN, keyboard=None)

    def get_emoji_stats(self, percentage):
        text = ""
        perc = int(percentage//10+1)
        for x in range(perc):
            text += "🏆"
        for x in range (10-perc):
            text += "🔴"
        return text

    def analyze_messages(self):
            try:
                while len(self.unAnsweredMessages) > 0:
                    if isinstance(self.unAnsweredMessages[0][4], str):
                        text_orig = str(self.unAnsweredMessages[0][4])
                        text = text_orig.lower()
                    else:
                        text = "noText"
                    user_id = self.unAnsweredMessages[0][0]
                    chat_id = self.unAnsweredMessages[0][6]
                    message_id = self.unAnsweredMessages[0][7]
                    first_name = self.unAnsweredMessages[0][2]
                    last_name = self.unAnsweredMessages[0][3]
                    username = self.unAnsweredMessages[0][3]
                    index = self.getIndexByChatID(chat_id)      # getIndexByChatID -> checkt ob Spiel im Chat vorhanden
                    lang_id = str(check_if_user_saved(user_id)[2])
                    game_type = self.unAnsweredMessages[0][5]

                    if text.startswith("/"):
                        text = str(text[1:])
                        text_orig = str(text_orig[1:])

                    keyboard_running = [[translation("keyboardItemOneMore", lang_id), translation("keyboardItemNoMore", lang_id)], [translation("keyboardItemStop", lang_id)]]
                    keyboard_not_running = [[translation("keyboardItemOneMore", lang_id),translation("keyboardItemNoMore", lang_id)],[translation("keyboardItemStart", lang_id)]]

                    if text.startswith("comment"):
                        sendmessage(chat_id, translation("userComment", lang_id), self.BOT_TOKEN, keyboard=keyboard_not_running)
                        sendmessage(24421134, "Nutzer Kommentar:\n\n" + str(text_orig[7:] + "\n\n" + str(user_id) + " | " + str(first_name) + " | " + str(last_name) + " | " + str(username) + " | " + str(lang_id)), self.BOT_TOKEN)
                        self.setMessageAnswered()

                    elif not self.getIndexByChatID(chat_id) == -1:
                        # If a game is present, send messages directly to that game
                        game = self.GameList[self.getIndexByChatID(chat_id)]
                        game.analyze_message(text, user_id, first_name, message_id)
                        self.setMessageAnswered()

                    elif text.startswith(translation("startCmd", lang_id)):
                        self.setMessageAnswered()

                        if index == -1:
                            self.addToGameList(chat_id, user_id, lang_id, game_type, first_name, message_id)
                            # game = self.GameList[self.getIndexByChatID(chat_id)]
                            # sendmessage(chat_id, translation("playerDraws1", lang_id).format(game.getKartenName()) + "\n" + translation("playerDraws2", lang_id).format(str(game.kartenwert)), keyboard=keyboard_running)
                            # sql_insert("lastPlayed", int(time()), user_id)
                            # add_game_played(user_id)
                            # users[check_if_user_saved(user_id)][9] = int(time())
                        else:
                            sendmessage(chat_id, translation("alreadyAGame", lang_id), self.BOT_TOKEN, keyboard=keyboard_running)
                    elif text.startswith("language"):
                        sendmessage(chat_id, translation("langSelect", lang_id), self.BOT_TOKEN, message_id=message_id, keyboard=self.keyboard_language, force_reply=True)
                        self.setMessageAnswered()
                    elif text.startswith("deutsch"):
                        self.send_lang_changed_message(chat_id, message_id, "de", user_id)
                    elif text.startswith("english"):
                        self.send_lang_changed_message(chat_id, message_id, "en", user_id)
                    elif text.startswith("português"):
                        self.send_lang_changed_message(chat_id, message_id, "br", user_id)
                    elif text.startswith("nederlands"):
                        self.send_lang_changed_message(chat_id, message_id, "nl", user_id)

                    elif text.startswith("hide"):
                        hide_keyboard(chat_id)
                        self.setMessageAnswered()
                    elif text.startswith("stats"):
                        # todo statistics
                        user = sql_getUser(user_id)
                        playedGames = 1;
                        if int(user[6]) > 0:
                            playedGames = user[6]
                        sendmessage(chat_id, "Here are your statistics  📊:\n\nPlayed Games: " + str(user[6]) +
                        "\nWon Games : " + str(user[7]) +

                        "\nLast Played: " + datetime.datetime.fromtimestamp(int(user[9])).strftime('%d.%m.%y %H:%M') + " CET" +
                        "\n\n" + self.get_emoji_stats(round(float(user[7])/float(playedGames), 4)*100) +
                        "\n\nWinning rate: " + '{percent:.2%}'.format(percent=float(user[7])/float(playedGames)), self.BOT_TOKEN, message_id, keyboard_not_running)
                                    # str(round(float(user[7])/float(user[6]), 4)) + "%", message_id, keyboard_not_running)
                        #"\nTies: " + str(user[8]) +
                        self.setMessageAnswered()
                    elif text.startswith("notext"):
                        self.setMessageAnswered()
                    elif text.startswith("#updatemessage"):
                        print("UpdateMessage wird gesendet!")
                        self.send_update_message(text_orig[15:])
                        self.setMessageAnswered()
                    else:
                        self.setMessageAnswered()
            except:
                sendmessage(24421134, "Bot Error:\n\nNachrichten konnten nicht ausgewertet werden! (" + text + ")", self.BOT_TOKEN)
                raise

    def end_game(self, chat_id):
        self.GameList.pop(self.getIndexByChatID(chat_id))

    def __init__(self):
        print("Bot gestartet")

    def get_users(self):
        print(len(self.users))

main = main()
main.update_adapter()
