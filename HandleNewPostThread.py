import threading
from BotHandler import BotHandler
from Handle_queries import Handle_queries
from datetime import datetime, date, time , timedelta
import telepot
import pprint
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
# from Keyboard import Keyboard

TOKEN = "402496318:AAFgpEa_wllKaR6wTcgO6Wnsu9QL4gNSzfg"
telebot = telepot.Bot(TOKEN)
bot = BotHandler()
botUserID = bot.get_myinfo()['id']
# keyboard = Keyboard()

class HandleNewPostThread (threading.Thread):
   def __init__(self, chat_id , token): # chatID-thread is a dict
      threading.Thread.__init__(self)
      self.lock1 = threading.Lock()
      self.lock1.acquire()
      self.lock2 = threading.Lock()
      self.chat_id = chat_id
      self.token = token
      self.last_update = None
      # self.startpost_message_id = 0
      # self.stoppost_message_id = 0
      # self.channel_username = None
      self.first_step = False # send /newposts
      self.second_step = False # give username and check validity 
      self.third_step = False # send /startposts
      self.forth_step = False # send /stopposts
      self.keyboard = False # choose between time interval or set time
      # self.setTimeOrInterval = False  # True = set time , False = time interval
      self.fifth_1_step = False # set time
      self.fifth_2_step = False # set interval
      self.finish = False

      self.introduce()

   def run(self):
      message_list = []

      while not self.finish :
         self.lock1.acquire()
         last_update = self.last_update
         self.check_for_repeat_an_operation(last_update , message_list)

         if not self.first_step :
            self.get_newpost_command(last_update)

         elif not self.second_step :
            channel_username = self.validate_admins(last_update)

         elif not self.third_step :
            self.get_startpost_command(last_update)

         elif not self.forth_step :
            self.addToList(message_list , last_update )
            self.get_stoppost_command(last_update)

         elif not self.keyboard :
            del message_list[-1] # because the last message is /stoppost command
            query_data = self.handle_keyboard(last_update)

         elif not self.fifth_1_step: 
            sending_time = self.settime(last_update)           
            if sending_time:
               self.fifth_1_step = True
               if query_data == "set time" :
                  self.fifth_2_step = True
                  self.finish = True
                  self.send_posts(message_list , channel_username ,  query_data , sending_time , 0 )
               else : 
                  bot.sendMessage(self.chat_id , "please enter the time interval between your posts ")
            else :
               bot.sendMessage(self.chat_id , "please enter the time in correct format !" )

         elif not self.fifth_2_step :
            time_interval = self.set_time_interval(last_update)
            if time_interval :
               print time_interval
               self.fifth_2_step = True
               self.finish = True
               self.send_posts(message_list , channel_username , query_data , sending_time , time_interval)
            else :
               bot.sendMessage(self.chat_id , "please enter the time in correct format !" )

         self.lock2.release()


   def introduce(self) :
      text = "Hi !\nTo work with this bot,\n1- Your channel should be public.\n2- Add me to your channel as an adminisrator that can post message .\n3- You should be an admin that can post messages to the channel.\nthen send me '/newposts' "
      bot.sendMessage(self.chat_id , text)

   def handle_last_update(self , last_update) :
      self.lock2.acquire()
      self.last_update = last_update
      self.lock1.release()

   def check_for_repeat_an_operation(self , last_update , message_list) :
      flag , msg = self.check_text("/newposts" , last_update) 
      if flag :
         self.reset()
         return
      flag , msg = self.check_text("/startposts" , last_update) 
      if flag :
         message_list[:] = []
         self.third_step = False # send /startposts
         self.forth_step = False # send /stopposts
         self.keyboard = False # choose between time interval or set time
         self.fifth_1_step = False # set time
         self.fifth_2_step = False # set interval
         self.finish = False

   def get_newpost_command(self, last_update) :
      resp , msg = self.check_text("/newposts" , last_update) 
      if resp :
         self.first_step = True
         bot.sendMessage(self.chat_id , "Ok ! send me the channel username in this form : @channel_name")

   def check_text(self , desired_text , last_update):

      response , msg = self.extract_keyOFMessage(last_update)
      if not response :
         return False , None

      if last_update[msg].has_key('text'):
         if last_update[msg]['text'] == desired_text :
            return True , msg
         else :
            return False , None
      else :
         return False , None

   def extract_keyOFMessage(self , last_update):
      if(last_update.has_key("message")) :
         return True , "message"
      elif (last_update.has_key("edited_message")) :
         return True , "edited_message"
      else :
         return False , None      

   def get_admins(self, last_update):
      response , msg = self.extract_keyOFMessage(last_update)
      if not response :
         return None

      if last_update[msg].has_key('text'):
         try :
            self.channel_username = last_update[msg]['text']
            admins = bot.get_admins(last_update[msg]['text'])
            return admins , msg
         except :
            return None , None
      else :
         return None , None

   def validate_admins(self , last_update) :
      bot_is_valid = False
      user_is_valid = False
      admins , msg= self.get_admins(last_update)

      if admins == None :
         bot.sendMessage(self.chat_id , "your message is not a channel username or I'm not an adminstrator in this channel !")
         return None
      else :
         for admin in admins :
            if (admin['user']['id'] == self.chat_id and (admin['status'] == 'creator' or admin['status'] == 'administrator' and admin['can_post_messages']))  :
               user_is_valid = True
            elif admin['user']['id'] == botUserID and admin['can_post_messages'] :
               bot_is_valid = True

      if bot_is_valid and user_is_valid :
         self.second_step = True
         bot.sendMessage(self.chat_id , "good ! now send me the /startposts command to continue . ")
         return last_update[msg]['text']
      else :
         bot.sendMessage(self.chat_id , "You are not an admin that can post messages or I cant post messages !")
         return None

   def get_startpost_command(self , last_update) :
      resp , msg = self.check_text("/startposts" , last_update) 
      if resp :
         self.third_step = True
         bot.sendMessage(self.chat_id , "Allright ! send posts you want to send to the channel.\nAfter sending All your posts send /stopposts command.\nIf you want to edit your messages you can do it just before sending /stopposts command .after sending this command your messages will save and they won't change.")
         # return last_update['update_id'] , last_update[msg]['message_id']
      else :
         bot.sendMessage(self.chat_id , "first you should send me '/startposts'")
         # return None , None

   def addToList(self , message_list , last_update) :
      if last_update.has_key("message"):
         message_list.append(last_update['message'])
      elif last_update.has_key("edited_message"):
         for i in range(0 , len(message_list)) :
            if message_list[i]['message_id'] == last_update['edited_message']['message_id'] :
               message_list[i] = last_update['edited_message']

   def get_stoppost_command(self , last_update):
      resp , msg = self.check_text("/stopposts" , last_update) 
      if resp:
         self.forth_step = True

         keyboard = InlineKeyboardMarkup(inline_keyboard = [
         [InlineKeyboardButton(text = 'time interval between posts', callback_data = 'interval')],
         [InlineKeyboardButton(text = 'set time for sending posts', callback_data = 'set time')],
         ])

         telebot.sendMessage(self.chat_id, "please choose in which model you want to handle your posts ?", reply_markup = keyboard)
         # return last_update['update_id'] , last_update[msg]['message_id']

      # return None , None

   def handle_keyboard(self , last_update):

      if last_update.has_key('callback_query') :
         if last_update['callback_query']['data'] == "set time" :
            query_data = 'set time'
         elif last_update['callback_query']['data'] == "interval":
            query_data = 'set interval'

         query_id = last_update['callback_query']['id']
         telebot.answerCallbackQuery(query_id , text = query_data)
         self.keyboard = True
         self.sendMessage_to_enter_time(query_data)
         return query_data

      else :
         telebot.sendMessage(self.chat_id, 'please choose by keyboard button ')

   def sendMessage_to_enter_time(self , query_data) :

      if query_data == "set time" :
         telebot.sendMessage(self.chat_id, "All Right ! when you want your posts to be send ?\nyou can just set time for 24 hours from now !!\nplease enter in this form : \nHH:MM ")
      else :
         telebot.sendMessage(self.chat_id, "All Right ! when you want your 'first' post send ?\nyour entry should be less than 24 hours !\nplease enter in this form : \nHH:MM ")

   def settime(self , last_update ):
      response , msg = self.extract_keyOFMessage(last_update)
      if not response :
         return None

      if last_update[msg].has_key('text'):
         text = last_update[msg]['text']
         time_is_correct , delay = self.get_delay(text)

         if time_is_correct :
            # send_posts(self.channel_username , self.chat_id , self.startpost_message_id + 2 , self.stoppost_message_id, delay)
            self.fifth_1_step
            return delay
         else :
            return None
      else :
         return None 


   def set_time_interval(self , last_update ):
      response , msg = self.extract_keyOFMessage(last_update)
      if not response :
         return None

      if last_update[msg].has_key('text'):
         text = last_update[msg]['text']
         time_is_correct , hour , minute = self.check_correctness_of_input_time(text)
         if not time_is_correct :
            return None

         delay = timedelta(hours = hour , minutes = minute)
         delay_seconds = delay.total_seconds()

         bot.sendMessage(self.chat_id , "successfully done ! your messages scheduled to be sent with "+ str(delay)+" delay :))")

         return delay_seconds


   def get_delay(self , text):
      time_is_correct  , hour , minute = self.check_correctness_of_input_time(text)
      if not time_is_correct :
         return False , None

      server_time = datetime.now()
      iran_time = server_time #+ timedelta(hours = 4 , minutes = 30) 
      x = time(iran_time.hour , iran_time.minute , 0)
      y = time(hour, minute , 0)
      one_day = timedelta(days=1)

      if x < y :
         diff = datetime.combine(date.today(), y) - datetime.combine(date.today(), x)
      else :
         diff = datetime.combine(date.today() + one_day , y) - datetime.combine(date.today(), x)

      bot.sendMessage(self.chat_id , "successfully done ! your message will be send " + str(diff) + " from now :))")
      return True , diff.total_seconds()

   def check_correctness_of_input_time(self , text):
      t = text.split(":")
      if len(text) > 5 or len(t[0]) > 2 or len(t[0]) < 1 or len(t[1]) > 2 or len(t[1]) < 1  : # 22:33 total length = 5 and each half = 2
         return False , None , None

      try :
         hour = int(t[0])
         minute = int(t[1])
      except :
         return False , None , None

      if not 0<= hour < 24 :
         return False , None , None
      if not 0<= minute < 60 :
         return False , None , None

      return True , hour , minute

   def reset(self):
      self.startpost_message_id = 0
      self.stoppost_message_id = 0
      self.channel_username = None
      self.first_step = False # send /newposts
      self.second_step = False # be valid 
      self.third_step = False # send /startposts
      self.forth_step = False # send /stopposts
      self.fifth_1_step = False # set time
      self.fifth_2_step = False # interval
      self.finish = False




   def send_posts(self , message_list, channel_username , query_data , sending_time , time_interval) :
      handler = Handle_queries()
      handler.plan_sending(message_list , channel_username , query_data , sending_time , time_interval)

def prettyprint(text) :
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(text)