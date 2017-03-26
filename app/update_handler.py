# -*- coding: utf-8 -*-
__author__ = 'Rico'
import datetime
import re

from database.db_wrapper import DBwrapper


def get_updates(offset, bot):
    updates = bot.get_updates(offset + 1).wait()
    returnlist = []

    if bool(updates) and updates:
        print("\n--- Processing updates: ---")
        for update in updates:
            if update is not None:
                try:
                    db = DBwrapper.get_instance()
                    templist = []
                    user_id = update.message.sender.id
                    first_name = update.message.sender.first_name
                    last_name = update.message.sender.last_name
                    username = update.message.sender.username
                    chat_id = update.message.chat.id
                    message_id = update.message.message_id
                    update_id = update.update_id
                    text = update.message.text
                    upd_time = int(update.message.date)
                    reply_message_text = ""

                    if update.message.reply_to_message is not None:
                        reply_message_text = update.message.reply_to_message.text

                        if reply_message_text is not None:
                            try:
                                pattern = re.compile("([0-9]{5,}) \|")  # pretty weak detection of a userid in the answer (regarding /comment feature)
                                reply_message_text = pattern.search(reply_message_text).group(1)
                            except:
                                reply_message_text = ""

                    if username is None:
                        username = ""
                    if last_name is None:
                        last_name = ""

                    if db.is_user_saved(user_id) == False:
                        db.add_user(user_id, "en", first_name, last_name, username)  # add new user to db

                    if chat_id > 0:
                        chat_type = "0"
                    else:
                        chat_type = "1"

                    st = datetime.datetime.fromtimestamp(upd_time).strftime('%Y-%m-%d %H:%M:%S')  # TODO print the time, the message was received by the server
                    print(st + "  -  Vorname: " + str(first_name) + " | Nachname: " + str(last_name) + " | Username: " + str(username) + " | UserID: " + str(user_id) + " | ChatType: " + str(chat_type) + " | Nachricht: " + str(text))
                    templist.extend((user_id, update_id, first_name, last_name, text, chat_type, chat_id, message_id, username, reply_message_text))
                    returnlist.append(templist)
                except AttributeError as attibuteError:
                    print("AttributeError ist aufgetreten!\n")
                    print(update)
                    print(attibuteError)
        return returnlist
    else:
        return None
