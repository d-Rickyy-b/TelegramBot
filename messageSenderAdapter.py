__author__ = 'Rico'
from twx.botapi import ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply


class MessageSenderAdapter(object):
    def __sendmessage(self):
        if self.force_reply is not None:
            self.bot.send_message(self.chat_id, self.text, reply_to_message_id=self.message_id, reply_markup=ForceReply.create(selective=True), parse_mode=self.parse_mode)
        elif self.keyboard is not None:
            reply_markup = ReplyKeyboardMarkup.create(self.keyboard, selective=True, one_time_keyboard=self.one_time_keyboard)
            self.bot.send_message(self.chat_id, self.text, reply_to_message_id=self.message_id, reply_markup=reply_markup, parse_mode=self.parse_mode)
        else:
            self.bot.send_message(self.chat_id, self.text, reply_to_message_id=self.message_id, parse_mode=self.parse_mode)
        self.clear_message()

    def send_new_message(self, chat_id, message_text, message_id=None, keyboard=None, one_time_keyboard=None, force_reply=None, parse_mode=None):
        self.text = message_text
        self.chat_id = chat_id
        self.message_id = message_id
        self.keyboard = keyboard
        self.one_time_keyboard = one_time_keyboard
        self.force_reply = force_reply
        self.parse_mode = parse_mode
        self.__sendmessage()

    def send_joined_message(self):
        self.__sendmessage()

    def add_to_message(self, text):
        self.text += text

    def set_metadata(self, message_id=None, keyboard=None, one_time_keyboard=None, parse_mode=None):
        if not message_id is None: self.message_id = message_id
        if not keyboard is None: self.keyboard = keyboard
        if not one_time_keyboard is None:self.one_time_keyboard = one_time_keyboard
        if not parse_mode is None:self.parse_mode = parse_mode

    def hide_keyboard(self, chat_id, text=None):
        reply_markup = ReplyKeyboardHide.create()
        if text is None:
            text = "👍"#Thumbs up emoji
        self.bot.send_message(chat_id, text, reply_markup=reply_markup).wait()
        self.clear_message()

    def clear_message(self):
        self.text = ""
        self.message_id = None
        self.keyboard = None
        self.one_time_keyboard = None

    def __init__(self, bot, chat_id):
        self.bot = bot
        self.text = ""
        self.chat_id = chat_id
        self.message_id = None
        self.keyboard = None
        self.one_time_keyboard = None
        self.force_reply = None
        self.parse_mode = None

