__author__ = 'Rico'
from twx.botapi import TelegramBot, ReplyKeyboardMarkup, ReplyKeyboardHide


def sendmessage(chat_id, message_text, BOT_TOKEN, message_id=None, keyboard=None, one_time_keyboard=None, force_reply=None):
    bot = TelegramBot(BOT_TOKEN)

    if keyboard is not None:
        reply_markup = ReplyKeyboardMarkup.create(keyboard, selective=True, one_time_keyboard=one_time_keyboard)
        bot.send_message(chat_id, message_text, reply_to_message_id=message_id, reply_markup=reply_markup).wait()
    else:
        bot.send_message(chat_id, message_text, reply_to_message_id=message_id).wait()


def hide_keyboard(chat_id, BOT_TOKEN, text=None):
    reply_markup = ReplyKeyboardHide.create()
    bot = TelegramBot(BOT_TOKEN)
    if text is None:
        text = "👍"
    bot.send_message(chat_id, text, reply_markup=reply_markup).wait()
