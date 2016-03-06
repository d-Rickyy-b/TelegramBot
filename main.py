# -*- coding: utf-8 -*-
__author__ = 'Rico'

import datetime

from twx.botapi import TelegramBot

from blackJack import blackJack
from messageSender import sendmessage, hide_keyboard
from language import translation
from gamehandler import GameHandler
from update_handler import getUpdates
from sql_handler import sql_connect, sql_insert, check_if_user_saved, sql_getUser


class Main(object):
    BOT_TOKEN = "<your_bot_token_here>"
    bot = TelegramBot(BOT_TOKEN)
    left_msgs = [[]] * 0
    offset = 0
    users = sql_connect()  # List, where userdata is stored in
    game_handler = GameHandler()
    GameList = game_handler.GameList #blackJack objects are stored in this list
    CommentList = [] * 0
    # message_adapter = messageSenderAdapter(bot, 0)

    keyboard_language = [
        ["Deutsch 🇩🇪", "English 🇺🇸"],
        ["Português 🇧🇷", "Nederlands 🇳🇱"], ["Esperanto 🌍"]]

    def add_to_game_list(self, chat_id, user_id, lang_id, game_type, first_name, message_id):
        bj = blackJack(chat_id, user_id, lang_id, game_type, first_name, self.game_handler, message_id, self.bot)
        self.GameList.append(bj)

    def set_message_answered(self):
        if len(self.left_msgs) > 0:
            self.offset = self.left_msgs[0][1]
            self.left_msgs.pop(0)
            print("Un-Answered Messages: " + str(len(self.left_msgs)))

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
                self.left_msgs.append(line)
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
            while len(self.left_msgs) > 0:
                if isinstance(self.left_msgs[0][4], str):
                    text_orig = str(self.left_msgs[0][4])
                    text = text_orig.lower()
                else:
                    text = ""

                user_id = self.left_msgs[0][0]
                chat_id = self.left_msgs[0][6]
                message_id = self.left_msgs[0][7]
                first_name = self.left_msgs[0][2]
                last_name = self.left_msgs[0][3]
                username = self.left_msgs[0][8]
                lang_id = str(check_if_user_saved(user_id)[2])
                game_type = self.left_msgs[0][5]

                chat_index = self.get_index_by_chat_id(chat_id)  # getIndexByChatID -> checkt ob Spiel im Chat vorhanden

                if text.startswith("/"):
                    text = str(text[1:])
                    text_orig = str(text_orig[1:])

                keyboard_running = [[translation("keyboardItemOneMore", lang_id), translation("keyboardItemNoMore", lang_id)], [translation("keyboardItemStop", lang_id)]]
                keyboard_not_running = [[translation("keyboardItemStart", lang_id)]]

                if text.startswith("comment"):
                    if len(text) == 7 or len(text) == 20:
                        if not user_id in self.CommentList:
                            sendmessage(chat_id, translation("sendCommentNow", lang_id), self.bot, message_id=message_id, force_reply=1)
                            self.CommentList.append(user_id)
                        else:
                            pass
                    else:
                        sendmessage(chat_id, translation("userComment", lang_id), self.bot, keyboard=keyboard_not_running)
                        sendmessage(24421134, "Nutzer Kommentar:\n\n" + str(
                            text_orig[7:] + "\n\n" + str(user_id) + " | " + str(first_name) + " | " + str(last_name) + " | @" + str(username) + " | " + str(lang_id)), self.bot, parse_mode=None)
                        if user_id in self.CommentList:
                            self.CommentList.pop(self.CommentList.index(user_id))

                elif text.startswith("cancel") and user_id in self.CommentList:  # TODO doesn't work at the moment
                    sendmessage(chat_id, "I cancelled your request", self.bot)
                    self.CommentList.pop(self.CommentList.index(user_id))

                elif text.startswith("!answer") and chat_id == 24421134:
                    text_orig = str(text_orig[8:])
                    if self.left_msgs[0][9] is not None and self.left_msgs[0][9] is not "":
                        try:
                            msg_chat_id = self.left_msgs[0][9]
                            answer_text = str(text_orig)
                        except:
                            msg_chat_id = "24421134"
                            answer_text = "Fehler"
                    else:
                        try:
                            msg_list = text_orig.split("|")
                            answer_text = str(msg_list[0])
                            msg_chat_id = msg_list[1]
                        except:
                            sendmessage(24421134, "Fehler bei answer", self.bot, parse_mode=None)
                            msg_chat_id = "24421134"
                            answer_text = "Fehler"
                    sendmessage(24421134, "Ich habe deine Nachricht an den Nutzer weitergeleitet: \n\n" + answer_text + "\n\n(" + msg_chat_id + ")", self.bot, parse_mode=None)
                    sendmessage(msg_chat_id, translation("thanksForComment", lang_id) + "\n" +
                                translation("answerFromDev", lang_id) + " \n\n" + answer_text + "\n\n" +
                                translation("clickCommentToAnswer", lang_id), self.bot, parse_mode=None)

                elif user_id in self.CommentList:
                    sendmessage(chat_id, translation("userComment", lang_id), self.bot, parse_mode=None)
                    sendmessage(24421134,
                                "Nutzer Kommentar:\n\n" + str(text_orig + "\n\n" + str(user_id) + " | " + str(first_name) + " | " + str(last_name) + " | @" + str(username) + " | " + str(lang_id)),
                                self.bot, parse_mode=None)
                    self.CommentList.pop(self.CommentList.index(user_id))

                elif not chat_index == -1:
                    # If a game is present, send messages directly to that game
                    game = self.GameList[chat_index]
                    game.analyze_message(text, user_id, first_name, message_id)

                elif text.startswith(translation("startCmd", lang_id)) or str(text).startswith("start"):
                    if chat_index == -1:
                        self.add_to_game_list(chat_id, user_id, lang_id, game_type, first_name, message_id)
                    else:
                        sendmessage(chat_id, translation("alreadyAGame", lang_id), self.bot, keyboard=keyboard_running)
                elif text.startswith("language"):
                    sendmessage(chat_id, translation("langSelect", lang_id), self.bot, message_id=message_id, keyboard=self.keyboard_language)
                elif text.startswith("deutsch"):
                    self.send_lang_changed_message(chat_id, message_id, "de", user_id)
                elif text.startswith("english"):
                    self.send_lang_changed_message(chat_id, message_id, "en", user_id)
                elif text.startswith("português"):
                    self.send_lang_changed_message(chat_id, message_id, "br", user_id)
                elif text.startswith("nederlands"):
                    self.send_lang_changed_message(chat_id, message_id, "nl", user_id)
                elif text.startswith("esperanto"):
                    self.send_lang_changed_message(chat_id, message_id, "eo", user_id)

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
                                "\n\n" + self.get_stats(round(float(user[7]) / float(played_games), 4) * 100) +
                                "\n\nWinning rate: " + '{percent:.2%}'.format(percent=float(user[7]) / float(played_games)), self.bot, message_id)
                self.set_message_answered()
        except:
            sendmessage(24421134, "Bot Error:\n\nNachrichten konnten nicht ausgewertet werden! (" + text + ")", self.bot)
            raise

    def __init__(self):
        print("Bot gestartet")

main = Main()
main.batch_run()
