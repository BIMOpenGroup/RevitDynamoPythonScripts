# -*- coding: utf-8 -*-

#-----------------------Импоорт библиотек----------------------
import clr
from System import Guid
clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager

#-----------------------Функции----------------------		


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
elements_by_cat = {cat: elements for cat,elements in zip(folders_2,IN[5])}
conditions = IN[6]

xml_full = xml_part_ONE_folder1.replace("__FOLDER_1__",__FOLDER_1__)
xml_full = xml_full.replace("__FOLDER_1_GUID__",__FOLDER_1_GUID__)

for f in folders_2:
	__FOLDER_2_SET__ += (xml_part_TWO_folder2.replace("__FOLDER_2__",f).replace("__FOLDER_2_GUID__",Guid.NewGuid().ToString()) + "\r\n") 
#[test_string + xml_part_TWO_folder2.replace("__FOLDER_2__",f) for f in __FOLDERs_2__]

for i in elements_by_cat.items():
	if i[0] == "Части":
		selection_set += __SELECTION_SET__.replace("__CATEGORY__","Стены").replace("__CONDITIONS__",next(cond for cond in conditions if "__TYPE_NAME__" in cond))
	
xml_full = xml_full.replace("__FOLDER_2_SET__",__FOLDER_2_SET__)
	
OUT = selection_set,xml_full,elements_by_cat.items()