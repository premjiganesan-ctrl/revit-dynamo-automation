import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import FilteredElementCollector, FamilySymbol, BuiltInCategory, Wall, Level, XYZ, Structure

doc = DocumentManager.Instance.CurrentDBDocument
ft_per_m = 3.28084

levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
level_1 = None
for lvl in levels:
    if lvl.Name == "PRM-Level 1":
        level_1 = lvl

window_symbols = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).OfClass(FamilySymbol).ToElements()

normal_type = None
bathroom_type = None
for ws in window_symbols:
    if ws.Name == "900 x 1200mm":
        normal_type = ws
    if ws.Name == "600 x 900mm":
        bathroom_type = ws

all_walls = FilteredElementCollector(doc).OfClass(Wall).ToElements()

target_walls = {"front": ((0.0, 0.0), (15.0, 0.0)), "back": ((15.0, 12.0), (0.0, 12.0)), "left": ((0.0, 12.0), (0.0, 0.0)), "right": ((15.0, 0.0), (15.0, 12.0))}

found_walls = {}
for w in all_walls:
    if w.LevelId == level_1.Id and w.WallType.Name == "M_Exterior - Brick on Mtl. Stud":
        loc = w.Location.Curve
        s = loc.GetEndPoint(0)
        e = loc.GetEndPoint(1)
        s_m = (round(s.X / ft_per_m, 1), round(s.Y / ft_per_m, 1))
        e_m = (round(e.X / ft_per_m, 1), round(e.Y / ft_per_m, 1))
        for name, pair in target_walls.items():
            if s_m == pair[0] and e_m == pair[1]:
                found_walls[name] = w

window_positions = {"front": [3.0, 11.0], "back": [3.0, 11.0], "left": [4.0]}
bathroom_pos = 10.5

TransactionManager.Instance.EnsureInTransaction(doc)

if not normal_type.IsActive:
    normal_type.Activate()
if not bathroom_type.IsActive:
    bathroom_type.Activate()

new_windows = []

for name, wall in found_walls.items():
    positions = window_positions.get(name, [])
    for pos in positions:
        if name == "front":
            pt = XYZ(pos * ft_per_m, 0.0, level_1.Elevation)
        elif name == "back":
            pt = XYZ((15.0 - pos) * ft_per_m, 12.0 * ft_per_m, level_1.Elevation)
        elif name == "left":
            pt = XYZ(0.0, (12.0 - pos) * ft_per_m, level_1.Elevation)
        win = doc.Create.NewFamilyInstance(pt, normal_type, wall, level_1, Structure.StructuralType.NonStructural)
        sill_param = win.LookupParameter("Sill Height")
        if sill_param:
            sill_param.Set(0.9 * ft_per_m)
        if win.CanFlipFacing:
            win.flipFacing()
        new_windows.append(win)

if "right" in found_walls:
    pt = XYZ(15.0 * ft_per_m, bathroom_pos * ft_per_m, level_1.Elevation)
    bath_win = doc.Create.NewFamilyInstance(pt, bathroom_type, found_walls["right"], level_1, Structure.StructuralType.NonStructural)
    sill_param = bath_win.LookupParameter("Sill Height")
    if sill_param:
        sill_param.Set(1.5 * ft_per_m)
    if bath_win.CanFlipFacing:
        bath_win.flipFacing()
    new_windows.append(bath_win)

TransactionManager.Instance.TransactionTaskDone()

OUT = "Placed {} windows on {} (normal: 900x1200mm, bathroom: 600x900mm), pre-flipped for correct orientation".format(len(new_windows), level_1.Name)