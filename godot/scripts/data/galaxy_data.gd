extends RefCounted
class_name GalaxyData
## Loads Python-exported galaxy JSON from res://data/galaxy/

const DATA_DIR := "res://data/galaxy/"

var meta: Dictionary = {}
var stars: Array = []
var lanes: Array = []


func load_all() -> Error:
	meta = _load_json_dict(DATA_DIR + "meta.json")
	var stars_doc := _load_json_dict(DATA_DIR + "stars.json")
	var lanes_doc := _load_json_dict(DATA_DIR + "lanes.json")
	if stars_doc.is_empty() or lanes_doc.is_empty():
		push_error("GalaxyData: missing export. Run: .venv/bin/python export_godot.py")
		return ERR_FILE_NOT_FOUND
	stars = stars_doc.get("stars", [])
	lanes = lanes_doc.get("lanes", [])
	return OK


func map_center() -> Vector3:
	var c: Array = meta.get("map_center", [0.86, 0.86])
	return Vector3(float(c[0]), 0.0, float(c[1]))


func region_size() -> float:
	return float(meta.get("region_size", 1.72))


func _load_json_dict(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		push_warning("GalaxyData: file not found: %s" % path)
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var text := f.get_as_text()
	var data = JSON.parse_string(text)
	if typeof(data) != TYPE_DICTIONARY:
		return {}
	return data
