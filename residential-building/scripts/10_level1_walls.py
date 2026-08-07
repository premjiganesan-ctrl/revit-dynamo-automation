import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import (
    Wall, WallType, Level, Line, XYZ,
    FilteredElementCollector, BuiltInParameter
)

doc = DocumentManager.Instance.CurrentDBDocument
ft_per_m = 3.28084

levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
level_1 = None
level_2 = None
for lvl in levels:
    if lvl.Name == "PRM-Level 1":
        level_1 = lvl
    if lvl.Name == "PRM-Level 2":
        level_2 = lvl

wall_types = FilteredElementCollector(doc).OfClass(WallType).ToElements()
exterior_wall_type = None
for wt in wall_types:
    if wt.Name == "M_Exterior - Brick on Mtl. Stud":
        exterior_wall_type = wt
        break

width = 15.0
depth = 12.0

corners = [
    XYZ(0.0, 0.0, 0.0),
    XYZ(width * ft_per_m, 0.0, 0.0),
    XYZ(width * ft_per_m, depth * ft_per_m, 0.0),
    XYZ(0.0, depth * ft_per_m, 0.0)
]

# Check existing walls on Level 1 first to avoid duplicates
existing_walls = FilteredElementCollector(doc).OfClass(Wall).ToElements()
level_1_wall_count = 0
for w in existing_walls:
    if w.LevelId == level_1.Id:
        level_1_wall_count += 1

TransactionManager.Instance.EnsureInTransaction(doc)

new_walls = []
if level_1_wall_count == 0:
    for i in range(4):
        start = corners[i]
        end = corners[(i + 1) % 4]
        line = Line.CreateBound(start, end)
        wall = Wall.Create(doc, line, exterior_wall_type.Id, level_1.Id, 3.3 * ft_per_m, 0.0, False, False)
        wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(level_2.Id)
        wall.Flip()
        new_walls.append(wall)

TransactionManager.Instance.TransactionTaskDone()

OUT = "Existing Level 1 walls found: {} | Created {} new perimeter walls on {}".format(
    level_1_wall_count, len(new_walls), level_1.Name
)