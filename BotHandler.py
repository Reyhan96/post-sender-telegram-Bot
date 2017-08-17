import requests
import datetime


class BotHandler:

    def __init__(self):
        self.api_url = "https://api.telegram.org/bot402496318:AAFgpEa_wllKaR6wTcgO6Wnsu9QL4gNSzfg/"

    def get_myinfo(self ) :
        method = 'getMe'
        resp = requests.get(self.api_url + method)
        result_json = resp.json()
        return result_json['result']     

    def get_updates(self, offset=None, timeout=1 ):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset , 'allowed_updates' : ["message"] , 'limit' : 1}
        resp = requests.get(self.api_url + method, params)
        try :
            result_json = resp.json()
            return result_json['result']
        except:
            return None

    def forward_message(self, target_chat_id, from_chat_id , message_id):
        params = {'chat_id': target_chat_id, 'from_chat_id' : from_chat_id , 'disable_notification' : False , 'message_id' : message_id }
        method = 'forwardMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def sendMessage(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def sendFile(self , chat_id , file_id , _type , _method , caption) : # _type : photo,video,voice,...     _method = sendPhoto,sendVideo,sendVoice,....
        params = {'chat_id' : chat_id , _type : file_id , 'caption' : caption}
        params2 = {'chat_id' : chat_id , _type : file_id}
        if _method == "sendVideoNote" :
            params = params2 
        method = _method
        resp = requests.post(self.api_url + method, params)
        return resp


    def get_chatMember(self , chat_id , user_id) :
        params = {'chat_id': chat_id, 'user_id': user_id}
        method = 'getChatMember'
        resp = requests.get(self.api_url + method, params)
        return resp

    def get_admins(self , chat_id):
        params = {'chat_id': chat_id}
        method = 'getChatAdministrators'
        resp = requests.get(self.api_url + method, params)
        return resp.json()['result']

    def get_last_update(self):
        get_result = self.get_updates()
        if get_result == None :
            return None

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = None

        return last_update
