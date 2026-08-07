import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import Wall, WallType, Level, Line, XYZ, FilteredElementCollector

doc = DocumentManager.Instance.CurrentDBDocument
ft_per_m = 3.28084

levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
ground_level = None
for lvl in levels:
    if lvl.Name == "PRM-Ground":
        ground_level = lvl
        break

wall_types = FilteredElementCollector(doc).OfClass(WallType).ToElements()
interior_wall_type = None
for wt in wall_types:
    if wt.Name == "Interior - 125mm Partition":
        interior_wall_type = wt
        break

# Find the wrong-type interior walls by their known coordinates (not by Id)
target_lines = [
    ((8.0, 0.0), (8.0, 12.0)),
    ((0.0, 6.0), (8.0, 6.0)),
    ((8.0, 4.0), (15.0, 4.0)),
]

all_walls = FilteredElementCollector(doc).OfClass(Wall).ToElements()
walls_to_delete = []

for w in all_walls:
    try:
        loc = w.Location.Curve
        s = loc.GetEndPoint(0)
        e = loc.GetEndPoint(1)
        s_m = (round(s.X / ft_per_m, 1), round(s.Y / ft_per_m, 1))
        e_m = (round(e.X / ft_per_m, 1), round(e.Y / ft_per_m, 1))
        for (ts, te) in target_lines:
            if (s_m == ts and e_m == te) and w.WallType.Name != "Interior - 125mm Partition":
                walls_to_delete.append(w.Id)
    except:
        pass

TransactionManager.Instance.EnsureInTransaction(doc)

for wid in walls_to_delete:
    doc.Delete(wid)

partitions = [
    (XYZ(8.0 * ft_per_m, 0.0, 0.0), XYZ(8.0 * ft_per_m, 12.0 * ft_per_m, 0.0)),
    (XYZ(0.0, 6.0 * ft_per_m, 0.0), XYZ(8.0 * ft_per_m, 6.0 * ft_per_m, 0.0)),
    (XYZ(8.0 * ft_per_m, 4.0 * ft_per_m, 0.0), XYZ(15.0 * ft_per_m, 4.0 * ft_per_m, 0.0)),
]

new_walls = []
for start, end in partitions:
    line = Line.CreateBound(start, end)
    wall = Wall.Create(doc, line, interior_wall_type.Id, ground_level.Id, 3.3 * ft_per_m, 0.0, False, False)
    new_walls.append(wall)

TransactionManager.Instance.TransactionTaskDone()

OUT = "Deleted {} wrong-type walls, created {} correct interior partitions using {}".format(
    len(walls_to_delete), len(new_walls), interior_wall_type.Name
)