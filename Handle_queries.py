from BotHandler import BotHandler
import requests
from enum import Enum
import threading
from datetime import datetime, date, time 

class Type(Enum) :
	photo = 1
	video = 2
	voice = 3
	audio = 4
	document = 5
	file = 6
	video_note = 7
	text = 8

class Method(Enum):
	sendPhoto = 1
	sendVideo = 2
	sendVoice = 3
	sendAudio = 4
	sendDocument= 5
	sendFile = 6
	sendVideoNote = 7
	sendMessage = 8

class Handle_queries :

	def __init__(self ):
		self.api_url = "https://api.telegram.org/bot402496318:AAFgpEa_wllKaR6wTcgO6Wnsu9QL4gNSzfg/"

	def plan_sending(self , message_list , channel_username , query , sending_time , delay = 0 ):
		if query == "set time" :
			threading.Timer(sending_time, self.sendAllTogehter , [ message_list , channel_username]).start()
		else :
			self.sendWithDelay( message_list , channel_username ,sending_time , delay)


	def ExtractFile_id(self , message , _type):
		if _type == "photo":
			return message[_type][0]['file_id']

		return message[_type]['file_id']	     


	def sendWithDelay(self , message_list , channel_username , sending_time , delay):
		c = -1
		for message in message_list : 
			c = c + 1 

			if message.has_key('sticker'):
				self.forward_message(message , channel_username , sending_time + c*delay)
				continue

			for t in Type :
				if message.has_key(t.name):
					if t.value == 8 :   # message is text and has no file id
						threading.Timer(sending_time + c*delay , bot.sendMessage , [channel_username , message['text']]).start()
					else :
						file_id = self.ExtractFile_id(message , t.name)
						caption = ""
						if message.has_key('caption') :
							caption = message['caption']
						threading.Timer(sending_time + c*delay , bot.sendFile , [channel_username , file_id , t.name ,  Method(t.value).name , caption]).start()
			

	def sendAllTogehter(self , message_list , channel_username):
		for message in message_list : 

			if message.has_key('sticker'):
				bot.forward_message(channel_username , message['chat']['id'] , message['message_id'])
				continue

			for t in Type :
				if message.has_key(t.name):
					if t.value == 8 :
						bot.sendMessage(channel_username , message['text'])
					else :
						file_id = self.ExtractFile_id(message , t.name)
						caption = ""
						if message.has_key('caption') :
							caption = message['caption']						
						bot.sendFile(channel_username , file_id , t.name , Method(t.value).name , caption)	

	def forward_message(self , message , channel_username , delay) :
		threading.Timer(delay , bot.forward_message , [channel_username , message['chat']['id'] , message['message_id']]).start()



bot = BotHandler()

