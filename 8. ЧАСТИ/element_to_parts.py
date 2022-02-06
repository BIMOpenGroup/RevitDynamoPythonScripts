import clr
clr.AddReference("System")
from System.Collections.Generic import List

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument

list_elems = UnwrapElement(IN[0])
falis = []

list_id = [elem.Id for elem in list_id]

# [[list_id.append(i) for i in e.GetMemberIds()] if (e.Category.Id.IntegerValue == -2000095) or (e.Category.Id.IntegerValue == -2000267) else list_id.append(e.Id) for e in el_ref ]
# Lel_id = [r1.Id for r1 in el_ref]
# #test = [e.get_Parameter(BuiltInParameter.ELEM_CATEGORY_PARAM).AsValueString() for e in el_ref]
# #test = [e.Category.Id.IntegerValue for e in el_ref if e.Category.Id.IntegerValue == -2000095]
eList = List[ElementId]()
[eList.Add(_id) for _id in list_id if PartUtils.AreElementsValidForCreateParts(doc, List[ElementId]([_id])) and not PartUtils.HasAssociatedParts(doc, _id)]

if IN[1]:
	TransactionManager.Instance.EnsureInTransaction(doc)
	PartUtils.CreateParts(doc, eList)
	TransactionManager.Instance.ForceCloseTransaction()
else:
	for e in eList:
		try:
			TransactionManager.Instance.EnsureInTransaction(doc)
			PartUtils.CreateParts(doc, List[ElementId]([e]))
			TransactionManager.Instance.ForceCloseTransaction()
		except: # noqa
			falis.append(e)
# partsid = [PartUtils.GetAssociatedParts(doc, e, True, True) for e in eList]
# parts = [doc.GetElement(i) for id in partsid for i in id]

OUT = falis 