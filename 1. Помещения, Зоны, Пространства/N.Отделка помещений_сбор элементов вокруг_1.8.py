# -*- coding: utf-8 -*- 

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import * 
import Autodesk

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.GeometryConversion)

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager

doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
version = app.VersionNumber
options = Autodesk.Revit.DB.SpatialElementBoundaryOptions()

incopenings,incshadows,incwalls,incshared = True,True,True,True

items = UnwrapElement(IN[0])
p_roomseparator = IN[2]
p_wall = IN[3]
elementlist = []
curvelist_wall = []
curtain_list=[]
insertslist = []
curvelist_others = []

for item in items:
	blist = []
	clist = []
	colist = []
	for boundarylist in item.GetBoundarySegments(options):
		for boundary in boundarylist:
			b_element1=doc.GetElement(boundary.ElementId)
			if b_element1 == None:
				colist.append(boundary.GetCurve().ToProtoType())
			elif b_element1.Category.Name == p_roomseparator:
				pass
			elif b_element1.Category.Name == p_wall and "Autodesk.Revit.DB.CurtainGrid" in str(b_element1.CurtainGrid):
				curtain_list.append(b_element1)
			elif b_element1.Category.Name == p_wall:
				blist.append(b_element1)
				if version > 2016:
					clist.append(boundary.GetCurve().ToProtoType())
				else:
					clist.append(boundary.Curve.ToProtoType())
			else:
				colist.append(boundary.GetCurve().ToProtoType())
	inserts2 = []
	
	for bl in blist:
		inserts1 = []
		test = bl.FindInserts(incopenings,incshadows,incwalls,incshared)
		for insert in test:
			inserts1.append(doc.GetElement(insert))
		inserts2.append(inserts1)
	insertslist.append(inserts2)
	elementlist.append(blist)
	curvelist_wall.append(clist)
	curvelist_others.append(colist)
	"""
	bounds = item.GetBoundarySegments(options)
	for bound in bounds[0]:
		line = bound.GetCurve()
		curvelist_others.append(line.ToProtoType())
	"""
OUT = elementlist,curvelist_wall,insertslist,curvelist_others,curtain_list

