import clr
import math
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.GeometryConversion)


clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
# Import Revit elements
from Revit.Elements import *

instances_by_room = IN[0]
instances_angles_by_room = IN[1]
xz = Vector.ZAxis()


for i_br, a_br in zip(instances_by_room, instances_angles_by_room):
	for i_bw, a_bw in zip(i_br,a_br):
		if len(i_bw) == 0:
				pass
		else:
			for i, a in zip(i_bw,a_bw):
				i_geom = Element.Geometry(i)
				i_geom_solid = []
				for i in i_geom:
					if str(i) == "Solid":
						i_geom_solid.append(i)
					else:
						pass
				u_solid = Solid.ByUnion(i_geom_solid)
				cent_solid = Solid.Centroid(u_solid)
				r_solid = Geometry.Rotate(u_solid,cent_solid, xz, (a*-1))
				bb_solid = BoundingBox.ToCuboid(BoundingBox.ByGeometry(r_solid))
				cent_bb_solid = Solid.Centroid(bb_solid)
				bb_solid_grow = Geometry.Scale(bb_solid, Plane.ByOriginNormal(cent_bb_solid,xz) ,1 ,5, 1)
				bb_solid_rotated = Geometry.Rotate(bb_solid_grow, Solid.Centroid(bb_solid_grow), xz, a)
				
				
"""
for room in list_of_elements_by_room:
	if len(room) == 0:
		curves_by_wall, angles_by_wall =  [[]], [[]]
	else:
		curves_by_wall, angles_by_wall =  [], []
		wall_elements_by_wall, instance_elements_by_wall = [], []
		e_not_for_by_wall = []		
		for wall_by_room in room:
			curves, angles = [], []
			wall, instance = [], []
			e_not_for = []
			for item in wall_by_room:
				loc = item.Location
				if loc.ToString() == 'Autodesk.Revit.DB.LocationCurve':
					crv = loc.Curve.ToProtoType()
					p1 = crv.StartPoint
					p2 = crv.EndPoint
					vec = Vector.ByTwoPoints(p1, p2)
					xa = Vector.XAxis()
					xz = Vector.ZAxis()
					lineangle = Vector.AngleAboutAxis(xa,vec,xz)
					if round(lineangle) == 90:
						e_not_for.append(item)
					elif round(lineangle) == 270:
						e_not_for.append(item)
					elif round(lineangle) == 0:
						e_not_for.append(item)
					else:	
						#curves.append(lineangle)
						curves.append(loc.Curve.ToProtoType())
						wall.append(item)
				elif loc.ToString() == 'Autodesk.Revit.DB.LocationPoint':
					deg = math.degrees(loc.Rotation)
					if round(deg) == 180:
						e_not_for.append(item)
					elif round(deg) == 270:
						e_not_for.append(item)
					else:
						angles.append(deg)
						instance.append(item)
				else:
					test.append(item)
					
			curves_by_wall.append(curves)
			angles_by_wall.append(angles)
			
			wall_elements_by_wall.append(wall)
			instance_elements_by_wall.append(instance)	
			
			e_not_for_by_wall.append(e_not_for)
			
	curves_by_room.append(curves_by_wall)
	angles_by_room.append(angles_by_wall)
	
	wall_elements_by_room.append(wall_elements_by_wall)
	instance_elements_by_room.append(instance_elements_by_wall)
	
	elements_not_for_turning_by_room.append(e_not_for_by_wall)
"""
OUT = bb_solid_rotated