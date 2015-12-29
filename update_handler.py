__author__ = 'Rico'
from twx.botapi import TelegramBot, botapi
from messageSender import sendmessage
from sql_handler import check_if_user_saved, sql_write
import datetime, time


def getUpdates(offset, BOT_TOKEN):
    bot = TelegramBot(BOT_TOKEN)
    updates = bot.get_updates(offset+1).wait()
    returnList = [[]]*0

    try:
        if updates is not None:
            for update in updates:
                if update is not None:
                    print("\n--- Processing updates: ---")

                    templist = []*0
                    user_id = update.message.sender.id
                    first_name = update.message.sender.first_name
                    last_name = update.message.sender.last_name
                    username = update.message.sender.username
                    chat_id = update.message.chat.id
                    message_id = update.message.message_id

                    if username is None:
                        print("Username is None")
                        username = ""
                    if last_name is None:
                        print("last_name is None")
                        last_name = ""
                    update_id = update.update_id
                    text = update.message.text
                    user_index = check_if_user_saved(user_id)

                    if user_index == -1:  # and chat_id == user_id:
                        print("New User")
                        tmp = []*0
                        tmp.extend(("", user_id, "en", first_name, last_name, username, 0, 0, 0, 0))
                        sql_write(user_id, "en", first_name, last_name, username)  # neuen Nutzer hinzufügen
                        text = "noText"

                    if type(update.message.chat) == botapi.User:
                        chat_type = "0"
                    elif type(update.message.chat) == botapi.GroupChat:
                        chat_type = "1"

                    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                    print(st + "  -  Vorname: " + str(first_name) + " | Nachname: " + str(last_name) + " | Username: " + str(username) + " | UserID: " + str(user_id) + " | ChatType: " + str(chat_type) + " | Nachricht: " + str(text))
                    templist.extend((user_id, update_id, first_name, last_name, text, chat_type, chat_id, message_id))
                    returnList.append(templist)

            return returnList
    except:
        print("ERROR IST AUFGETRETEN!")
        sendmessage(24421134, "Bot Error:\n\nNachrichten konnten nicht empfangen werden!", BOT_TOKEN)
        raise
