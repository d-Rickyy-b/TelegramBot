# TelegramBot
This is the code for my Telegram Bot. You can find it here: https://telegram.me/BlackJackBot

The main file is - as the name already says - main.py
You need to put your API-Token in the right place.

It fetches updates once a second.

The bot has a command "!ip" to get the IP from inside the bot. If you don't want that feature, comment the line. If you want it you need a script returning the IP. I will uploade one, if you request it.

## Database

To set up the database, you need two tables:

1) ```CREATE TABLE 'admins' ('userID'	INTEGER NOT NULL,	'first_name'	TEXT,	'username'	TEXT,	PRIMARY KEY('userID'));```

2) ```CREATE TABLE 'users' ('userID'	INTEGER NOT NULL,	'languageID'	TEXT,	'first_name'	TEXT,	'last_name'	TEXT,	'username'	TEXT, 'gamesPlayed'	INTEGER,	'gamesWon'	INTEGER,	'gamesTie'	INTEGER,	'lastPlayed'	INTEGER,	PRIMARY KEY('userID'));```
