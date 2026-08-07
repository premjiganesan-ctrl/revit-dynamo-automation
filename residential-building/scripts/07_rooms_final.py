import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import Level, UV, FilteredElementCollector, SpatialElement

doc = DocumentManager.Instance.CurrentDBDocument
ft_per_m = 3.28084

levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
ground_level = None
for lvl in levels:
    if lvl.Name == "PRM-Ground":
        ground_level = lvl
        break

existing_rooms = FilteredElementCollector(doc).OfClass(SpatialElement).ToElements()
room_ids_to_delete = [r.Id for r in existing_rooms if r.Category is not None and r.Category.Name == "Rooms"]

TransactionManager.Instance.EnsureInTransaction(doc)

for rid in room_ids_to_delete:
    doc.Delete(rid)

room_data = [
    ("Living Room", 4.0, 3.0),
    ("Bedroom", 4.0, 9.0),
    ("Bathroom", 11.5, 2.0),
    ("Kitchen", 11.5, 8.0),
]

new_rooms = []
for name, x, y in room_data:
    point = UV(x * ft_per_m, y * ft_per_m)
    room = doc.Create.NewRoom(ground_level, point)
    room.Name = name
    new_rooms.append(room)

TransactionManager.Instance.TransactionTaskDone()

OUT = "Deleted {} old room(s), created {} new rooms: {}".format(
    len(room_ids_to_delete), len(new_rooms), [r.Name for r in new_rooms]
)