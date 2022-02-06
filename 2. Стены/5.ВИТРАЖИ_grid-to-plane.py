import clr

clr.AddReference('RevitAPIUI')
from  Autodesk.Revit.UI import *

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.Creation import ItemFactoryBase
from Autodesk.Revit.UI import *

clr.AddReference('RevitNodes')
import Revit
clr.ImportExtensions(Revit.GeometryConversion)
clr.ImportExtensions(Revit.Elements)

clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager


doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
view = doc.ActiveView

rplist = UnwrapElement(IN[1]) #Some Reference Plane
cglist = UnwrapElement(IN[2]) #CurtineGridLine

rpref = []
for rp in rplist:
	rpref.append(rp.GetReference())

TransactionManager.Instance.EnsureInTransaction(doc)

options = Options()
options.ComputeReferences = True
options.IncludeNonVisibleObjects = True
options.DetailLevel = ViewDetailLevel.Fine

geomElem = []


for cgl in cglist:
	geomElem.append(cgl.get_Geometry(options))

GLWRf = []
for gr1 in geomElem:
	for gr in gr1:
		try:
			GLWRf.append(gr.Reference)
		except:	
			pass
doc.Regenerate()
TransactionManager.Instance.ForceCloseTransaction()

TransactionManager.Instance.EnsureInTransaction(doc)
doc.Regenerate()
lockedAlign = []
for ref in GLWRf:
	for rprf in rpref:
		try:
			lockedAlign.append(doc.Create.NewAlignment(view, rprf, ref))
		except:	
			pass	

TransactionManager.Instance.TransactionTaskDone()

OUT = ["New Align:",lockedAlign], ["CGL reference:", GLWRf], ["Geometry from CGL", geomElem]
