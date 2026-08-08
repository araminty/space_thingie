extends RefCounted
class_name SystemData
## Loads Python-exported system contents from res://data/systems/contents.json

const PATH := "res://data/systems/contents.json"

var _systems: Array = []
var loaded: bool = false


func load_all() -> Error:
	if not FileAccess.file_exists(PATH):
		push_error("SystemData: missing %s — run export_godot.py" % PATH)
		return ERR_FILE_NOT_FOUND
	var f := FileAccess.open(PATH, FileAccess.READ)
	if f == null:
		return ERR_FILE_CANT_OPEN
	var data = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY:
		return ERR_INVALID_DATA
	_systems = data.get("systems", [])
	loaded = not _systems.is_empty()
	return OK if loaded else ERR_INVALID_DATA


func get_system(star_id: int) -> Dictionary:
	if star_id < 0 or star_id >= _systems.size():
		return {}
	return _systems[star_id]
