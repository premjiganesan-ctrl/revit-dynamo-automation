import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Level

doc = DocumentManager.Instance.CurrentDBDocument

levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
ground_level = None
for lvl in levels:
    if lvl.Name == "PRM-Ground":
        ground_level = lvl

all_windows = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()

TransactionManager.Instance.EnsureInTransaction(doc)

flipped_count = 0
for win in all_windows:
    if win.LevelId == ground_level.Id:
        if win.CanFlipFacing:
            win.flipFacing()
            flipped_count += 1

TransactionManager.Instance.TransactionTaskDone()

OUT = "Flipped {} windows on {}".format(flipped_count, ground_level.Name)