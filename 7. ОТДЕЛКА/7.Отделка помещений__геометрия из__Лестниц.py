# -*- coding: utf-8 -*-

#-----------------------Импоорт библиотек----------------------
import clr
from clr import StrongBox

import sys 
sys.path.append("C:\Program Files (x86)\IronPython 2.7\Lib")
import random
from random import randint

import System
from System import Type, Byte
clr.AddReference('System')
from System.Collections.Generic import List

clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *
clr.AddReference('RevitAPIIFC')
from Autodesk.Revit.DB.IFC import ExporterIFCUtils

clr.AddReference("RevitNodes") 
import Revit
clr.ImportExtensions(Revit.Elements) #ToDSType не работает без
clr.ImportExtensions(Revit.GeometryConversion)
#from Revit.Elements import Element


clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

#clr.AddReference('ProtoGeometry')
#from Autodesk.DesignScript.Geometry import *

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import Surface,BoundingBox
from Autodesk.DesignScript.Geometry import Curve as DSCurve

#-----------------------Импоорт библиотек----------------------

#-----------------------Функции----------------------		

def flatten(container):
    for i in container:
        if isinstance(i, (list,tuple)):
            for j in flatten(i):
                yield j
        else:
            yield i
			
def flatten2(list,container):
    for i in container:
        if type(i) == list:
            for j in flatten2(list,i):
                list.append(j)
        else:
            list.append(i)
	return list
	
output = [] 
	
def reemovNestings(l): 
    for i in l: 
        if type(i) == list: 
            reemovNestings(i) 
        else: 
            output.append(i) 

def GetWallCut(fi,wall,_face):
	doc = fi.Document
	cutDir = StrongBox[XYZ](wall.Orientation)
	try:
		curveLoop1 = ExporterIFCUtils.GetInstanceCutoutFromWall(doc, wall, fi, cutDir)
		multpl = wall.Width
		w_vector = wall.Orientation
		f_vector = fi.FacingOrientation
		for c in curveLoop1:
			test_curv = c
		if _face.Intersect(test_curv) == SetComparisonResult.Subset:
			move = Transform.CreateTranslation(w_vector.Multiply(multpl))
			extr_vector = -w_vector
		else:
			if w_vector.IsAlmostEqualTo(f_vector):
				move = Transform.CreateTranslation(XYZ(0,0,0))
				extr_vector = w_vector
			else:
				move = Transform.CreateTranslation(XYZ(0,0,0))
				extr_vector = f_vector
		curv_move = [cl.CreateTransformed(move) for cl in curveLoop1]
		curveLoop2 = CurveLoop()
		for cm in curv_move:
			curveLoop2.Append(cm)
		icurveLoop = List[CurveLoop]([curveLoop2])
		geom = GeometryCreationUtilities.CreateExtrusionGeometry(icurveLoop,extr_vector,wall.Width*2).ToProtoType()
		#loops = [i.ToProtoType() for i in curveLoop1] # - профиль сгенерированый Експортером
		return geom#[loops,geom]
	except:
		geom = BoundingBox.ToCuboid(fi.get_BoundingBox(doc.ActiveView).ToProtoType())
		return geom

def GetWallProfil(insert_wall,host_wall,_face):	
	#uw_geom = Element.Geometry(u_wall.ToDSType(True)) #ToDSType не работает без clr.ImportExtensions(Revit.Elements)
	g_curve_list = GetW_P_curve(insert_wall)
	if g_curve_list != None:
		icurve = List[Autodesk.Revit.DB.Curve](g_curve_list)
		#--- Расположение точек в линиях должно быть последовательным для курвелооп
		i_crv_loop = CurveLoop.Create(icurve)
		i_list_crv_loop = List[CurveLoop]([i_crv_loop])
		wh_vector = host_wall.Orientation
		iw_vector = insert_wall.Orientation
		f_vector = face.FaceNormal 
		if wh_vector.IsAlmostEqualTo(f_vector):
			extr_vector = insert_wall.Orientation
		else:
			extr_vector = host_wall.Orientation
		geom = GeometryCreationUtilities.CreateExtrusionGeometry(i_list_crv_loop,extr_vector,host_wall.Width).ToProtoType()
		#loops = [i.ToProtoType() for i in g_id_list]
		#p_crv = PolyCurve.ByJoinedCurves([crv1,crv2,crv3,crv4])		
		return geom#[loops,geom]#[i.ToPoint() for i in test]
	
def GetW_P_curve(u_wall):
	if u_wall.GetType().Name == "Wall":
		loc = u_wall.Location
		crv = loc.Curve
		bo = u_wall.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET).AsDouble()#/0.3048#*size_param
		wh = u_wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble()#/0.3048#*size_param
		move_bo = Transform.CreateTranslation(XYZ(0,0,bo))
		move_wh = Transform.CreateTranslation(XYZ(0,0,wh))
		crv1 = crv.CreateTransformed(move_bo)
		crv2 = crv1.CreateTransformed(move_wh)

		crv11 = Autodesk.Revit.DB.Line.CreateBound(crv1.GetEndPoint(0),crv2.GetEndPoint(0))
		crv22 = Autodesk.Revit.DB.Line.CreateBound(crv2.GetEndPoint(0),crv2.GetEndPoint(1))
		crv33 = Autodesk.Revit.DB.Line.CreateBound(crv2.GetEndPoint(1),crv1.GetEndPoint(1))
		crv44 = Autodesk.Revit.DB.Line.CreateBound(crv1.GetEndPoint(1),crv1.GetEndPoint(0))
		"""
		crv11 = CreateBound(crv1.GetEndPoint(0),crv2.GetEndPoint(0))
		crv22 = CreateBound(crv2.GetEndPoint(0),crv2.GetEndPoint(1))
		crv33 = CreateBound(crv2.GetEndPoint(1),crv1.GetEndPoint(1))
		crv44 = CreateBound(crv1.GetEndPoint(1),crv1.GetEndPoint(0))
		"""
		g_crv_list = [crv11,crv22,crv33,crv44]
		return g_crv_list
	else:
		return None
				
def ElementGeomFaces2(element):
	geom_elem = element.get_Geometry(Options())
	geom_solid_list = []
	geom_faces = []
	for g in geom_elem:
		if g.GetType() == Autodesk.Revit.DB.Solid:
			geom_solid_list.append(g)
		elif g.GetType() == Autodesk.Revit.DB.GeometryInstance:
			geom_elem2 = g.GetInstanceGeometry()
			for g2 in geom_elem2:
				if g2.GetType() == Autodesk.Revit.DB.Solid:
					geom_solid_list.append(g2)
	for i,geomSolid in enumerate(geom_solid_list):
		try:
			if i == 0:
				geom_faces_array = geomSolid.Faces
				geom_faces = [gf for gf in geom_faces_array]
			else:
				for fc in geomSolid.Faces:
					geom_faces.append(fc)
		except:
			pass
	return geom_faces	
		
def PaintFace(surf, mat):
    elemRef = surf.Tags.LookupTag("RevitFaceReference")
    #elemRef = surf.Reference
    elem = doc.GetElement(elemRef)
    face = elem.GetGeometryObjectFromReference(elemRef)
    if not (doc.IsPainted(elem.Id, face)):
		try:
			return doc.Paint(elem.Id, face, mat.Id)
		except:
			pass	
		
def PaintFace2(surf, mat, elem):
    if not (doc.IsPainted(elem.Id, surf)):
		try:
			return doc.Paint(elem.Id, surf, mat.Id)	
		except:
			pass
	
		
#-----------------------АПИ параметры----------------------
doc = DocumentManager.Instance.CurrentDBDocument
elements = UnwrapElement(IN[0])
rooms = UnwrapElement(IN[1])
mat = UnwrapElement(IN[3])
r_faces = UnwrapElement(IN[4])

test = []
all_room_surface = []
options = SpatialElementBoundaryOptions()
options.StoreFreeBoundaryFaces = True 
options.SpatialElementBoundaryLocation = SpatialElementBoundaryLocation.Finish
calculator = SpatialElementGeometryCalculator(doc,options)
trnsf = Transform.CreateTranslation(XYZ(0,0,100))
#trnsf.CreateTranslation(XYZ.BasisZ)
s_options = SolidOptions(ElementId(-1), ElementId(-1))
test2 = []	
newlist= []

#if (isinstance(surfaces, list)):
#    [PaintFace(j, material) for i in surfaces for j in i]
#else:
#    PaintFace(surfaces, material) 

for e in elements:
	hight = e.Height
	move_z = -hight*3.2808#e.get_BoundingBox(doc.ActiveView).Min.Z#.ToProtoType()
	test.append(ElementGeomFaces2(e))
	#test.append(e.get_BoundingBox(doc.ActiveView).ToProtoType())
	#test.append(e.BoundingBox)
	
TransactionManager.Instance.EnsureInTransaction(doc)
#newlist=[PaintFace2(item,mat,elements[0]) for items in test for item in items]
new = [PaintFace(item,mat) for item in r_faces if item != None]
TransactionManager.Instance.TransactionTaskDone()	

#newlist = [item for items in test for itemss in items for item in itemss]
transform_Z = Transform.CreateTranslation(XYZ(0,0,move_z))	

"""
for room in rooms:
	room_area = room.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble()
	room_volume = room.get_Parameter(BuiltInParameter.ROOM_VOLUME).AsDouble()
	room_height = room_volume/room_area*304.8
	if room_height == 0:
		OUT = "Необходимо включить расчёт объёма для помещений"
		break
	room_level = doc.GetElement(room.get_Parameter(BuiltInParameter.ROOM_LEVEL_ID).AsElementId())
	crv_lp = CurveLoop()
	separator_list = []
	by_face_list = []
	inserts = []
	curve_from_boundary_list = []
	elem_list = []
	results = calculator.CalculateSpatialElementGeometry(room)
	roomSolid = results.GetGeometry()
	inserts_by_wall = []
	boundary_surf = []
	boundary_curvs = []
	boundary_type = []
	boundary_level = []
	crv_list = []
	#wall_hight = None
#@@@-----------------------Боундари Элементс----------------------
	for boundarylist in room.GetBoundarySegments(options):
		b_s = []
		#boundary_curvs = [boundary.GetCurve().ToProtoType() for boundary in boundarylist]
		#boundary_surf = [Curve.Extrude(crv,XYZ(0,0,1).ToVector(),room_height) for crv in boundary_curvs]
		#surf_from_bound_curvs.append(boundary_surf)
		b_element1 = None
		b_element2 = None
		for i,boundary in enumerate(boundarylist):
			crv = None
			wall_hight = room_height
			if str(boundary.ElementId) == "-1" and str(boundary.LinkElementId) == "-1":
				#boundary_curvs.append(boundary.GetCurve().ToProtoType())
				crv = boundary.GetCurve()#.ToProtoType()
				#boundary_type.append(type)
			elif str(boundary.ElementId) != "-1":
				b_element1 = doc.GetElement(boundary.ElementId)
				if b_element1.GetType().Name == "ModelLine":
					separator_list.append(boundary.GetCurve())#!!!!!!!!!!!!!!!!boundary.GetCurve() вместо поиска геометрии у элементов!!!!!!!!!!
				elif b_element1.GetType().Name == "Wall" and b_element1.WallType.Kind == WallKind.Curtain:
					separator_list.append(boundary.GetCurve())
#---------------Убираем тип стены из расчёта -----------------------------------------------------------------------------------					
				elif b_element1.GetType().Name == "Wall" and doc.GetElement(b_element1.GetTypeId()).get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString() == "Ограждение МХМТС":
					pass
#-------------------------------------------------------------------------------------------------------------------------------------------
				elif b_element1.GetType().Name == "Wall":
					#wall_volum = b_element1.get_Parameter(BuiltInParameter.HOST_VOLUME_COMPUTED).AsDouble()
					#wall_area = b_element1.get_Parameter(BuiltInParameter.HOST_AREA_COMPUTED).AsDouble()
					#wall_hight = wall_volum/wall_area*3048#b_element1.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble()*304.8
					wall_box = b_element1.get_BoundingBox(doc.ActiveView)
					wall_hight = (wall_box.Max.Z - wall_box.Min.Z)*304.8
					#boundary_type.append(Get_walltype_ctruct_mat_name(doc,b_element1,room))
					#boundary_curvs.append(boundary.GetCurve().ToProtoType())
					crv = boundary.GetCurve()#.ToProtoType()
				else:
					#boundary_type.append(Get_walltype_ctruct_mat_name(doc,b_element1,room))
					#boundary_curvs.append(boundary.GetCurve().ToProtoType())
					crv = boundary.GetCurve()#.ToProtoType()
			elif str(boundary.LinkElementId) != "-1":
				b_element2 = link_doc.GetElement(boundary.LinkElementId)
				if b_element2.GetType().Name == "ModelLine":
					separator_list.append(boundary.GetCurve())
				elif b_element2.GetType().Name == "Wall" and b_element2.WallType.Kind == WallKind.Curtain:
					separator_list.append(boundary.GetCurve())
				#else:
					#boundary_type.append(Get_walltype_ctruct_mat_name(link_doc,b_element2,room))
					#boundary_curvs.append(boundary.GetCurve().ToProtoType())
			boundary_level.append(room_level)
			#boundary_level.append([room_height,wall_hight])
			#boundary_type.append([boundary.IsValidObject,b_element1.GetType().Name,boundary.ElementId])
#------------------------------------------------------Включаем расчет по высоте стен--------------------------------------------------
			if crv != None and IN[2]:
				crv = crv.CreateTransformed(transform_Z)#.ToProtoType()
			elif crv != None:
				crv = crv#.ToProtoType()
			
			if crv != None:
				crv_list.append(crv)
				crv_lp.Append(crv)
				#boundary_surf.append(crv)
				#test = Flatten(test)
				#boundary_surf.append(DSCurve.Extrude(crv,Autodesk.Revit.DB.XYZ(0,0,1).ToVector(),hight*328*5))	
	crv_i_list = List[Curve](crv_list)
	loop = CurveLoop.Create(crv_i_list)
	ilist_crv_loop = List[CurveLoop]()
	ilist_crv_loop.Add(CurveLoop.Create(crv_i_list))
	solid = GeometryCreationUtilities.CreateExtrusionGeometry(ilist_crv_loop,XYZ(0,0,1),hight*5)
	all_room_surface.append(boundary_surf)
	dy_faces = solid.Faces
	#dy_faces = [gf.ToProtoType() for gf in faces]
	for gf in dy_faces:
		for t in newlist:
			if gf.Intersect(t) == FaceIntersectionFaceResult.Intersecting:
				try:
					test2.append(t.ToProtoType())
				except:
					pass
"""				
#test = reemovNestings(test)


OUT = r_faces,newlist,all_room_surface,hight