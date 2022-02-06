# -*- coding: utf-8 -*- 
#-----------------------Импоорт библиотек----------------------
import clr
import sys 
sys.path.append("C:\Program Files (x86)\IronPython 2.7\Lib")
import os

import System
from System import Guid
from System import DateTime
from System.IO import StreamReader
from System.Net import WebRequest
clr.AddReference('System.Web.Extensions')
from System.Web.Script.Serialization import JavaScriptSerializer 

clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import ModelPathUtils


clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager

#-----------------------ФУНКЦИИ----------------------

def rsnrequest(p_f_n):
	request = WebRequest.Create("http://"+revit_server_name+"/RevitServerAdminRESTService"+version+"/AdminRESTService.svc/|"+p_f_n+"|/contents")		
	request.Method = "GET"
	request.Headers.Add("User-Name", os.environ.get('USERNAME'))
	request.Headers.Add("User-Machine-Name", os.getenv('COMPUTERNAME', 'defaultValue'))
	request.Headers.Add("Operation-GUID", Guid.NewGuid().ToString())

	rsp = request.GetResponse()
	stream_reader = StreamReader(rsp.GetResponseStream())

	jsonData = stream_reader.ReadToEnd()

	json = JavaScriptSerializer().DeserializeObject(jsonData)
	return (json)

def folderpars(folderslist):
	date = DateTime.Today.ToString("d").split(".")
	date_revers = date[2]+"."+date[1]+"."+date[0]
	new_path_date = new_path_to_copy+"\\"+date_revers
	if not os.path.exists(new_path_date):
		os.makedirs(new_path_date)
	count = 0
	for fldr in folderslist:
			path = "rsn://"+revit_server_name+"/"+project_folder_name+"/"+fldr+"/"
			json = rsnrequest(project_folder_name+"|"+fldr)	
			model_data_list = json["Models"]
			models_list = [m["Name"] for m in model_data_list]
			for model in models_list:
				mpatch = ModelPathUtils.ConvertUserVisiblePathToModelPath(path+model)
				new_path_folder = new_path_date+"\\"+fldr
				if not os.path.exists(new_path_folder):
					os.makedirs(new_path_folder)
				app.CopyModel(mpatch,new_path_folder+"\\"+model,True)
				count +=1	
	return count	

#-----------------------АПИ ПАРАМЕТРЫ----------------------

app = DocumentManager.Instance.CurrentUIApplication.Application
version = app.VersionNumber

#-----------------------РАБОЧИЕ ПАРАМЕТРЫ----------------------

revit_server_name = IN[0] #Server name: ""
project_folder_name = IN[1] #Project folder name: ""
#new_path_to_copy = "C:\\test\\RevitServer_backup"
new_path_to_copy = "\\\BIM_архив\\RevitServer_backup" #IN[2] #New Path: 
folders_or_full_server = False #Копируем папки, или весь сервер: True/False
folders = IN[4] #Foldersе (через запятую): "КР,АР" итд

paths = []
input_folders_list = folders.split(",")
count = 0

#-----------------------НАЧАЛО СКРИПТА----------------------

if folders_or_full_server:
	count = folderpars(input_folders_list)
else:
	path = "rsn://"+revit_server_name+"/"+project_folder_name
	json = rsnrequest(project_folder_name)
	folder_data_list = json["Folders"]
	find_folders_list = [m["Name"] for m in folder_data_list]
	count = folderpars(find_folders_list)

OUT = count
