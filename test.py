# Load the Python Standard and DesignScript Libraries
import sys
sys.path.append(u'C:\\Program Files (x86)\\IronPython 2.7\\Lib')
import json
import clr
import re

import System
from System import DateTime, Text, Environment
from System.Text import Encoding
clr.AddReference('System.Web.Extensions')
from System.Net import WebRequest, ServicePointManager, SecurityProtocolType

clr.AddReference('DynamoRevitDS')
import Dynamo
#access to the current Dynamo instance and workspace
dynamoRevit = Dynamo.Applications.DynamoRevit()
currentWorkspace = dynamoRevit.RevitDynamoModel.CurrentWorkspace

def remove_bad_requestl_symbols(text_to_clear):
	return re.sub('[!@#$_]', ' ', text_to_clear)

dyn_file_name = remove_bad_requestl_symbols(currentWorkspace.Name)

def telegram_bot_sendmessage(bot_message):
	bot_message = remove_bad_requestl_symbols(bot_message)
	bot_token = "5366350020:AAFmLWCOy2FLKVw7ksmmjkt35nHdUUgbk3E"
	#bot_chatID = "236079948" #user id
	bot_chatID = "-1001782932924" #chat_id
	#send_text = telegram_bot_sendmessage("{1}\n{2}".format())
	send_text = "https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&parse_mode=Markdown&text={2}\nuser: {3}\ndyn: {4}\n🐈{5}".format(bot_token, bot_chatID, str(DateTime.Now), Environment.UserName, dyn_file_name, bot_message) #dir
	#send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
	#send_text = "https://api.telegram.org/bot5366350020:AAFmLWCOy2FLKVw7ksmmjkt35nHdUUgbk3E/getMe"
	#send_text = 'https://api.telegram.org/bot5366350020:AAFmLWCOy2FLKVw7ksmmjkt35nHdUUgbk3E/getUpdates?offset=469437945'
	#send_text = "https://api.telegram.org/bot5366350020:AAFmLWCOy2FLKVw7ksmmjkt35nHdUUgbk3E/sendMessage?chat_id=236079948&parse_mode=Markdown&text=test"
	#ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12
	request = WebRequest.Create(send_text)
	rsp = request.GetResponse()
	#stream_reader = StreamReader(rsp.GetResponseStream())
	#jsonData = stream_reader.ReadToEnd()
	#json_deserialaized = JavaScriptSerializer().DeserializeObject(jsonData)
	#return json_deserialaized


telegram_bot_sendmessage("test_message")

OUT = dyn_file_name