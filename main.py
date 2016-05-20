# -*- coding: utf-8 -*-
__author__ = 'Rico'

import time
import subprocess

from twx.botapi import TelegramBot

from blackJack import blackJack
from language import translation
from gamehandler import GameHandler
from update_handler import get_updates
from sql_handler import sql_connect, sql_insert, check_if_user_saved, get_playing_users, get_highest_ranked_player
from messageSenderAdapter import MessageSenderAdapter
from statistics import get_user_stats


class Main(object):
    BOT_TOKEN = "<your_bot_token_here>"
    DEV_ID = 24421134
    bot = TelegramBot(BOT_TOKEN)
    left_msgs = [[]] * 0
    offset = 0
    users = sql_connect()
    game_handler = GameHandler()
    GameList = game_handler.GameList
    CommentList = [] * 0
    adminList = [DEV_ID, 58139255]
    message_adapter = MessageSenderAdapter(bot, 0)

    keyboard_language = [
        ["Deutsch 🇩🇪", "English 🇺🇸"],
        ["Português 🇧🇷", "Nederlands 🇳🇱"],
        ["Esperanto 🌍", "Español 🇪🇸"]]

    def add_to_game_list(self, chat_id, user_id, lang_id, game_type, first_name, message_id):
        black_jack_game = blackJack(chat_id, user_id, lang_id, game_type, first_name, self.game_handler, message_id, self.bot)
        self.game_handler.add_game(black_jack_game)

    def set_message_answered(self):
        if len(self.left_msgs) > 0:
            self.offset = self.left_msgs[0][1]
            self.left_msgs.pop(0)
            print("Un-Answered Messages: " + str(len(self.left_msgs)))

    def send_lang_changed_message(self, chat_id, message_id, lang_id, user_id):
        self.message_adapter.send_new_message(chat_id, translation("langChanged", lang_id), message_id=message_id, keyboard=[[translation("keyboardItemStart", lang_id)]])
        sql_insert("languageID", lang_id, user_id)  # TODO language setting for whole groups

    def batch_run(self):
        while True:
            time.sleep(0.01)
            self.update_adapter()

    def update_adapter(self):
        templist = get_updates(self.offset, self.bot)
        if templist: #and listLength > 0:
            for line in templist:
                self.left_msgs.append(line)
            self.analyze_messages()

    def analyze_messages(self):
        try:
            while len(self.left_msgs) > 0:
                if isinstance(self.left_msgs[0][4], str):
                    text_orig = str(self.left_msgs[0][4])
                    text = text_orig.lower()
                else:
                    text_orig = "noText"
                    text = ""

                user_id = self.left_msgs[0][0]
                chat_id = self.left_msgs[0][6]
                message_id = self.left_msgs[0][7]
                first_name = self.left_msgs[0][2]
                last_name = self.left_msgs[0][3]
                username = self.left_msgs[0][8]
                lang_id = str(check_if_user_saved(user_id)[2]) #problem maybe
                game_type = self.left_msgs[0][5]

                chat_index = self.game_handler.get_index(chat_id)  # get_index_by_chatid -> checkt ob Spiel im Chat vorhanden

                if text.startswith("/"):
                    text = str(text[1:])
                    text_orig = str(text_orig[1:])

                keyboard_running = [[translation("keyboardItemOneMore", lang_id), translation("keyboardItemNoMore", lang_id)], [translation("keyboardItemStop", lang_id)]]
                keyboard_not_running = [[translation("keyboardItemStart", lang_id)]]
                if text.startswith("comment"):

                    if len(text) == 7 or len(text) == 20:
                        if user_id not in self.CommentList:
                            self.message_adapter.send_new_message(chat_id, translation("sendCommentNow", lang_id), message_id=message_id, force_reply=1)
                            self.CommentList.append(user_id)
                    else:
                        self.message_adapter.send_new_message(chat_id, translation("userComment", lang_id), keyboard=keyboard_not_running)
                        self.message_adapter.send_new_message(self.DEV_ID, "Nutzer Kommentar:\n\n" + str(
                            text_orig[7:] + "\n\n" + str(user_id) + " | " + str(first_name) + " | " + str(last_name) + " | @" + str(username) + " | " + str(lang_id)))
                        if user_id in self.CommentList:
                            self.CommentList.pop(self.CommentList.index(user_id))

                elif text.startswith("cancel") and user_id in self.CommentList:
                    self.message_adapter.send_new_message(chat_id, "I cancelled your request")
                    self.CommentList.pop(self.CommentList.index(user_id))

                elif text.startswith("!help") and chat_id in self.adminList:
                    message_text = "*!help*    -  print this help\n" \
                           "*!ip*         -  print ip address of the Pi\n" \
                           "*!users*  -  show usercount\n" \
                           "*!id*         -  show your Telegram ID\n" \
                           "*!answer* -  answer to a comment"

                    self.message_adapter.send_new_message(chat_id, message_text, parse_mode="Markdown")
                elif text.startswith("!ip") and chat_id in self.adminList:
                    try:
                        message_text = subprocess.check_output('/home/pi/getip.sh')
                        self.message_adapter.send_new_message(chat_id, message_text)
                    except FileNotFoundError:
                        self.message_adapter.send_new_message(chat_id, "I'm sorry, I don't know my IP!")
                elif text.startswith("!users") and chat_id in self.adminList:
                    message_text = "*Here is the usercount for this bot:*\n\n*Last 24 hours:*\n👥 " + str(get_playing_users(time.time() - 86400)) + "\n\n*Last 3 days:*\n👥 " + str(get_playing_users(time.time() - 259200))
                    self.message_adapter.send_new_message(chat_id, message_text, parse_mode="Markdown")
                    self.message_adapter.send_new_message(chat_id, get_highest_ranked_player())
                elif text.startswith("!id"):
                    self.message_adapter.send_new_message(chat_id, str(chat_id))
                elif text.startswith("!answer") and chat_id == self.DEV_ID:
                    text_orig = str(text_orig[8:])
                    if self.left_msgs[0][9] is not None and self.left_msgs[0][9] is not "":
                        try:
                            msg_chat_id = self.left_msgs[0][9]
                            answer_text = str(text_orig)
                        except:
                            msg_chat_id = "DEV_ID"
                            answer_text = "Fehler"
                    else:
                        try:
                            msg_list = text_orig.split("|")
                            answer_text = str(msg_list[0])
                            msg_chat_id = msg_list[1]
                        except:
                            self.message_adapter.send_new_message(self.DEV_ID, "Fehler bei answer")
                            msg_chat_id = "DEV_ID"
                            answer_text = "Fehler"
                    self.message_adapter.send_new_message(self.DEV_ID, "Ich habe deine Nachricht an den Nutzer weitergeleitet: \n\n" + answer_text + "\n\n(" + msg_chat_id + ")")
                    self.message_adapter.send_new_message(msg_chat_id, translation("thanksForComment", lang_id) + "\n" +
                                translation("answerFromDev", lang_id) + " \n\n" + answer_text + "\n\n" +
                                translation("clickCommentToAnswer", lang_id))

                elif user_id in self.CommentList:
                    self.message_adapter.send_new_message(chat_id, translation("userComment", lang_id))
                    self.message_adapter.send_new_message(self.DEV_ID,
                                "Nutzer Kommentar:\n\n" + str(text_orig + "\n\n" + str(user_id) + " | " + str(first_name) + " | " + str(last_name) + " | @" + str(username) + " | " + str(lang_id)))
                    self.CommentList.pop(self.CommentList.index(user_id))

                elif not chat_index == -1:
                    # If a game is present, send messages directly to that game
                    game = self.GameList[chat_index]
                    game.analyze_message(text, user_id, first_name, message_id)

                elif text.startswith(translation("startCmd", lang_id)) or str(text).startswith("start"):
                    if chat_index == -1:
                        self.add_to_game_list(chat_id, user_id, lang_id, game_type, first_name, message_id)
                    else:
                        self.message_adapter.send_new_message(chat_id, translation("alreadyAGame", lang_id), keyboard=keyboard_running)
                elif text.startswith("language"):
                    self.message_adapter.send_new_message(chat_id, translation("langSelect", lang_id), message_id=message_id, keyboard=self.keyboard_language)
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
                elif text.startswith("español"):
                    self.send_lang_changed_message(chat_id, message_id, "es", user_id)

                elif text.startswith("hide"):
                    self.message_adapter.hide_keyboard(chat_id, self.bot)
                elif text.startswith("stats"):
                    self.message_adapter.send_new_message(chat_id, get_user_stats(user_id), message_id)
                self.set_message_answered()
        except:
            self.message_adapter.send_new_message(self.DEV_ID, "Bot Error:\n\nNachrichten konnten nicht ausgewertet werden!")
            raise

    def __init__(self):
        print("Bot gestartet")

main = Main()
main.batch_run()