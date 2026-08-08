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


func portal_disk_pos(system_id: int, toward_star: int) -> Vector3:
	## Portal center on the solar disk toward `toward_star` (Godot XZ).
	## Prefer authored hyperlane coords; empty if missing.
	var content := get_system(system_id)
	if content.is_empty() or toward_star < 0:
		return Vector3.ZERO
	for hl in content.get("hyperlanes", []):
		var h: Dictionary = hl
		if int(h.get("target_star", -1)) != toward_star:
			continue
		return Vector3(float(h.get("x", 0.0)), 0.0, float(h.get("y", 0.0)))
	return Vector3.ZERO


func hyperlane_ring_radius(system_id: int) -> float:
	var content := get_system(system_id)
	if content.is_empty():
		return 0.0
	return float(content.get("hyperlane_ring_radius", 0.0))
