__author__ = 'Rico'
from twx.botapi import ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply


class messageSenderAdapter(object):
    def sendmessage(self, chat_id, message_text, bot, message_id=None, keyboard=None, one_time_keyboard=None, force_reply=None):
        if force_reply is not None:
            bot.send_message(chat_id, message_text, reply_to_message_id=message_id, reply_markup=ForceReply.create(selective=True), parse_mode="Markdown")
        if keyboard is not None:
            reply_markup = ReplyKeyboardMarkup.create(keyboard, selective=True, one_time_keyboard=one_time_keyboard)
            bot.send_message(chat_id, message_text, reply_to_message_id=message_id, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, message_text, reply_to_message_id=message_id, parse_mode="Markdown")
        self.clear_message()

    def send_joined_message(self, ):
        self.sendmessage(self.chat_id, self.text, self.bot, self.message_id, self.keyboard, self.one_time_keyboard)

    def add_to_message(self, text):
        self.text += text

    def set_metadata(self, message_id=None, keyboard=None, one_time_keyboard=None):
        self.message_id = message_id
        self.keyboard = keyboard
        self.one_time_keyboard = one_time_keyboard

    def hide_keyboard(self, chat_id, bot, text=None):
        reply_markup = ReplyKeyboardHide.create()
        if text is None:
            text = "👍"
        bot.send_message(chat_id, text, reply_markup=reply_markup).wait()
        self.clear_message()

    def clear_message(self):
        self.text = ""
        self.message_id = 0
        self.keyboard = None
        self.one_time_keyboard = None

    def __init__(self, bot, chat_id):
        self.bot = bot
        self.text = ""
        self.chat_id = chat_id
        self.message_id = 0
        self.keyboard = None
        self.one_time_keyboard = None
