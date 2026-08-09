extends RefCounted
class_name GalaxyData
## Loads Python-exported galaxy JSON from res://data/galaxy/

const DATA_DIR := "res://data/galaxy/"
const TIER_HOME := 0

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


func sol_star_id() -> int:
	var n := stars.size()
	var sol_id := int(meta.get("sol_star_index", -1))
	if sol_id >= 0 and sol_id < n:
		return sol_id
	for s in stars:
		if String(s.get("special", "")) == "sol" or String(s.get("homeworld_key", "")) == "sol":
			return int(s.get("id", -1))
	return -1


func star_tier(star_id: int) -> int:
	if star_id < 0 or star_id >= stars.size():
		return -1
	return int(stars[star_id].get("tier", -1))


func star_unlock_group(star_id: int) -> int:
	if star_id < 0 or star_id >= stars.size():
		return -999
	return int(stars[star_id].get("unlock_group", -999))


func is_home_home_lane(lane_idx: int, unlock_group: int = -999) -> bool:
	## Both ends HOME tier; if unlock_group >= 0, both must match that group.
	if lane_idx < 0 or lane_idx >= lanes.size():
		return false
	var lane: Dictionary = lanes[lane_idx]
	var a := int(lane.get("a", -1))
	var b := int(lane.get("b", -1))
	if star_tier(a) != TIER_HOME or star_tier(b) != TIER_HOME:
		return false
	if unlock_group < 0:
		return true
	return star_unlock_group(a) == unlock_group and star_unlock_group(b) == unlock_group


func lane_paint(lane_idx: int) -> String:
	if lane_idx < 0 or lane_idx >= lanes.size():
		return ""
	return String(lanes[lane_idx].get("paint", ""))


func lane_cost(lane_idx: int) -> float:
	if lane_idx < 0 or lane_idx >= lanes.size():
		return 3.0
	return float(lanes[lane_idx].get("cost", 3.0))


func is_beltway_or_home_paint(lane_idx: int) -> bool:
	var p := lane_paint(lane_idx)
	return p == "beltway" or p == "green" or p == "home"


func find_lane(a: int, b: int) -> int:
	## Index of undirected lane a↔b, or -1.
	for i in lanes.size():
		var lane: Dictionary = lanes[i]
		var la := int(lane.get("a", -1))
		var lb := int(lane.get("b", -1))
		if (la == a and lb == b) or (la == b and lb == a):
			return i
	return -1


func map_center() -> Vector3:
	var c: Array = meta.get("map_center", [0.86, 0.86])
	return Vector3(float(c[0]), 0.0, float(c[1]))


func region_size() -> float:
	return float(meta.get("region_size", 1.72))


func sol_home_focus() -> Dictionary:
	## Centroid + span of Sol's home-cluster stars (Godot XZ disk, Y up).
	var n := stars.size()
	var sol_id := sol_star_id()
	if sol_id < 0 or sol_id >= n:
		return {"center": map_center(), "region": region_size() * 0.35}

	var sol_ug := star_unlock_group(sol_id)
	var acc := Vector3.ZERO
	var count := 0
	var pts: Array[Vector3] = []
	for i in n:
		var s: Dictionary = stars[i]
		if int(s.get("tier", -1)) != TIER_HOME:
			continue
		if int(s.get("unlock_group", -999)) != sol_ug:
			continue
		var p := Vector3(float(s.get("x", 0.0)), float(s.get("z", 0.0)), float(s.get("y", 0.0)))
		pts.append(p)
		acc += p
		count += 1
	if count == 0:
		var s0: Dictionary = stars[sol_id]
		var p0 := Vector3(float(s0.get("x", 0.0)), float(s0.get("z", 0.0)), float(s0.get("y", 0.0)))
		return {"center": p0, "region": 0.25}
	var center := acc / float(count)
	var max_r := 0.05
	for p2 in pts:
		max_r = maxf(max_r, center.distance_to(p2))
	var region := maxf(max_r * 3.2, 0.18)
	return {"center": center, "region": region}


func star_disk_xy(star_id: int) -> Vector2:
	## Galactic play-disk XY (export x,y → system portal directions). Ignores Z.
	if star_id < 0 or star_id >= stars.size():
		return Vector2.ZERO
	var s: Dictionary = stars[star_id]
	return Vector2(float(s.get("x", 0.0)), float(s.get("y", 0.0)))


func build_adjacency() -> Array:
	## Undirected lane graph: adj[i] = Array of neighbor star ids.
	return build_adjacency_masked(PackedByteArray())


func build_adjacency_masked(allowed_lanes: PackedByteArray) -> Array:
	## If allowed_lanes empty → all lanes. Else only edges with allowed_lanes[li] != 0.
	var n := stars.size()
	var adj: Array = []
	adj.resize(n)
	for i in n:
		adj[i] = []
	var filter := not allowed_lanes.is_empty()
	for li in lanes.size():
		if filter and (li >= allowed_lanes.size() or allowed_lanes[li] == 0):
			continue
		var lane: Dictionary = lanes[li]
		var a := int(lane.get("a", -1))
		var b := int(lane.get("b", -1))
		if a < 0 or b < 0 or a >= n or b >= n or a == b:
			continue
		adj[a].append(b)
		adj[b].append(a)
	return adj


func shortest_path(
	from_star: int, to_star: int, allowed_lanes: PackedByteArray = PackedByteArray()
) -> PackedInt32Array:
	## BFS hop path inclusive of endpoints. Empty if unreachable / invalid.
	## allowed_lanes empty → all geometric lanes; else only unlocked (etc.) edges.
	var n := stars.size()
	var out := PackedInt32Array()
	if from_star < 0 or to_star < 0 or from_star >= n or to_star >= n:
		return out
	if from_star == to_star:
		out.append(from_star)
		return out
	var adj := build_adjacency_masked(allowed_lanes)
	var prev: PackedInt32Array = PackedInt32Array()
	prev.resize(n)
	prev.fill(-1)
	var seen: PackedByteArray = PackedByteArray()
	seen.resize(n)
	seen.fill(0)
	var queue: Array = []
	queue.append(from_star)
	seen[from_star] = 1
	var qi := 0
	var found := false
	while qi < queue.size():
		var u: int = queue[qi]
		qi += 1
		if u == to_star:
			found = true
			break
		for v in adj[u]:
			var vi: int = int(v)
			if seen[vi] != 0:
				continue
			seen[vi] = 1
			prev[vi] = u
			queue.append(vi)
	if not found:
		return out
	var stack: Array = []
	var cur := to_star
	while cur >= 0:
		stack.append(cur)
		if cur == from_star:
			break
		cur = prev[cur]
	stack.reverse()
	for sid in stack:
		out.append(int(sid))
	return out


func pick_starting_home_lanes(count: int) -> PackedInt32Array:
	## Sol-first BFS: up to `count` home↔home lanes in Sol's unlock_group.
	var out := PackedInt32Array()
	var sol_id := sol_star_id()
	var n := stars.size()
	if sol_id < 0 or sol_id >= n or count <= 0:
		return out
	var sol_ug := star_unlock_group(sol_id)
	# Per-star list of home↔home lane indices (sorted for determinism).
	var by_star: Array = []
	by_star.resize(n)
	for i in n:
		by_star[i] = []
	for li in lanes.size():
		if not is_home_home_lane(li, sol_ug):
			continue
		var lane: Dictionary = lanes[li]
		var a := int(lane.get("a", -1))
		var b := int(lane.get("b", -1))
		by_star[a].append(li)
		by_star[b].append(li)
	for i in n:
		var arr: Array = by_star[i]
		arr.sort()
		by_star[i] = arr

	var used: PackedByteArray = PackedByteArray()
	used.resize(lanes.size())
	used.fill(0)
	var queue: Array = [sol_id]
	var reached: PackedByteArray = PackedByteArray()
	reached.resize(n)
	reached.fill(0)
	reached[sol_id] = 1
	var qi := 0
	while qi < queue.size() and out.size() < count:
		var u: int = queue[qi]
		qi += 1
		for li_v in by_star[u]:
			if out.size() >= count:
				break
			var li: int = int(li_v)
			if used[li] != 0:
				continue
			used[li] = 1
			out.append(li)
			var lane: Dictionary = lanes[li]
			var a := int(lane.get("a", -1))
			var b := int(lane.get("b", -1))
			var other := b if a == u else a
			if other >= 0 and other < n and reached[other] == 0:
				reached[other] = 1
				queue.append(other)
	return out


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
