# -*- coding: utf-8 -*-
__author__ = 'Rico'

import subprocess
import time
import traceback

from app.gamehandler import GameHandler
from app.messageSenderAdapter import MessageSenderAdapter
from twx.botapi import TelegramBot

from app.update_handler import get_updates
from database.db_wrapper import sql_connect, sql_insert, check_if_user_saved, get_playing_users, get_last_players_list, user_data_changed, set_user_data, get_admins, add_admin, rm_admin, get_admins_id, reset_stats
from database.statistics import get_user_stats
from game.blackJack import BlackJack
from lang.language import translation


class Main(object):
    BOT_TOKEN = "<your_bot_token_here>"
    bot = TelegramBot(BOT_TOKEN)
    left_msgs = [[]] * 0
    offset = 0
    users = sql_connect() #TODO high memory usage due to in-memory storage without usage
    game_handler = GameHandler()
    GameList = game_handler.GameList
    CommentList = []
    DEV_ID = 24421134
    adminList = []
    message_adapter = MessageSenderAdapter(bot, 0)

    keyboard_language = [
        ["Deutsch 🇩🇪", "English 🇺🇸"],
        ["Português 🇧🇷", "Русский 🇷🇺", "Nederlands 🇳🇱"],
        ["Esperanto 🌍", "Español 🇪🇸", "فارسی 🇮🇷"]]

    def add_to_game_list(self, chat_id, user_id, lang_id, game_type, first_name, message_id):
        black_jack_game = BlackJack(chat_id, user_id, lang_id, game_type, first_name, self.game_handler, message_id, self.bot)
        self.game_handler.add_game(black_jack_game)

    def set_message_answered(self):
        if len(self.left_msgs) > 0:
            self.offset = self.left_msgs[0][1]
            self.left_msgs.pop(0)
            print("Un-Answered Messages: " + str(len(self.left_msgs)))

    def send_lang_changed_message(self, chat_id, message_id, lang_id, user_id):
        self.message_adapter.send_new_message(chat_id, translation("langChanged", lang_id), message_id=message_id, keyboard=[[translation("keyboardItemStart", lang_id)]])
        sql_insert("languageID", lang_id, user_id)  # TODO language setting for whole groups (low prio)

    def batch_run(self):
        while True:
            self.update_adapter()

    def update_adapter(self):
        templist = get_updates(self.offset, self.bot)
        if templist:
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
                lang_id = str(check_if_user_saved(user_id)[2])
                game_type = self.left_msgs[0][5]

                if user_data_changed(user_id, first_name, last_name, username):
                    set_user_data(user_id, first_name, last_name, username)

                chat_index = self.game_handler.get_index(chat_id)

                if text.startswith("/"):
                    text = str(text[1:])
                    text_orig = str(text_orig[1:])

                keyboard_running = [[translation("keyboardItemOneMore", lang_id), translation("keyboardItemNoMore", lang_id)], [translation("keyboardItemStop", lang_id)]]
                keyboard_not_running = [[translation("keyboardItemStart", lang_id)]]
                keyboard_cancel = [[translation("cancel", lang_id)]]

                if text.startswith("comment"):
                    text = str(text[7:])
                    if ((len(text) == 13 and text.startswith("@blackjackbot")) or (len(text) == 0)) or ((len(text) == 11 and text.startswith("@mytest_bot")) or (len(text) == 0)):
                        if user_id not in self.CommentList:
                            self.message_adapter.send_new_message(chat_id, translation("sendCommentNow", lang_id), message_id=message_id, keyboard=keyboard_cancel, force_reply=None)
                            self.CommentList.append(user_id)
                    else:
                        self.message_adapter.send_new_message(chat_id, translation("userComment", lang_id), keyboard=keyboard_not_running, force_reply=None)
                        self.message_adapter.send_new_message(self.DEV_ID, "Nutzer Kommentar:\n\n" + str(
                            text_orig[7:] + "\n\n" + str(user_id) + " | " + str(first_name) + " | " + str(last_name) + " | @" + str(username) + " | " + str(lang_id)))
                        if user_id in self.CommentList:
                            self.CommentList.pop(self.CommentList.index(user_id))

                elif text.startswith(translation("cancel", lang_id).lower()) and user_id in self.CommentList:
                    self.message_adapter.hide_keyboard(chat_id, translation("cancelledMessage", lang_id))
                    self.CommentList.pop(self.CommentList.index(user_id))

                elif user_id in self.CommentList:
                    self.message_adapter.send_new_message(chat_id, translation("userComment", lang_id), message_id=message_id, keyboard=keyboard_not_running, force_reply=None)
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
                    self.send_lang_changed_message(chat_id, message_id, "pt_BR", user_id)
                elif text.startswith("nederlands"):
                    self.send_lang_changed_message(chat_id, message_id, "nl", user_id)
                elif text.startswith("esperanto"):
                    self.send_lang_changed_message(chat_id, message_id, "eo", user_id)
                elif text.startswith("español"):
                    self.send_lang_changed_message(chat_id, message_id, "es", user_id)
                elif text.startswith("русский"):
                    self.send_lang_changed_message(chat_id, message_id, "ru", user_id)
                elif text.startswith("فارسی"):
                    self.send_lang_changed_message(chat_id, message_id, "fa", user_id)

                elif text.startswith("hide"):
                    self.message_adapter.hide_keyboard(chat_id)
                elif text.startswith("stats"):
                    self.message_adapter.send_new_message(chat_id, get_user_stats(user_id), message_id)
                elif text.startswith("reset"):
                    # TODO erneute Abfrage ob Stats resettet werden sollen!
                    reset_stats(user_id)
                    self.message_adapter.send_new_message(chat_id, "Statistics were reset!")

                elif text.startswith("!id"):
                    self.message_adapter.send_new_message(chat_id, str(chat_id))
                elif text.startswith("!answer") and chat_id == self.DEV_ID:
                    text_orig = str(text_orig[8:])
                    if self.left_msgs[0][9] is not None and self.left_msgs[0][9] is not "":
                        try:
                            msg_chat_id = self.left_msgs[0][9]
                            answer_text = str(text_orig)
                        except:
                            msg_chat_id = self.DEV_ID
                            answer_text = "Fehler"
                    else:
                        try:
                            msg_list = text_orig.split("|")
                            answer_text = str(msg_list[0])
                            msg_chat_id = msg_list[1]
                        except:
                            self.message_adapter.send_new_message(self.DEV_ID, "Fehler bei answer")
                            msg_chat_id = self.DEV_ID
                            answer_text = "Fehler"
                    user_lang_id = str(check_if_user_saved(msg_chat_id)[2])
                    # TODO throws TypeError when answering to the wrong message but doesn't crash
                    self.message_adapter.send_new_message(self.DEV_ID, "Ich habe deine Nachricht an den Nutzer weitergeleitet: \n\n" + answer_text + "\n\n(" + msg_chat_id + ")")
                    self.message_adapter.send_new_message(msg_chat_id, translation("thanksForComment", user_lang_id) + "\n" +
                                                          translation("answerFromDev", user_lang_id) + " \n\n" + answer_text + "\n\n" +
                                                          translation("clickCommentToAnswer", user_lang_id))

                elif user_id in self.adminList:
                    if text.startswith("!help"):
                        message_text = "*!help*     -  print this help\n" \
                                       "*!ip*          -  print ip address of the Pi\n" \
                                       "*!users*   -  show usercount\n" \
                                       "*!id*          -  show your Telegram ID\n" \
                                       "*!answer*  -  answer to a comment\n" \
                                       "*!games*  -  list number of active games\n" \
                                       "*!admins*  -  show all admins\n" \
                                       "*!addadmin*  -  add a new admin\n" \
                                       "*!rmadmin*  -  remove existing admins"

                        self.message_adapter.send_new_message(chat_id, message_text, parse_mode="Markdown")
                    elif text.startswith("!ip"):
                        try:
                            message_text = subprocess.check_output('/home/rico/getip.sh')
                            self.message_adapter.send_new_message(chat_id, message_text)
                        except FileNotFoundError:
                            self.message_adapter.send_new_message(chat_id, "I'm sorry, I don't know my IP!")
                    elif text.startswith("!users"):
                        message_text = "*Last 24 hours:*\n👥 " + str(get_playing_users(time.time() - 86400)) + "\n\n*Last 3 days:*\n👥 " + str(get_playing_users(time.time() - 259200))
                        self.message_adapter.send_new_message(chat_id, message_text, parse_mode="Markdown")
                        self.message_adapter.send_new_message(chat_id, get_last_players_list())
                    elif text.startswith("!games"):
                        self.message_adapter.send_new_message(chat_id, len(self.game_handler.GameList))
                    elif text.startswith("!admins"):
                        admin_dict = get_admins()
                        admin_str = ""

                        for admin in admin_dict:
                            admin_str += admin["first_name"] + " | " + str(admin["user_id"]) + " | "
                            if admin["username"] is not None and admin["username"] is not "":
                                admin_str += "@" + admin["username"]

                            admin_str += "\n"

                        self.message_adapter.send_new_message(chat_id, admin_str)

                    elif text.startswith("!addadmin"):
                        text_orig = str(text_orig[10:])
                        args = text_orig.split()
                        if len(args) < 3 and len(args) != 2:
                            self.message_adapter.send_new_message(chat_id, "Usage: !addadmin <user_id> <first_name> <username>")
                        elif len(args) == 2 or len(args) == 3:
                            a_user_id = a_first_name = a_username = ""

                            if len(args) == 2:
                                a_user_id, a_first_name = args
                            elif len(args) == 3:
                                a_user_id, a_first_name, a_username = args

                            return_val = add_admin(a_user_id, a_first_name, a_username)
                            if return_val is not 0:
                                self.message_adapter.send_new_message(chat_id, "There was an error adding an admin!")
                            else:
                                self.message_adapter.send_new_message(chat_id, "Admin added successfully!")
                                self.adminList = get_admins_id()

                    elif text.startswith("!rmadmin"):
                        text = str(text[9:])
                        if len(text) > 3 and len(text.split()) == 1:
                            a_user_id = text.split()
                            return_val = rm_admin(a_user_id)

                            if return_val is not 0:
                                self.message_adapter.send_new_message(chat_id, "There was an error removing an admin!")
                            else:
                                self.message_adapter.send_new_message(chat_id, "Admin removed successfully!")
                                self.adminList = get_admins_id()
                        else:
                            self.message_adapter.send_new_message(chat_id, "Usage: !rmadmin <user_id>")

                self.set_message_answered()
        except Exception as expt:
            print(expt)
            self.set_message_answered()
            self.message_adapter.send_new_message(self.DEV_ID, "Bot Error:\n\nNachrichten konnten nicht ausgewertet werden!")
            traceback.print_exc()

    def __init__(self):
        print("Bot gestartet")
        self.adminList = get_admins_id()
        print("Admins are:")
        print(self.adminList)

main = Main()
main.batch_run()
