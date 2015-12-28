__author__ = 'Rico'
from twx.botapi import TelegramBot, ReplyKeyboardMarkup, ReplyKeyboardHide


BOT_TOKEN_Test = "93649491:AAGqs2JEuCZuq7qBgei7-6x2ObXwXft76kA"
BOT_TOKEN = "118984346:AAGUCYlSYNlj05Djh1XyixYNKNCZifG13ko"


def sendmessage(chat_id, message_text, message_id=None, keyboard=None, one_time_keyboard=None, force_reply=None):
    bot = TelegramBot(BOT_TOKEN)

    if keyboard is not None:
        reply_markup = ReplyKeyboardMarkup.create(keyboard, selective=True, one_time_keyboard=one_time_keyboard)
        bot.send_message(chat_id, message_text, reply_to_message_id=message_id, reply_markup=reply_markup).wait()
    else:
        bot.send_message(chat_id, message_text, reply_to_message_id=message_id).wait()


def hide_keyboard(chat_id, text=None):
    reply_markup = ReplyKeyboardHide.create()
    bot = TelegramBot(BOT_TOKEN)
    if text is None:
        text = "👍"
    bot.send_message(chat_id, text, reply_markup=reply_markup).wait()
