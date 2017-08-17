import requests  
import datetime
import pprint
import json
from BotHandler import BotHandler
from HandleNewPostThread import HandleNewPostThread
import threading
# from SchedulerThread import SchedulerThread

token = "402496318:AAFgpEa_wllKaR6wTcgO6Wnsu9QL4gNSzfg"
chatID_thread = {}
botUserID = None

class UpdateHandler:

    def __init__(self , BotHandler):
        self.BotHandler = BotHandler
        self.update_id = None
        self.chat_id = None

    def handle_update(self , last_update) :    

        response , chat_id = self.extract_chat_id(last_update)
        if not response :
            return

        if chatID_thread.has_key(chat_id) :
            thread = chatID_thread[chat_id]
            if (thread.isAlive()) : 
                thread.handle_last_update(last_update)
            else : 
                print "the threade has finished"
                self.create_new_thread(chatID_thread , chat_id , last_update)

        else :
            self.create_new_thread(chatID_thread , chat_id , last_update)

    def create_new_thread(self , _dict , chat_id , last_update):
        new_post_handler = HandleNewPostThread(chat_id , token )
        new_post_handler.handle_last_update(last_update)
        new_post_handler.start()
        if _dict.has_key(chat_id) :
            _dict[chat_id] = new_post_handler
        else :
            _dict.setdefault(chat_id , new_post_handler )
            saveUsernames(last_update)

    def extract_chat_id(self , last_update):

        if(last_update.has_key("message")) :
            return True , last_update['message']['chat']['id']
        elif (last_update.has_key("edited_message")) :
            return True , last_update['edited_message']['chat']['id']
        elif (last_update.has_key('callback_query')) :
            return True , last_update['callback_query']['message']['chat']['id']
        else :
            return False , None 


        

def prettyprint(text) :
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(text)

def saveUsernames(last_update) :
    with open('profiles.txt' , 'a') as f:
        f.write(json.dumps(last_update))
        f.write('\n') 


bot = BotHandler()
botUserID = bot.get_myinfo()['id']
update_handler = UpdateHandler(bot)  

def main():  
    new_offset = None

    while True:
        bot.get_updates(new_offset) # this part get the messages with update id greater than new offset
        last_update = bot.get_last_update()
        if (last_update) :
            last_update_id = last_update['update_id']
            update_handler.handle_update(last_update)

            new_offset = last_update_id + 1



if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()