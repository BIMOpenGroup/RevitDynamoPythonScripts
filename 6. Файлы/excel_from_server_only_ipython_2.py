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


from System import Type, Activator
Excel = Activator.CreateInstance(Type.GetTypeFromProgID("Excel.Application"))


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
	
def rsnrequest_modelInfo(m_p):
	request = WebRequest.Create("http://"+revit_server_name+"/RevitServerAdminRESTService"+version+"/AdminRESTService.svc/|"+m_p+"|/modelInfo")		
	request.Method = "GET"
	request.Headers.Add("User-Name", os.environ.get('USERNAME'))
	request.Headers.Add("User-Machine-Name", os.getenv('COMPUTERNAME', 'defaultValue'))
	request.Headers.Add("Operation-GUID", Guid.NewGuid().ToString())

	rsp = request.GetResponse()
	stream_reader = StreamReader(rsp.GetResponseStream())

	jsonData = stream_reader.ReadToEnd()

	json = JavaScriptSerializer().DeserializeObject(jsonData)
	return (json)

	
def time_compare(current_time, test_time, row, sheet):
	test = []
	c_date = (current_time.split(" "))[0]
	t_date = (test_time.split(" "))[0]
	c_s = [int(c) for c in c_date.split(".")]
	t_s = [int(t) for t in t_date.split(".")]
	c_dt = DateTime(c_s[2],c_s[1],c_s[0]).Date
	t_dt = DateTime(t_s[2],t_s[1],t_s[0]).Date
	timedelta = c_dt.Subtract(t_dt).Days
	test.append(timedelta)
	#test.append([c_dt,t_dt])
	
	sheet.Cells(row,4).Interior.Color = 11711154
	test.append([c_date,t_date])
	#if c_date == t_date:
	if timedelta == 0:
		sheet.Cells(row,4).Interior.Color = 5296274
	elif timedelta > 0 and timedelta <= 7:
		sheet.Cells(row,4).Interior.Color = 6750207
	elif timedelta >= 8 and timedelta < 31:
		sheet.Cells(row,4).Interior.Color = 5263615
	return test
	
	
		
def folderpars2(folderslist,sheet):
	date = DateTime.Now.ToString()
	sheet.Cells(1,1).Value = "Дата обновления: "+str(date)
	list = []
	row = 3
	lRow = sheet.Cells(sheet.Rows.Count, 2).End(-4162).Row
	sheet.Range("A3:F"+str(lRow)).Delete()
	
	for fldr in folderslist:
		path = project_folder_name+"|"+fldr+"|"
		json = rsnrequest(project_folder_name+"|"+fldr)	
		model_data_list = json["Models"]
		models_list = [m["Name"] for m in model_data_list]
		row1 = row
		for model in models_list:
			sheet.Cells(row,1).Value = fldr
			sheet.Cells(row,1).HorizontalAlignment = -4108
			sheet.Cells(row,1).VerticalAlignment = -4108
			sheet.Cells(row,2).Value = model
			json3 = rsnrequest_modelInfo(path+model)
			sheet.Cells(row,3).Value = json3["DateCreated"]
			sheet.Cells(row,4).Value = json3["DateModified"]
			test.append(time_compare(date,str(json3["DateModified"]),row,sheet))
			sheet.Cells(row,5).Value = json3["LastModifiedBy"]
			sheet.Cells(row,6).Value = json3["ModelSize"]/1048576
			row +=1
		list1 = []
		Excel.DisplayAlerts = False
		aa = sheet.Cells(row1,1).Address(False, False)
		bb = sheet.Cells(row-1,1).Address(False, False)
		ab = str(aa)+":"+str(bb)
		sheet.Range(ab).Merge()
		list.append(ab)
	#sheet.Columns(1).Font.Bold = True
	#sheet.Columns(4).FormatConditions.AddColorScale(3)
	return [test,lRow,list]	

	
#-----------------------РАБОЧИЕ ПАРАМЕТРЫ----------------------

version = "2017"
revit_server_name = "" #Server name: ""
project_folder_name = "" #Project folder name: "Павлова 38"
path_to_copy = u'\\RS_Report.xlsx'
#path_to_copy = u'C:\\test\\RS_Report3.xlsx'
test = []

#-----------------------НАЧАЛО СКРИПТА----------------------


path = "rsn://"+revit_server_name+"/"+project_folder_name

json = rsnrequest(project_folder_name)
folder_data_list = json["Folders"]
find_folders_list = [m["Name"] for m in folder_data_list]

wb = Excel.Workbooks.Open(path_to_copy)
sheet = wb.ActiveSheet
json2 = folderpars2(find_folders_list,sheet)

wb.Save()
wb.Close()
Excel.Quit()

print json2

#OUT = json2