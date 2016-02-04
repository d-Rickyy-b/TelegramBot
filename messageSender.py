__author__ = 'Rico'
from twx.botapi import ReplyKeyboardMarkup, ReplyKeyboardHide


def sendmessage(chat_id, message_text, bot, message_id=None, keyboard=None, one_time_keyboard=None, force_reply=None):
    if keyboard is not None:
        reply_markup = ReplyKeyboardMarkup.create(keyboard, selective=True, one_time_keyboard=one_time_keyboard)
        bot.send_message(chat_id, message_text, reply_to_message_id=message_id, reply_markup=reply_markup, parse_mode="Markdown").wait()
    else:
        bot.send_message(chat_id, message_text, reply_to_message_id=message_id).wait()

def hide_keyboard(chat_id, bot, text=None):
    reply_markup = ReplyKeyboardHide.create()
    if text is None:
        text = "👍"
    bot.send_message(chat_id, text, reply_markup=reply_markup).wait()
