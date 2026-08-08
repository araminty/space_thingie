extends RefCounted
class_name GalaxyData
## Loads Python-exported galaxy JSON from res://data/galaxy/

const DATA_DIR := "res://data/galaxy/"
const TIER_HOME := 0
## Prototype fog: Sol home cluster + stars within this many lane hops (all lanes).
const FOG_REVEAL_HOPS := 2

var meta: Dictionary = {}
var stars: Array = []
var lanes: Array = []
## Parallel to star index: 1 = revealed (clickable), 0 = fog of war.
var revealed: PackedByteArray = PackedByteArray()


func load_all() -> Error:
	meta = _load_json_dict(DATA_DIR + "meta.json")
	var stars_doc := _load_json_dict(DATA_DIR + "stars.json")
	var lanes_doc := _load_json_dict(DATA_DIR + "lanes.json")
	if stars_doc.is_empty() or lanes_doc.is_empty():
		push_error("GalaxyData: missing export. Run: .venv/bin/python export_godot.py")
		return ERR_FILE_NOT_FOUND
	stars = stars_doc.get("stars", [])
	lanes = lanes_doc.get("lanes", [])
	_compute_fog_of_war()
	return OK


func is_revealed(star_id: int) -> bool:
	if revealed.is_empty():
		return true
	if star_id < 0 or star_id >= revealed.size():
		return false
	return revealed[star_id] != 0


func revealed_count() -> int:
	var n := 0
	for i in revealed.size():
		if revealed[i] != 0:
			n += 1
	return n


func map_center() -> Vector3:
	var c: Array = meta.get("map_center", [0.86, 0.86])
	return Vector3(float(c[0]), 0.0, float(c[1]))


func region_size() -> float:
	return float(meta.get("region_size", 1.72))


func sol_home_focus() -> Dictionary:
	## Centroid + span of Sol's home-cluster stars (Godot XZ disk, Y up).
	var n := stars.size()
	var sol_id := int(meta.get("sol_star_index", -1))
	if sol_id < 0 or sol_id >= n:
		for s in stars:
			if String(s.get("special", "")) == "sol":
				sol_id = int(s.get("id", -1))
				break
	if sol_id < 0 or sol_id >= n:
		return {"center": map_center(), "region": region_size() * 0.35}

	var sol_ug := int(stars[sol_id].get("unlock_group", -1))
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
	# Pad so the whole cluster fits with a little margin (zoomed in, not whole galaxy).
	var region := maxf(max_r * 3.2, 0.18)
	return {"center": center, "region": region}


func _compute_fog_of_war() -> void:
	## Reveal Sol's home cluster (tier HOME + Sol's unlock_group) and anything
	## within FOG_REVEAL_HOPS jumps on the full lane graph. No discovery yet.
	var n := stars.size()
	revealed = PackedByteArray()
	revealed.resize(n)
	revealed.fill(0)
	if n == 0:
		return

	var sol_id := int(meta.get("sol_star_index", -1))
	if sol_id < 0 or sol_id >= n:
		for s in stars:
			if String(s.get("special", "")) == "sol" or String(s.get("homeworld_key", "")) == "sol":
				sol_id = int(s.get("id", -1))
				break
	if sol_id < 0 or sol_id >= n:
		# Fail-open: no Sol → everything revealed.
		revealed.fill(1)
		return

	var sol_ug := int(stars[sol_id].get("unlock_group", -1))
	var adj: Array = []
	adj.resize(n)
	for i in n:
		adj[i] = []
	for lane in lanes:
		var a := int(lane.get("a", -1))
		var b := int(lane.get("b", -1))
		if a < 0 or b < 0 or a >= n or b >= n:
			continue
		adj[a].append(b)
		adj[b].append(a)

	# Multi-source BFS from every star in Sol's home cluster.
	var queue: Array = []
	var dist: PackedInt32Array = PackedInt32Array()
	dist.resize(n)
	dist.fill(-1)
	for i in n:
		var s: Dictionary = stars[i]
		var sid := int(s.get("id", i))
		if int(s.get("tier", -1)) != TIER_HOME:
			continue
		if int(s.get("unlock_group", -999)) != sol_ug:
			continue
		if sid < 0 or sid >= n:
			continue
		dist[sid] = 0
		queue.append(sid)

	if queue.is_empty():
		# Sol alone if cluster lookup failed.
		dist[sol_id] = 0
		queue.append(sol_id)

	var qi := 0
	while qi < queue.size():
		var u: int = queue[qi]
		qi += 1
		if dist[u] >= FOG_REVEAL_HOPS:
			continue
		for v in adj[u]:
			var vi: int = int(v)
			if dist[vi] >= 0:
				continue
			dist[vi] = dist[u] + 1
			queue.append(vi)

	for i in n:
		if dist[i] >= 0 and dist[i] <= FOG_REVEAL_HOPS:
			revealed[i] = 1


func star_disk_xy(star_id: int) -> Vector2:
	## Galactic play-disk XY (export x,y → system portal directions). Ignores Z.
	if star_id < 0 or star_id >= stars.size():
		return Vector2.ZERO
	var s: Dictionary = stars[star_id]
	return Vector2(float(s.get("x", 0.0)), float(s.get("y", 0.0)))


func build_adjacency() -> Array:
	## Undirected lane graph: adj[i] = Array of neighbor star ids.
	var n := stars.size()
	var adj: Array = []
	adj.resize(n)
	for i in n:
		adj[i] = []
	for lane in lanes:
		var a := int(lane.get("a", -1))
		var b := int(lane.get("b", -1))
		if a < 0 or b < 0 or a >= n or b >= n or a == b:
			continue
		adj[a].append(b)
		adj[b].append(a)
	return adj


func shortest_path(from_star: int, to_star: int) -> PackedInt32Array:
	## BFS hop path inclusive of endpoints. Empty if unreachable / invalid.
	var n := stars.size()
	var out := PackedInt32Array()
	if from_star < 0 or to_star < 0 or from_star >= n or to_star >= n:
		return out
	if from_star == to_star:
		out.append(from_star)
		return out
	var adj := build_adjacency()
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
