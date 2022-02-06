# -*- coding: utf-8 -*-

#-----------------------Импоорт библиотек----------------------
import clr
from System import *#Guid
clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager

clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *
#-----------------------Функции----------------------		


def selection_set_modif(__SELECTION_SET__,cat,type):
	return __SELECTION_SET__.replace("__CATEGORY__",cat).replace("__SELECTIONSET_NAME__",type).replace("__SELECTIONSET_GUID__",Guid.NewGuid().ToString()).replace("__CONDITIONS__",next(cond for cond in conditions if "__TYPE_NAME__" in cond)).replace("__TYPE_NAME__",type)

#-----------------------Рабочие параметры----------------------	
doc = DocumentManager.Instance.CurrentDBDocument

__FOLDER_1_GUID__ = Guid.NewGuid().ToString()

xml_part_ONE_folder1 = IN[0]
__FOLDER_1__ = IN[1]
xml_part_TWO_folder2 = IN[2]
folders_2 = IN[3]
__FOLDER_2_SET__ = ""
__SELECTION_SET__ = IN[4].replace("__FILE_TITLE__",doc.Title)
selection_set = ""
#elements_by_cat = {cat: elements for cat,elements in zip(folders_2,IN[5])}
elements_by_cat = {cat: set() for cat in folders_2}
conditions = IN[6]
test = []

for cat,elements in zip(folders_2,UnwrapElement(IN[5])):
	if cat != "Части":
		for e in elements:
			elements_by_cat[cat].add(e.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString())
	else:
		for e in elements:
			if e.GetType().Name == "DirectShape":
				elements_by_cat[cat].add(e.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString())
			else:
				elements_by_cat[cat].add(doc.GetElement(e.GetSourceElementIds()[0].HostElementId).get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString())

xml_full = xml_part_ONE_folder1.replace("__FOLDER_1__",__FOLDER_1__)
xml_full = xml_full.replace("__FOLDER_1_GUID__",__FOLDER_1_GUID__)

#for f in folders_2:
#	__FOLDER_2_SET__ += (xml_part_TWO_folder2.replace("__FOLDER_2__",f).replace("__FOLDER_2_GUID__",Guid.NewGuid().ToString()) + "\r\n") 
for cat,items in elements_by_cat.items():
	selection_set = ""
	if cat == "Части":
		for type in items:
			selection_set += selection_set_modif(__SELECTION_SET__,"Стены",type)#__SELECTION_SET__.replace("__CATEGORY__","Стены").replace("__SELECTIONSET_NAME__",type).replace("__SELECTIONSET_GUID__",Guid.NewGuid().ToString()).replace("__CONDITIONS__",next(cond for cond in conditions if "__TYPE_NAME__" in cond)).replace("__TYPE_NAME__",type)
	else:
		for type in items:
			selection_set += selection_set_modif(__SELECTION_SET__,cat,type)
	#else:
		#for type in items:
			#selection_set += __SELECTION_SET__.replace("__CATEGORY__",cat).replace("__SELECTIONSET_NAME__",type).replace("__SELECTIONSET_GUID__",Guid.NewGuid().ToString()).replace("__CONDITIONS__",next(cond for cond in conditions if "__TYPE_NAME__" in cond)).replace("__TYPE_NAME__",type)
	__FOLDER_2_SET__ += (xml_part_TWO_folder2.replace("__FOLDER_2__",cat).replace("__FOLDER_2_GUID__",Guid.NewGuid().ToString()) + "\r\n").replace("__SELECTION_SET__",selection_set)
#[test_string + xml_part_TWO_folder2.replace("__FOLDER_2__",f) for f in __FOLDERs_2__]
"""
for items in elements_by_cat.items():
	if items[0] == "Части":
		for type in items[1]:
			selection_set += __SELECTION_SET__.replace("__CATEGORY__","Стены").replace("__SELECTIONSET_NAME__",type).replace("__SELECTIONSET_GUID__",Guid.NewGuid().ToString()).replace("__CONDITIONS__",next(cond for cond in conditions if "__TYPE_NAME__" in cond)).replace("__TYPE_NAME__",type)
	else:
		for type in items[1]:
			selection_set += __SELECTION_SET__.replace("__CATEGORY__",items[0]).replace("__CONDITIONS__",next(cond for cond in conditions if "__TYPE_NAME__" in cond)).replace("__TYPE_NAME__",type)
"""		
xml_full = xml_full.replace("__FOLDER_2_SET__",__FOLDER_2_SET__)
	
OUT = xml_full