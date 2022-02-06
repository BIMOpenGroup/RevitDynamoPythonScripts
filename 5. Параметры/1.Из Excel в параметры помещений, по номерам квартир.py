import clr

clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

from time import time
tic = time()

doc = DocumentManager.Instance.CurrentDBDocument

elements_list1 = IN[0]
dict_list1 = IN[1]
elements_list2 = IN[2]
dict_list2 = IN[3]
d = {}

rooms_list = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms)

dict_excel = dict(zip(dict_list1, elements_list1))
x=0
y=0

"""
TransactionManager.Instance.EnsureInTransaction(doc)
for r in rooms_list:
	if "a" in r.LookupParameter(param_get).AsString():
		x=x+1
		for d in dict_excel:	
			if str(d) == r.LookupParameter(param_get).AsString():
				y=y+1
				
				(r.LookupParameter(param_set)).Set((float(dict_excel[d])*10.7639)) #Convert square foot to square meter
				
			else:
				pass
	else:
		pass
TransactionManager.Instance.TransactionTaskDone()
"""
		
toc = time()

xx=float(dict_excel[d])
yy=dict_excel[d]

all_time=toc-tic
OUT = x,y,all_time,xx,yy
