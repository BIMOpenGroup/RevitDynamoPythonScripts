# -*- coding: utf-8 -*-

#-----------------------Импоорт библиотек----------------------
import clr, sys
sys.path.append('C:\Program Files (x86)\IronPython 2.7\Lib')
import string
from System import Guid
clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import BuiltInParameter
#-----------------------Функции----------------------		

conditions = IN[6]

def selection_set_modif(__SELECTION_SET__,cat,type):
	return __SELECTION_SET__.replace("__CATEGORY__",cat).replace("__SELECTIONSET_NAME__",type).replace("__SELECTIONSET_GUID__",Guid.NewGuid().ToString()).replace("__CONDITIONS__",next(cond for cond in conditions if "__TYPE_NAME__" in cond)).replace("__TYPE_NAME__",type)

def selection_set_modif2(__SELECTION_SET__,cat,param_value,condition_type):
	return __SELECTION_SET__.replace("__CATEGORY__",cat).replace("__SELECTIONSET_NAME__",param_value).replace("__SELECTIONSET_GUID__",Guid.NewGuid().ToString()).replace("__CONDITIONS__",next(cond for cond in conditions if condition_type in cond)).replace(condition_type,param_value)
	
	
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

test = []
#[elements_by_cat[e.get_Parameter(BuiltInParameter.DPART_ORIGINAL_CATEGORY).AsString()] = set() for e in elements if e.get_Parameter(BuiltInParameter.DPART_ORIGINAL_CATEGORY) != None]

for cat,elements in zip(folders_2,UnwrapElement(IN[5])):
	if cat == "Части":
		[elements_by_cat[cat].add(e.Name) for e in elements]
		#for e in elements:
		#	elements_by_cat[cat].add(e.Name)	
	else:
		[elements_by_cat[cat].add(e.get_Parameter(BuiltInParameter.DPART_ORIGINAL_TYPE).AsString()) if e.GetType().Name == "Part" else elements_by_cat[cat].add(e.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString()) for e in elements]
		#for e in elements:
		#	if e.GetType().Name == "Part":
		#		elements_by_cat[cat].add(e.get_Parameter(BuiltInParameter.DPART_ORIGINAL_TYPE).AsString())
		#	else:
		#		elements_by_cat[cat].add(e.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString())
			#test.append(e.get_Parameter(BuiltInParameter.DPART_ORIGINAL_TYPE).AsString())
				
xml_full = xml_part_ONE_folder1.replace("__FOLDER_1__",__FOLDER_1__)
xml_full = xml_full.replace("__FOLDER_1_GUID__",__FOLDER_1_GUID__)

folder_2_set_list = []
for cat,items in elements_by_cat.items():
	selection_set = ""
	selection_list = []
	
	if cat == "Части":
		selection_list = [selection_set_modif2(__SELECTION_SET__,cat,param_value,"__O_NAME__") for param_value in items]
		#for param_value in items:
		#	selection_set += selection_set_modif2(__SELECTION_SET__,cat,param_value,"__O_NAME__") #Части отделка из DirectShape
	else:
		selection_list = [selection_set_modif2(__SELECTION_SET__,cat,param_value,"__TYPE_NAME__") for param_value in items]
		#for param_value in items:
		#	selection_set += selection_set_modif2(__SELECTION_SET__,cat,param_value,"__TYPE_NAME__")
	selection_set = string.join(selection_list,"")
	folder_2_set_list.append((xml_part_TWO_folder2.replace("__FOLDER_2__",cat).replace("__FOLDER_2_GUID__",Guid.NewGuid().ToString()) + "\r\n").replace("__SELECTION_SET__",selection_set))

__FOLDER_2_SET__ = string.join(folder_2_set_list,"")
	
xml_full = xml_full.replace("__FOLDER_2_SET__",__FOLDER_2_SET__)
	
OUT = xml_full