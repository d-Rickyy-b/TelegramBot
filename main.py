# -*- coding: utf-8 -*-
__author__ = 'Rico'

from blackJack import blackJack
from messageSender import sendmessage, hide_keyboard
from language import translation
from gamehandler import GameHandler
from update_handler import getUpdates
import datetime
from sql_handler import sql_connect, sql_insert, check_if_user_saved, sql_getUser
from twx.botapi import TelegramBot


class Main(object):
    BOT_TOKEN = "<your_bot_token_here>"

    bot = TelegramBot(BOT_TOKEN)
    unAnsweredMessages = [[]]*0
    offset = 0
    users = sql_connect()  # List, where userdata is stored in
    game_handler = GameHandler()
    GameList = game_handler.GameList #blackJack objects are stored in this list

    keyboard_language = [
        ["Deutsch 🇩🇪", "English 🇺🇸"],
        ["Português 🇧🇷", "Nederlands 🇳🇱"]]

    def add_to_game_list(self, chat_id, user_id, lang_id, game_type, first_name, message_id):
        bj = blackJack(chat_id, user_id, lang_id, game_type, first_name, self.game_handler, message_id, self.bot)
        self.GameList.append(bj)

    def set_message_answered(self):
        if len(self.unAnsweredMessages)>0 :
            self.offset = self.unAnsweredMessages[0][1]
            self.unAnsweredMessages.pop(0)
            print("Un-Answered Messages: " + str(len(self.unAnsweredMessages)))

    def send_lang_changed_message(self, chat_id, message_id, lang_id, user_id):
        sendmessage(chat_id, translation("langChanged", lang_id), self.bot, message_id=message_id, keyboard=[[translation("keyboardItemStart", lang_id)]])
        sql_insert("languageID", lang_id, user_id) # TODO language in gruppen

    def batch_run(self):
        while True:
            self.update_adapter()

    def update_adapter(self):
        templist = getUpdates(self.offset, self.bot)
        #listLength = len(templist) #throws error if templist is None
        if templist: #and listLength > 0:
            for line in templist:
                self.unAnsweredMessages.append(line)
            self.analyze_messages()

    def get_index_by_chat_id(self, chat_id, i=0):
        for x in self.GameList:
            if x.chat_id == chat_id:
                return i
            i += 1
        return -1

    @staticmethod
    def get_stats(percentage):
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
                        text = ""

                    user_id = self.unAnsweredMessages[0][0]
                    chat_id = self.unAnsweredMessages[0][6]
                    message_id = self.unAnsweredMessages[0][7]
                    first_name = self.unAnsweredMessages[0][2]
                    last_name = self.unAnsweredMessages[0][3]
                    username = self.unAnsweredMessages[0][8]
                    lang_id = str(check_if_user_saved(user_id)[2])
                    game_type = self.unAnsweredMessages[0][5]

                    chat_index = self.get_index_by_chat_id(chat_id)      # getIndexByChatID -> checkt ob Spiel im Chat vorhanden

                    if text.startswith("/"):
                        text = str(text[1:])
                        text_orig = str(text_orig[1:])

                    keyboard_running = [[translation("keyboardItemOneMore", lang_id), translation("keyboardItemNoMore", lang_id)], [translation("keyboardItemStop", lang_id)]]
                    keyboard_not_running = [[translation("keyboardItemStart", lang_id)]]

                    if text.startswith("comment"):
                        sendmessage(chat_id, translation("userComment", lang_id), self.bot, keyboard=keyboard_not_running)
                        sendmessage(24421134, "Nutzer Kommentar:\n\n" + str(text_orig[7:] + "\n\n" + str(user_id) + " | " + str(first_name) + " | " + str(last_name) + " | @" + str(username) + " | " + str(lang_id)), self.bot)

                    elif not chat_index == -1:
                        # If a game is present, send messages directly to that game
                        game = self.GameList[chat_index]
                        game.analyze_message(text, user_id, first_name, message_id)

                    elif text.startswith(translation("startCmd", lang_id)):

                        if chat_index == -1:
                            self.add_to_game_list(chat_id, user_id, lang_id, game_type, first_name, message_id)
                        else:
                            sendmessage(chat_id, translation("alreadyAGame", lang_id), self.bot, keyboard=keyboard_running)
                    elif text.startswith("language"):
                        sendmessage(chat_id, translation("langSelect", lang_id), self.bot, message_id=message_id, keyboard=self.keyboard_language, force_reply=True)
                    elif text.startswith("deutsch"):
                        self.send_lang_changed_message(chat_id, message_id, "de", user_id)
                    elif text.startswith("english"):
                        self.send_lang_changed_message(chat_id, message_id, "en", user_id)
                    elif text.startswith("português"):
                        self.send_lang_changed_message(chat_id, message_id, "br", user_id)
                    elif text.startswith("nederlands"):
                        self.send_lang_changed_message(chat_id, message_id, "nl", user_id)

                    elif text.startswith("hide"):
                        hide_keyboard(chat_id, self.bot)
                    elif text.startswith("stats"):
                        # TODO if user didn't ever play -> crash maybe
                        user = sql_getUser(user_id)
                        played_games = 1
                        if int(user[6]) > 0:
                            played_games = user[6]
                        sendmessage(chat_id, "Here are your statistics  📊:\n\nPlayed Games: " + str(user[6]) +
                        "\nWon Games : " + str(user[7]) +
                        "\nLast Played: " + datetime.datetime.fromtimestamp(int(user[9])).strftime('%d.%m.%y %H:%M') + " CET" +
                        "\n\n" + self.get_stats(round(float(user[7])/float(played_games), 4)*100) +
                        "\n\nWinning rate: " + '{percent:.2%}'.format(percent=float(user[7])/float(played_games)), self.bot, message_id)
                    self.set_message_answered()
            except:
                sendmessage(24421134, "Bot Error:\n\nNachrichten konnten nicht ausgewertet werden! (" + text + ")", self.bot)
                raise

    def __init__(self):
        print("Bot gestartet")

main = Main()
main.batch_run()