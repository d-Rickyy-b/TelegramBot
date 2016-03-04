__author__ = 'Rico'
from twx.botapi import ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply


def sendmessage(chat_id, message_text, bot, message_id=None, keyboard=None, one_time_keyboard=None, force_reply=None, parse_mode="Markdown"):
    if force_reply is not None:
        bot.send_message(chat_id, message_text, reply_to_message_id=message_id, reply_markup=ForceReply.create(selective=True), parse_mode=parse_mode).wait()
    elif keyboard is not None:
        reply_markup = ReplyKeyboardMarkup.create(keyboard, selective=True, one_time_keyboard=one_time_keyboard)
        bot.send_message(chat_id, message_text, reply_to_message_id=message_id, reply_markup=reply_markup, parse_mode=parse_mode).wait()
    else:
        bot.send_message(chat_id, message_text, reply_to_message_id=message_id, parse_mode=parse_mode).wait()

def hide_keyboard(chat_id, bot, text=None):
    reply_markup = ReplyKeyboardHide.create()
    if text is None:
        text = "👍"
    bot.send_message(chat_id, text, reply_markup=reply_markup).wait()
