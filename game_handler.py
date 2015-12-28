__author__ = 'Rico'


# game_handler handles the blackJack objects. When a new object is created, it is saved in "GameList"
# getIndexByChatID returns the index of a running game in the list
# gl_create creates the GameList
# gl_remove delets the game from the list
class game_handler(object):

    GameList = []*0         # List, where the running Games are stored in
    game_id = 0

    def getIndexByChatID(self, chat_id, i=0):
        for x in self.GameList:
            if x.chat_id == chat_id:
                return i
            i += 1
        return -1

    def gl_create(self):
        self.GameList = []*0

    def gl_remove(self, chat_id):
        if not self.getIndexByChatID(chat_id) == -1:
            self.GameList.pop(self.getIndexByChatID(chat_id))

    def __init__(self, game_id=1):
        self.game_id = game_id
