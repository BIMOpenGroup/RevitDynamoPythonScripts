import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

import System
clr.AddReference('System')
from System.Collections.Generic import List

clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

test = []
test2 = []
test3 = []

def ElGet(id): 
	if id.GetType() == Autodesk.Revit.DB.ElementId:
		return doc.GetElement(id)
	elif id.GetType() == System.Int32:
		return doc.GetElement(ElementId(id))

def ElementGeomFaces2(geomSolid):
	geom_faces_array = geomSolid.Faces
	geom_faces = [gf.ToRevitType() for gf in geom_faces_array]
	return geom_faces
	
	
def ElementGeomFaces1(element):
	geom_elem = element.get_Geometry(Options())
	geom_solid_list = []
	geom_faces = []
	
	for g in geom_elem:
		if g.GetType() == Autodesk.Revit.DB.Solid:
			geom_solid_list.append(g)
			#test.append(g.GraphicsStyleId)
		elif g.GetType() == Autodesk.Revit.DB.GeometryInstance:
			geom_elem2 = g.GetInstanceGeometry()
			for g2 in geom_elem2:
				if g2.GetType() == Autodesk.Revit.DB.Solid:
					geom_solid_list.append(g2)
					#test.append(g.GraphicsStyleId)
	for i,geomSolid in enumerate(geom_solid_list):
		try:
			if i == 0:
				geom_faces_array = geomSolid.Faces
				geom_faces = [gf for gf in geom_faces_array]
				#t = geom_faces[0]
				#[test.append(doc.GetElement(t.GraphicsStyleId).GraphicsStyleCategory.Name) for t in geom_faces]
			else:
				for fc in geomSolid.Faces:
					geom_faces.append(fc)
					#test.append(doc.GetElement(t.GraphicsStyleId).GraphicsStyleCategory.Name)
				#t = geom_faces[0]
			#test.append(doc.GetElement(t.GraphicsStyleId).GraphicsStyleCategory.Name)				
		except:
			pass
	return geom_faces


def ElementGeomFaces3(element):
	opt = Options()
	opt.ComputeReferences = True
	opt.DetailLevel = ViewDetailLevel.Fine
	opt.IncludeNonVisibleObjects = True
	geom_elem = element.get_Geometry(opt)
	geom_solid_list = []
	geom_faces = []
	
	for g in geom_elem:
		if g.GetType() == Autodesk.Revit.DB.Solid:
			geom_solid_list.append(g)
			#test.append(g.GraphicsStyleId)
		elif g.GetType() == Autodesk.Revit.DB.GeometryInstance:
			geom_elem2 = g.GetInstanceGeometry()
			for g2 in geom_elem2:
				if g2.GetType() == Autodesk.Revit.DB.Solid:
					geom_solid_list.append(g2)
					#test.append(g.GraphicsStyleId)
	for i,geomSolid in enumerate(geom_solid_list):
		#test.append(geomSolid.ToProtoType())
		try:
			#test.append(geomSolid.Volume)
			geom_faces_array = geomSolid.Faces
			geom_faces = [gf for gf in geom_faces_array]
			geom_mats = {ElGet(d.MaterialElementId).Name:[] for d in geom_faces}
			test.append(geom_mats.keys())
			if any("_Отделка" in m for m in geom_mats.keys()):
				test.append("_Отделка")
				test.append(geomSolid.ToProtoType())
				test.append(geomSolid.Volume*0.028316846592)
				#test.append(geomSolid.Volume)
				#test.append(geomSolid.SurfaceArea)
				test2.append(geomSolid.ToProtoType())
		except:
			pass
	return geom_faces

def ElementGeomFaces4(element,params):
	opt = Options()
	opt.ComputeReferences = True
	opt.DetailLevel = ViewDetailLevel.Fine
	opt.IncludeNonVisibleObjects = True
	
	geom_elem = element.get_Geometry(opt)
	geom_solid_list = []
	geom_faces = []
	
	if element.GetType() == Autodesk.Revit.DB.Architecture.Stairs:
		run_type = ElGet(ElGet(s.GetTypeId()).RunType)
		landing_type = ElGet(ElGet(s.GetTypeId()).LandingType)
		stup_mat = ElGet(run_type.get_Parameter(BuiltInParameter.STAIRS_TRISERTYPE_TREAD_MATERIAL).AsElementId())
		if stup_mat == None: stup_mat = "___Лестницы_без отделки" 
		else: stup_mat = stup_mat.Name
		stup_mat_hight = run_type.get_Parameter(BuiltInParameter.STAIRS_TRISERTYPE_TREAD_THICKNESS).AsDouble()
		plosh_mat = ElGet(landing_type.get_Parameter(BuiltInParameter.STAIRS_TRISERTYPE_TREAD_MATERIAL).AsElementId())
		if plosh_mat == None: plosh_mat = "___Лестницы_без отделки" 
		else: plosh_mat = plosh_mat.Name
		plosh_mat_hight = landing_type.get_Parameter(BuiltInParameter.STAIRS_TRISERTYPE_TREAD_THICKNESS).AsDouble()
		test3.append([stup_mat,stup_mat_hight,plosh_mat,plosh_mat_hight])
	else:
		stup_mat_hight = 1
		plosh_mat_hight = 1
	mat_dict = {}
	
	for p in params:
		mat_dict[p] = [0]
	
	for g in geom_elem:
		if g.GetType() == Autodesk.Revit.DB.Solid:
			geom_solid_list.append(g)
			#test.append(g.GraphicsStyleId)
		elif g.GetType() == Autodesk.Revit.DB.GeometryInstance:
			geom_elem2 = g.GetInstanceGeometry()
			for g2 in geom_elem2:
				if g2.GetType() == Autodesk.Revit.DB.Solid:
					geom_solid_list.append(g2)
					#test.append(g.GraphicsStyleId)
					
	for geomSolid in geom_solid_list:
		geom_faces = list(geomSolid.Faces)
		solid_mats_dict = {}
		for face in geom_faces:
			face_mat = ElGet(face.MaterialElementId)
			if face_mat != None:
				if "___Лестницы" in face_mat.Name:
					if face_mat.Name == "___Лестницы_Отделка ступенек":
						mat_dict["___Лестницы_Отделка ступенек"] = set()
					elif face_mat.Name == "___Лестницы_Отделка площадок":
						mat_dict["___Лестницы_Отделка площадок"] = set()	
					else:	
						mat_dict[face_mat.Name] = []
				else:
					mat_dict["___Лестницы_без отделки"] = []
			else:
				mat_dict["___Лестницы_без отделки"] = []
	for geomSolid in geom_solid_list:
		#test.append(geomSolid.ToProtoType())
		geom_faces = list(geomSolid.Faces)
		for face in geom_faces:
			face_mat = ElGet(face.MaterialElementId)
			if face_mat != None:
				if "___Лестницы" in face_mat.Name:
					if face_mat.Name == "___Лестницы_Торец лестницы  на стене":
						mat_dict["___Лестницы_Торец лестницы  на стене"].append(face.Area)
					elif face_mat.Name == "___Лестницы_Отделка ступенек":
						mat_dict["___Лестницы_Отделка ступенек"].add(geomSolid.Volume/stup_mat_hight)
					elif face_mat.Name == "___Лестницы_Отделка площадок":
						mat_dict["___Лестницы_Отделка площадок"].add(geomSolid.Volume/plosh_mat_hight)	
					else:
						mat_dict[face_mat.Name].append(face.Area)
				else:
					mat_dict["___Лестницы_без отделки"].append(face.Area)
			else:
				mat_dict["___Лестницы_без отделки"].append(face.Area)		
		"""
		geom_mats = {ElGet(d.MaterialElementId).Name:[] for d in geom_faces}
		test.append(geom_mats.keys())
		if any("_Отделка" in m for m in geom_mats.keys()):
			test.append("_Отделка")
			test.append(geomSolid.ToProtoType())
			test.append(geomSolid.Volume*0.028316846592)
			test2.append(geomSolid.ToProtoType())
		"""
	if sum(mat_dict["___Лестницы_Покраска маршей и площадок"]) > 0:
		mat_dict["___Лестницы_Покраска маршей и площадок"] = sum(mat_dict["___Лестницы_Покраска маршей и площадок"])-sum(mat_dict["___Лестницы_Отделка ступенек"])-sum(mat_dict["___Лестницы_Отделка площадок"])	
	if mat_dict["___Лестницы_Покраска маршей и площадок"] < 0:
		mat_dict["___Лестницы_Покраска маршей и площадок"] = 0
	
	return mat_dict	
	
def SortFacesByMat(geom_faces):
	face_dict = {}
	for face in geom_faces:
		face_dict[face.MaterialElementId] = []
	for face in geom_faces:
		face_dict[face.MaterialElementId].append(face.Area)
	return face_dict

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
stairs_elems = []
"""
doc.GetElement(item)
for geom_solids in geom_solid_list:
	for solid in geom_solids:
		test.append(ElementGeomFaces2(solid))
"""
for s in stairs:
	RemParamValList(s,param_list)
	elems = []
	mats.append(ElementGeomFaces4(s,param_list).keys())
	areas.append(ElementGeomFaces4(s,param_list).values())
	#test.append(s.GetType())
	#mats.append(ElementGeomFaces4(s).keys())
	#areas.append(ElementGeomFaces4(s).values())
	#areas.append(SortFacesByMat(ElementGeomFaces3(s)).values())
	#mats.append([doc.GetElement(key).Name if doc.GetElement(key) != None and "___Лестницы" in doc.GetElement(key).Name else "___Лестницы_без отделки" for key in SortFacesByMat(ElementGeomFaces1(s)).keys() ])
	#geom_faces = ElementGeomFaces1(s)
	#test.append(ElementGeomFaces1(s))
	stairs_elems.append(elems)


OUT = mats,areas,test3#,test,test2,test3