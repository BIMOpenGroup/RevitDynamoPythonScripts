import clr
#clr.AddReference('ProtoGeometry')
#from Autodesk.DesignScript.Geometry import *

clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

#import System
#clr.AddReference('System')
#from System.Collections.Generic import List

clr.AddReference('RevitServices')
#import RevitServices
from RevitServices.Persistence import DocumentManager
#from RevitServices.Transactions import TransactionManager

"""
clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)
"""

def ElGet(id): 
	if id.GetType() == Autodesk.Revit.DB.ElementId:
		return doc.GetElement(id)
	elif id.GetType() == System.Int32:
		return doc.GetElement(ElementId(id))

def ElementGeomFaces4(element,params):
	opt = Options()
	opt.ComputeReferences = True
	opt.DetailLevel = ViewDetailLevel.Fine
	opt.IncludeNonVisibleObjects = True
	
	geom_elem = element.get_Geometry(opt)
	geom_solid_list = []
	geom_faces = []
	mat_dict = {}
	
	for p in params:
		mat_dict[p] = [0]
	
	for g in geom_elem:
		if g.GetType() == Autodesk.Revit.DB.Solid:
			geom_solid_list.append(g)
		elif g.GetType() == Autodesk.Revit.DB.GeometryInstance:
			geom_elem2 = g.GetInstanceGeometry()
			for g2 in geom_elem2:
				if g2.GetType() == Autodesk.Revit.DB.Solid:
					geom_solid_list.append(g2)
					
	for geomSolid in geom_solid_list:
		geom_faces = list(geomSolid.Faces)
		solid_mats_dict = {}
		for face in geom_faces:
			face_mat = ElGet(face.MaterialElementId)
			if face_mat != None:
				mat_dict[face_mat.Name] = []
				
	for geomSolid in geom_solid_list:
		geom_faces = list(geomSolid.Faces)
		for face in geom_faces:
			face_mat = ElGet(face.MaterialElementId)
			if face_mat != None:
				if "___Лестницы" in face_mat.Name:
					if face_mat.Name == "___Лестницы_Торец лестницы  на стене":
						mat_dict["___Лестницы_Торец лестницы  на стене"].append(face.Area)
					elif face_mat.Name == "___Лестницы_Отделка ступенек":
						mat_dict["___Лестницы_Отделка ступенек"].append(face.Area)
					elif face_mat.Name == "___Лестницы_Отделка площадок":
						mat_dict["___Лестницы_Отделка площадок"].append(face.Area)
					else:
						mat_dict[face_mat.Name].append(face.Area)
				else:
					mat_dict["___Лестницы_без отделки"].append(face.Area)
			else:
				mat_dict["___Лестницы_без отделки"].append(face.Area)		
	return mat_dict	
	

def RemParamValList(element,param_list):
	for p in param_list:
		try:
			element.LookupParameter(p).Set(0)
		except:
			pass

doc = DocumentManager.Instance.CurrentDBDocument	
stairs = UnwrapElement(IN[0])
param_list = UnwrapElement(IN[1])
areas = []
mats = []

for s in stairs:
	RemParamValList(s,param_list)
	elems = []
	#mats.append(ElementGeomFaces4(s,param_list).keys())
	#areas.append(ElementGeomFaces4(s,param_list).values())
	for mat, area in zip(ElementGeomFaces4(s,param_list).items()):
		s.LookupParameter(mat).Set(sum(area))

test = []

for a1 in areas:
	for a in a1:
		test.append(sum(a))


OUT = mats,areas,test