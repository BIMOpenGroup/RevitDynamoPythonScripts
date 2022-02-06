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
from Autodesk.Revit.DB import SpatialElement, SpatialElementBoundaryOptions, SpatialElementBoundaryLocation, SpatialElementGeometryCalculator, SpatialElementBoundarySubface, SolidOptions
from Autodesk.Revit.DB import Transform, XYZ, SubfaceType, WallKind, SetComparisonResult, CurveLoop, GeometryCreationUtilities, BuiltInParameter, Line, Curve, ElementId, Material, Color
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

clr.AddReference('System')
from System import Type

#-----------------------Параметры над функциями----------------------

doc = DocumentManager.Instance.CurrentDBDocument
test = []

#-----------------------Функции----------------------		
def __wall_by_id_work__ (_id,_doc,_face):
	full_id_list.append(_id)
	b_element = _doc.GetElement(_id)
	#test3.append([b_element,b_element.GetType().Name])
	if b_element.GetType().Name == "Wall":	
		wallType = _doc.GetElement(b_element.GetTypeId())
		type_name = wallType.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
		if type_name == "Ограждение МХМТС": 
			pass
		elif "(автомойка)" in type_name:
			pass
		elif wallType.Kind == WallKind.Curtain:
			curtain_list.append(b_element)
		else:
			#blist.append(b_element)
			inserts_list = b_element.FindInserts(incopenings,incshadows,incwalls,incshared)
			if not inserts_list:
				pass
			else:
				for insert in inserts_list:
					if _doc.GetElement(insert).GetType().Name == "Opening":
						pass
					else:
						item = _doc.GetElement(insert)
						x = None
						#x = item.GetType().Name
						if item.GetType().Name == "FamilyInstance":
							x = GetWallCut(item,b_element,_face)
						elif item.GetType().Name == "Wall":
							x = GetWallProfil(item,b_element,_face)
						else:
							x = BoundingBox.ToCuboid(item.get_BoundingBox(doc.ActiveView).ToProtoType())
						inserts_by_wall.append(x)
	else:
		pass
	
def is_not_curtain(_id,_doc):
	wall = _doc.GetElement(_id)
	#wallType = wall.WallType#doc.GetElement(wall.GetTypeId())
	if wall.GetType().Name == "Wall": 
		if wall.WallType.Kind == WallKind.Curtain:	
			return False
		else:
			return True
	else:
		return True
	
def GetWallCut(fi,wall,_face):
	doc = fi.Document
	cutDir = StrongBox[XYZ](wall.Orientation)
	try:
		curveLoop1 = ExporterIFCUtils.GetInstanceCutoutFromWall(doc, wall, fi, cutDir)
		multpl = wall.Width
		w_vector = wall.Orientation
		f_vector = fi.FacingOrientation
		#test_curv = [c for c in curveLoop1]
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
		#[curveLoop2.Append(cm) for cm in curv_move]
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
		
def Get_walltype_ctruct_mat_name(doc,b_element,room):
	room_func = room.LookupParameter("Name").AsString() #ПЕРЕДЕЛАТЬ ЧТОБЫ НЕ БЫЛО ЗАВИСИМОСТИ ОТ ЯЗЫКА REVIT
	if room_func == "Мойка автомобилей":
		room_func = "Автостоянка"
	if b_element.GetType().Name != "RevitLinkInstance":
		mat_name = doc.GetElement(b_element.GetTypeId()).get_Parameter(BuiltInParameter.STRUCTURAL_MATERIAL_PARAM).AsValueString()#b_element.WallType.get_Parameter(BuiltInParameter.STRUCTURAL_MATERIAL_PARAM).AsValueString()
		if "елезобетон" in mat_name:
			out = "АБН_Отделка стен железобетон"+"("+room_func+")"
			Create_Material(out)
		else:
			out = "АБН_Отделка стен кладка"+"("+room_func+")"
			Create_Material(out)
	else:
		out = "АБН_Отделка стен кладка"+"("+room_func+")"
		Create_Material(out)
	return out
	
def Create_Material(mat_name):
	if Material.IsNameUnique(doc,mat_name):
		TransactionManager.Instance.EnsureInTransaction(doc)
		mat = Material.Create(doc,mat_name)
		doc.GetElement(mat).Color = Autodesk.Revit.DB.Color(Byte.Parse(str(randint(0, 255))), Byte.Parse(str(randint(0, 255))), Byte.Parse(str(randint(0, 255))))
		TransactionManager.Instance.TransactionTaskDone()
#-----------------------АПИ параметры----------------------
doc = DocumentManager.Instance.CurrentDBDocument
link_doc = UnwrapElement(IN[1])
custom_hight = IN[3]
#uiapp = DocumentManager.Instance.CurrentUIApplication
#app = uiapp.Application
#version = app.VersionNumber
options = SpatialElementBoundaryOptions()
options.StoreFreeBoundaryFaces = True 
options.SpatialElementBoundaryLocation = SpatialElementBoundaryLocation.Finish
calculator = SpatialElementGeometryCalculator(doc,options)
trnsf = Transform.CreateTranslation(XYZ(0,0,100))
#trnsf.CreateTranslation(XYZ.BasisZ)
s_options = SolidOptions(ElementId(-1), ElementId(-1))

#-----------------------Рабочие параметры----------------------	
#xz = Vector.ZAxis()
size_param = 1000
incopenings,incshadows,incwalls,incshared = True,False,True,True
rooms = UnwrapElement(IN[0])
custom_hight = IN[3]
surf_by_room = []
element_by_room = []
full_id_list = []
curtain_list=[]
insertslist = []
surface_in_room = []
surface_list_all = []
surf_from_bound_curvs = []
boundarylist = []
blist = []
x=0
test3 = []
boundary_type_by_room = []
boundary_by_room_level = []
separator_list = []
move_z = IN[5]*0.00328084
transform_Z = Transform.CreateTranslation(XYZ(0,0,move_z))

#@@@-----------------------Начало Скрипта----------------------
for room in rooms:
	room_area = room.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble()
	room_volume = room.get_Parameter(BuiltInParameter.ROOM_VOLUME).AsDouble()
	room_height = room_volume/room_area*304.8
	room_level = doc.GetElement(room.get_Parameter(BuiltInParameter.ROOM_LEVEL_ID).AsElementId())

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
				if i+1 < len(boundarylist):
					try:
						type = Get_walltype_ctruct_mat_name(doc,doc.GetElement(boundarylist[i+1].ElementId),room)
					except:
						type = "АБН_Отделка стен"
						"""
						try:
							type = Get_walltype_ctruct_mat_name(doc,doc.GetElement(boundarylist[i-1].ElementId),room)
						except:
							type = "АБН_Отделка стен"
						"""
				elif i-1 >= 0:
					try:
						type = Get_walltype_ctruct_mat_name(doc,doc.GetElement(boundarylist[i-1].ElementId),room)
					except:
						type = "АБН_Отделка стен"
						"""try:
							type = Get_walltype_ctruct_mat_name(doc,doc.GetElement(boundarylist[i+1].ElementId),room)
						except:
						type = "where is my type dude2"""
				else:
					type = "where is my type dude3"
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
					type = Get_walltype_ctruct_mat_name(doc,b_element1,room)
					#boundary_type.append(Get_walltype_ctruct_mat_name(doc,b_element1,room))
					#boundary_curvs.append(boundary.GetCurve().ToProtoType())
					crv = boundary.GetCurve()#.ToProtoType()
				else:
					try:
						type = Get_walltype_ctruct_mat_name(doc,b_element1,room)
					except:
						type = "АБН_Отделка стен"
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
			#test.append(crv.Length*0.3048)
			if crv.Length*0.3048 > 0.01:
				test.append(crv.Length*0.3048)
				if crv != None and IN[4]:
					crv = crv.CreateTransformed(transform_Z).ToProtoType()

				elif crv != None:
					crv = crv.ToProtoType()
					if IN[2]:	
						if crv != None:
							boundary_surf.append(DSCurve.Extrude(crv,Autodesk.Revit.DB.XYZ(0,0,1).ToVector(),room_height))
							boundary_type.append(type)
					else:
						if crv != None:
							boundary_surf.append(DSCurve.Extrude(crv,Autodesk.Revit.DB.XYZ(0,0,1).ToVector(),custom_hight))
							boundary_type.append(type)
		#boundary_surf = b_s

#@@@-----------------------Боундари Фэйс----------------------			
	for face in results.GetGeometry().Faces:
		inserts_by_wall = []
		for bface in results.GetBoundaryFaceInfo(face):
			inserts_by_wall = []
			test_list = []
			test_list2 = []
			link_id = 0
			by_face_h = False
			by_face_l = False
			if bface.SubfaceType != SubfaceType.Side:
				pass
			else:
				host_id = bface.SpatialBoundaryElement.HostElementId
				if str(host_id) != "-1" and is_not_curtain(host_id,doc):
					by_face_list.append(face)#-------------Cобираем плоскость
					by_face_h = face
					__wall_by_id_work__(host_id,doc,by_face_h)
					inserts.extend(inserts_by_wall)
				else:
					link_id = bface.SpatialBoundaryElement.LinkedElementId
					if str(link_id) != "-1" and is_not_curtain(link_id,link_doc):
						by_face_list.append(face)#---------Cобираем плоскость
						by_face_l = face
						#__wall_by_id_work__(link_id,link_doc,by_face_l)
						inserts.extend(inserts_by_wall)
					else:
#@@@-----------------------Тут убираем дубликаты плоскостей----------------------
						for b_f in by_face_list:
							if face.Equals(b_f):
								test_list.append(True)
							else:	
								test_list.append(False)
						#[test_list.append(True) if face.Equals(b_f) else test_list.append(False) for b_f in by_face_list]
						if any(test_list):
							pass
						else:
#@@@-----------------------Тут убираем разделители----------------------
							for s_l in separator_list:
								if str(face.Intersect(s_l)) == "Disjoint":
									test_list2.append(False)
								else:	
									test_list2.append(True)
							if any(test_list2):
								pass
							elif bface.SubfaceArisesFromElementFace: #------Убираем плоскости витражей
								pass
							else:
								by_face_list.append(face)#------Cобираем торцевые плоскости
								by_face = face
								inserts.extend(inserts_by_wall)
			
	insertslist.append(inserts)
	surface_in_room = []
	#by_face_list2 = [bs.ToProtoType() for bs in by_face_list]
	

	for bs in boundary_surf:
		new_bs = bs
		for ins in inserts:
			if ins and bs.DoesIntersect(ins):
				try:
#-------------------ВЫРЕЗАЕТ ИЗ ПЛОСКОСТИ СТЕНЫ ЕСЛИ ДВЕРЬ ПРИМЫКАЕТ К НЕЙ ТОРЦОМ, ИСПРАВИТЬ -------------------
#-------------------нужен метот для получения плоскости стены с изминёным профилем -------------------
					new_bs = new_bs.SubtractFrom(ins)[0] 
				except:
					pass
		surface_in_room.append(new_bs)
		
	surface_list_all.append(surface_in_room)		
	boundary_type_by_room.append(boundary_type)
	boundary_by_room_level.append(boundary_level)
OUT = surface_list_all,boundary_type_by_room,boundary_by_room_level,separator_list,test