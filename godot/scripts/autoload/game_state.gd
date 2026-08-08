extends Node
## Global navigation + shared simulation clock + live fleets + proximity battles.

signal entered_system(star_id: int)
signal returned_to_galaxy
signal day_changed(day: float)
signal playing_changed(playing: bool)
signal play_speed_changed(speed: float)
signal fleets_changed
signal battles_changed
signal fleet_selection_changed(fleet_id: String)

## 48 half-hours per day; play advances at prior rate / 48.
const HALF_HOURS_PER_DAY := 48.0
const DAYS_PER_SECOND := 24.0 / HALF_HOURS_PER_DAY  # 0.5 days/sec at 1×
## Multipliers relative to DAYS_PER_SECOND (¼× … 16×).
const PLAY_SPEEDS: Array[float] = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
const HYPERLANE_TRAVEL_DAYS := 28.0
## Edge-to-edge (diameter) crossing time at fleet cruise speed (matches SystemView).
const FLEET_CROSSING_DAYS := 20.0
## Min days between hyperlane *entries* (set when transit begins).
const HYPERLANE_ENTRY_COOLDOWN_DAYS := 28.0
## Seed / unset: fleet may enter a hyperlane immediately.
const HYPERLANE_ENTER_READY_DAY := -999.0
const FLEET_ARRIVE_EPS_AU := 0.002
const FOLLOW_STANDOFF_AU := 0.02
## Fallback system edge when contents lack ring / planet extents.
const DEFAULT_SYSTEM_EDGE_AU := 8.0
## One battle round every half hour of simulation time.
const HALF_HOUR_DAYS := 1.0 / HALF_HOURS_PER_DAY
## Start a new fight vs a lone hostile.
const BATTLE_CONTACT_AU := 0.25
## Join an ongoing multi-fleet engagement (nearest engaged participant).
const BATTLE_JOIN_AU := 0.30

var current_star_id: int = -1
var in_system: bool = false
## Last successfully entered system (for galaxy double-Tab). Not cleared on return.
var last_system_id: int = -1
var day: float = 0.0
var playing: bool = false
## Wall-clock multiplier on DAYS_PER_SECOND while playing (default 1×).
var play_speed: float = 1.0
## Fog of war: empty = all systems open; else 1 = revealed. Set by galaxy map.
var discovered: PackedByteArray = PackedByteArray()
## Live fleets keyed by id. See register_fleet / begin_hyperlane_transit.
## Optional fields: ordered, dest_x/z, pursue_fleet_id, orbiting, engaged, battle_id,
##   route (Array of system_cruise / hyperlane hops),
##   last_hyperlane_enter_day (sim day when last lane entry began; ready if unset / ≤ READY).
var fleets: Dictionary = {}
## Shared selection across system / galaxy (empty = none). Persists across
## galaxy ↔ system view switches; cleared only by Esc / explicit deselect / LMB empty.
var selected_fleet_id: String = ""
## Active battles keyed by id → {id, friendly_ids, hostile_ids, friendly_id,
##   hostile_id, system_id, next_round_day, round, side_a, side_b, last_summary}.
## friendly_id / hostile_id are the first participant on each side (compat).
var battles: Dictionary = {}
## Lazy map data for multi-hop pathing (portal coords + lane BFS).
var _galaxy_data: GalaxyData = null
var _system_data: SystemData = null
## Arrival pose = portal center × this (inward of oval). Matches SystemView.
const ARRIVAL_INSET := 0.72
## Last sim day used for in-system cruise dt (−1 = uninitialized).
var _fleet_sim_day: float = -1.0


func _process(delta: float) -> void:
	if not playing:
		return
	day += DAYS_PER_SECOND * play_speed * delta
	_tick_fleet_arrivals()
	_tick_system_fleet_motion()
	_tick_proximity_battles_all()
	_tick_battles()
	day_changed.emit(day)


func toggle_play() -> void:
	playing = not playing
	playing_changed.emit(playing)


func set_playing(value: bool) -> void:
	if playing == value:
		return
	playing = value
	playing_changed.emit(playing)


func set_play_speed(speed: float) -> void:
	## Snap to nearest offered multiplier; leave playing state unchanged.
	var best := PLAY_SPEEDS[0]
	var best_d := absf(speed - best)
	for s in PLAY_SPEEDS:
		var d := absf(speed - s)
		if d < best_d:
			best_d = d
			best = s
	if is_equal_approx(play_speed, best):
		return
	play_speed = best
	play_speed_changed.emit(play_speed)


func cycle_play_speed(dir: int) -> void:
	## dir > 0 → faster, dir < 0 → slower; clamps at ends.
	if dir == 0:
		return
	var idx := 0
	var best_d := absf(play_speed - PLAY_SPEEDS[0])
	for i in range(PLAY_SPEEDS.size()):
		var d := absf(play_speed - PLAY_SPEEDS[i])
		if d < best_d:
			best_d = d
			idx = i
	idx = clampi(idx + (1 if dir > 0 else -1), 0, PLAY_SPEEDS.size() - 1)
	set_play_speed(PLAY_SPEEDS[idx])


func is_discovered(star_id: int) -> bool:
	if discovered.is_empty():
		return true
	if star_id < 0 or star_id >= discovered.size():
		return false
	return discovered[star_id] != 0


func enter_system(star_id: int) -> void:
	if not is_discovered(star_id):
		return
	current_star_id = star_id
	last_system_id = star_id
	in_system = true
	entered_system.emit(star_id)


func return_to_galaxy() -> void:
	in_system = false
	current_star_id = -1
	returned_to_galaxy.emit()


func day_label_text() -> String:
	## Whole days + half-hour step within the day (0..47 → 0h..23.5h).
	var whole := int(floor(day))
	var frac := day - float(whole)
	var half := int(floor(frac * HALF_HOURS_PER_DAY + 1e-6))
	half = clampi(half, 0, int(HALF_HOURS_PER_DAY) - 1)
	var hours := int(half / 2.0)
	var mins := 0 if (half % 2) == 0 else 30
	return "day %d  %02d:%02d" % [whole, hours, mins]


func has_fleet(fleet_id: String) -> bool:
	return fleets.has(fleet_id)


func register_fleet(fleet: Dictionary) -> void:
	## Idempotent seed from system content / arrival.
	var fid := String(fleet.get("id", ""))
	if fid.is_empty() or fleets.has(fid):
		return
	var f: Dictionary = fleet.duplicate(true)
	if not f.has("last_hyperlane_enter_day"):
		f["last_hyperlane_enter_day"] = HYPERLANE_ENTER_READY_DAY
	fleets[fid] = f
	fleets_changed.emit()


func hyperlane_entry_cooldown_left(fleet_id: String) -> float:
	## Days until this fleet may begin a hyperlane again (0 = ready).
	if not fleets.has(fleet_id):
		return 0.0
	var last := float(fleets[fleet_id].get("last_hyperlane_enter_day", HYPERLANE_ENTER_READY_DAY))
	return maxf(0.0, (last + HYPERLANE_ENTRY_COOLDOWN_DAYS) - day)


func can_begin_hyperlane_transit(fleet_id: String) -> bool:
	return hyperlane_entry_cooldown_left(fleet_id) <= 0.0


func update_fleet_system_pose(fleet_id: String, system_id: int, pos: Vector3) -> void:
	if not fleets.has(fleet_id):
		return
	var f: Dictionary = fleets[fleet_id]
	if String(f.get("status", "")) != "in_system":
		return
	f["system_id"] = system_id
	f["pos_x"] = pos.x
	f["pos_z"] = pos.z
	f["needs_placement"] = false


func select_fleet(fleet_id: String) -> void:
	## Empty id clears. Selecting a missing id also clears.
	var next := fleet_id if (not fleet_id.is_empty() and fleets.has(fleet_id)) else ""
	if selected_fleet_id == next:
		return
	selected_fleet_id = next
	fleet_selection_changed.emit(selected_fleet_id)


func clear_fleet_selection() -> void:
	select_fleet("")


func _ensure_map_data() -> void:
	if _galaxy_data == null:
		_galaxy_data = GalaxyData.new()
		_galaxy_data.load_all()
	if _system_data == null:
		_system_data = SystemData.new()
		_system_data.load_all()


func clear_fleet_route(fleet_id: String) -> void:
	if not fleets.has(fleet_id):
		return
	fleets[fleet_id]["route"] = []


func fleet_route(fleet_id: String) -> Array:
	if not fleets.has(fleet_id):
		return []
	var r = fleets[fleet_id].get("route", [])
	return r if typeof(r) == TYPE_ARRAY else []


func portal_disk_pos(system_id: int, toward_star: int) -> Vector3:
	## Portal center in system_id toward toward_star (Godot XZ). Uses contents,
	## else ring radius × galactic outward direction.
	_ensure_map_data()
	var pos := _system_data.portal_disk_pos(system_id, toward_star)
	if pos.length_squared() > 1e-8:
		return pos
	var ring := _system_data.hyperlane_ring_radius(system_id)
	if ring < 1e-6:
		ring = 8.0
	var here := _galaxy_data.star_disk_xy(system_id)
	var dest := _galaxy_data.star_disk_xy(toward_star)
	var dxy := dest - here
	if dxy.length_squared() < 1e-12:
		return Vector3(ring, 0.0, 0.0)
	var outward := dxy.normalized()
	return Vector3(outward.x * ring, 0.0, outward.y * ring)


func arrival_inward_pos(system_id: int, arrived_from: int) -> Vector3:
	## Standard spawn inward of the return portal (~72% of portal radius).
	var portal := portal_disk_pos(system_id, arrived_from)
	if portal.length_squared() < 1e-8:
		var ring := DEFAULT_SYSTEM_EDGE_AU
		_ensure_map_data()
		var r := _system_data.hyperlane_ring_radius(system_id)
		if r > 1e-6:
			ring = r
		return Vector3(ring * ARRIVAL_INSET * 0.5, 0.0, 0.0)
	return portal * ARRIVAL_INSET


func system_cruise_edge_au(system_id: int) -> float:
	## Approximate system edge (AU) for cruise speed — ring / portals / planets.
	_ensure_map_data()
	var content := _system_data.get_system(system_id)
	if content.is_empty():
		return DEFAULT_SYSTEM_EDGE_AU
	var edge := 1.0
	edge = maxf(edge, float(content.get("hyperlane_ring_radius", 0.0)))
	for hl in content.get("hyperlanes", []):
		var h: Dictionary = hl
		var hx := float(h.get("x", 0.0))
		var hy := float(h.get("y", 0.0))
		edge = maxf(edge, sqrt(hx * hx + hy * hy) + 1.0)
	for p in content.get("planets", []):
		var pd: Dictionary = p
		edge = maxf(edge, float(pd.get("orbital_radius", 0.0)))
	for af in content.get("asteroid_fields", []):
		var ad: Dictionary = af
		var a := float(ad.get("orbital_radius", 0.0))
		var half_w := 0.5 * float(ad.get("radial_width", 0.0))
		edge = maxf(edge, a + half_w)
	if edge <= 1.0 + 1e-6:
		return DEFAULT_SYSTEM_EDGE_AU
	return edge


func fleet_cruise_speed_au_per_day(system_id: int) -> float:
	## Diameter crossing / FLEET_CROSSING_DAYS (same formula as SystemView).
	return (2.0 * system_cruise_edge_au(system_id)) / FLEET_CROSSING_DAYS


func resolve_fleet_placement(fleet_id: String) -> void:
	## Apply arrival-inward pose when needs_placement (works off-screen).
	if not fleets.has(fleet_id):
		return
	_resolve_fleet_placement(fleets[fleet_id])


func _resolve_fleet_placement(f: Dictionary) -> void:
	if not bool(f.get("needs_placement", false)):
		return
	if String(f.get("status", "")) != "in_system":
		return
	var sys := int(f.get("system_id", -1))
	var from_star := int(f.get("arrived_from", -1))
	var pos := arrival_inward_pos(sys, from_star)
	f["pos_x"] = pos.x
	f["pos_z"] = pos.z
	f["needs_placement"] = false


func _tick_system_fleet_motion() -> void:
	## Authoritative in-system cruise for all systems (galaxy map or system view).
	## Day-delta motion; portal reach → begin_hyperlane_transit; final dest → route pop.
	## Position updates do not emit fleets_changed (views sync on day_changed).
	if _fleet_sim_day < 0.0:
		_fleet_sim_day = day
		return
	var dt := day - _fleet_sim_day
	_fleet_sim_day = day
	if dt <= 0.0:
		return
	var emit_change := false
	var ids: Array = fleets.keys()
	for fid_v in ids:
		var fid := String(fid_v)
		if not fleets.has(fid):
			continue
		var f: Dictionary = fleets[fid]
		if String(f.get("status", "")) != "in_system":
			continue
		if bool(f.get("hostile", false)) or bool(f.get("stationary", false)):
			continue
		if bool(f.get("engaged", false)):
			continue
		if bool(f.get("needs_placement", false)):
			_resolve_fleet_placement(f)
		# Pursue: retarget cruise dest each tick (standoff).
		var pursue_id := String(f.get("pursue_fleet_id", ""))
		if not pursue_id.is_empty():
			if not _retarget_pursuit(f, pursue_id):
				emit_change = true
				continue
		if not bool(f.get("ordered", false)):
			continue
		var sys := int(f.get("system_id", -1))
		var speed := fleet_cruise_speed_au_per_day(sys)
		var px := float(f.get("pos_x", 0.0))
		var pz := float(f.get("pos_z", 0.0))
		var dx := float(f.get("dest_x", px))
		var dz := float(f.get("dest_z", pz))
		var ddx := dx - px
		var ddz := dz - pz
		var dist := sqrt(ddx * ddx + ddz * ddz)
		var nx := px
		var nz := pz
		if dist <= FLEET_ARRIVE_EPS_AU:
			nx = dx
			nz = dz
		else:
			var step := minf(speed * dt, dist)
			var inv := 1.0 / dist
			nx = px + ddx * inv * step
			nz = pz + ddz * inv * step
		f["pos_x"] = nx
		f["pos_z"] = nz
		f["orbiting"] = false
		var pos := Vector3(nx, 0.0, nz)
		if _try_enter_portal_at(fid, f, pos):
			# begin_hyperlane_transit already emitted fleets_changed.
			continue
		if Vector3(nx, 0.0, nz).distance_to(Vector3(dx, 0.0, dz)) <= FLEET_ARRIVE_EPS_AU:
			# At cruise dest: start routed hyperlane, else clear/pop cruise.
			var route_dest := route_next_hyperlane_dest(fid)
			if route_dest >= 0:
				begin_hyperlane_transit(fid, sys, route_dest)
			else:
				on_fleet_reached_disk_dest(fid)
	if emit_change:
		fleets_changed.emit()


func _retarget_pursuit(f: Dictionary, pursue_id: String) -> bool:
	## Update dest toward live target; returns false if chase cleared (target gone).
	if not fleets.has(pursue_id):
		f["pursue_fleet_id"] = ""
		f["ordered"] = false
		f["orbiting"] = false
		return false
	var t: Dictionary = fleets[pursue_id]
	if String(t.get("status", "")) != "in_system":
		f["pursue_fleet_id"] = ""
		f["ordered"] = false
		f["orbiting"] = false
		return false
	if int(t.get("system_id", -1)) != int(f.get("system_id", -1)):
		f["pursue_fleet_id"] = ""
		f["ordered"] = false
		f["orbiting"] = false
		return false
	var px := float(f.get("pos_x", 0.0))
	var pz := float(f.get("pos_z", 0.0))
	var tx := float(t.get("pos_x", 0.0))
	var tz := float(t.get("pos_z", 0.0))
	var dest := _pursue_standoff_dest(Vector3(px, 0.0, pz), Vector3(tx, 0.0, tz))
	f["ordered"] = true
	f["orbiting"] = false
	f["dest_x"] = dest.x
	f["dest_z"] = dest.z
	return true


func _pursue_standoff_dest(pursuer_pos: Vector3, target_pos: Vector3) -> Vector3:
	var p := Vector3(pursuer_pos.x, 0.0, pursuer_pos.z)
	var t := Vector3(target_pos.x, 0.0, target_pos.z)
	var to_t := t - p
	var dist := to_t.length()
	if dist <= FOLLOW_STANDOFF_AU:
		return p
	return t - (to_t / dist) * FOLLOW_STANDOFF_AU


func _nearest_portal(system_id: int, pos: Vector3) -> Dictionary:
	## Portal whose oval contains pos (approximate radius from contents).
	_ensure_map_data()
	var content := _system_data.get_system(system_id)
	if content.is_empty():
		return {}
	var best: Dictionary = {}
	var best_d := 1e9
	for hl in content.get("hyperlanes", []):
		var h: Dictionary = hl
		var cx := float(h.get("x", 0.0))
		var cy := float(h.get("y", 0.0))
		var ah := float(h.get("along_half", 0.35))
		var ch := float(h.get("across_half", 0.55))
		var radius := maxf(ah, ch) + 0.25
		var c := Vector3(cx, 0.0, cy)
		var d := Vector3(pos.x, 0.0, pos.z).distance_to(c)
		if d <= radius and d < best_d:
			best_d = d
			best = {
				"center": c,
				"radius": radius,
				"target_star": int(h.get("target_star", -1)),
				"target_label": String(h.get("target_label", "System")),
				"name": String(h.get("name", "Hyperlane Entry")),
			}
	return best


func _try_enter_portal_at(fleet_id: String, f: Dictionary, pos: Vector3) -> bool:
	var sys := int(f.get("system_id", -1))
	var portal := _nearest_portal(sys, pos)
	if portal.is_empty():
		return false
	var dest := int(portal.get("target_star", -1))
	if dest < 0:
		return false
	var route_dest := route_next_hyperlane_dest(fleet_id)
	if route_dest >= 0 and route_dest != dest:
		return false
	return begin_hyperlane_transit(fleet_id, sys, dest)


func _tick_proximity_battles_all() -> void:
	## Contact / join using GameState poses in every system that has fleets.
	var systems: Dictionary = {}
	for fid in fleets.keys():
		var f: Dictionary = fleets[fid]
		if String(f.get("status", "")) != "in_system":
			continue
		var sid := int(f.get("system_id", -1))
		if sid >= 0:
			systems[sid] = true
	for sid_v in systems.keys():
		var sid := int(sid_v)
		try_join_proximity_battles(sid)
		try_start_proximity_battles(sid)


func set_fleet_disk_destination(fleet_id: String, dest: Vector3) -> bool:
	## Fixed RMB disk dest. Clears pursue + multi-hop route.
	if not fleets.has(fleet_id):
		return false
	var f: Dictionary = fleets[fleet_id]
	if bool(f.get("hostile", false)) or bool(f.get("stationary", false)):
		return false
	if bool(f.get("engaged", false)):
		return false
	if String(f.get("status", "")) != "in_system":
		return false
	f["route"] = []
	f["pursue_fleet_id"] = ""
	f["ordered"] = true
	f["orbiting"] = false
	f["dest_x"] = dest.x
	f["dest_z"] = dest.z
	fleets_changed.emit()
	return true


func order_fleet_path_to_star(fleet_id: String, target_star: int) -> bool:
	## Multi-hop lane path to target_star. In-system: from current system.
	## Mid-transit A→B: pick continue-to-B vs reverse-to-A by fractional
	## lane cost + BFS hops, then queue route from the chosen end to D.
	## Clears pursue / prior route. Final waypoint = arrival-inward pose.
	if not fleets.has(fleet_id):
		return false
	var f: Dictionary = fleets[fleet_id]
	if bool(f.get("hostile", false)) or bool(f.get("stationary", false)):
		return false
	if bool(f.get("engaged", false)):
		return false
	if target_star < 0:
		return false
	_ensure_map_data()
	if not is_discovered(target_star):
		return false
	var status := String(f.get("status", ""))
	if status == "in_transit":
		return _order_transit_path_to_star(f, target_star)
	if status != "in_system":
		return false
	var from_star := int(f.get("system_id", -1))
	if from_star < 0 or from_star == target_star:
		return false
	var path := _galaxy_data.shortest_path(from_star, target_star)
	if path.size() < 2:
		return false
	f["route"] = _build_multi_hop_route(path)
	f["pursue_fleet_id"] = ""
	f["orbiting"] = false
	_apply_current_route_cruise(f)
	fleets_changed.emit()
	return true


func _order_transit_path_to_star(f: Dictionary, target_star: int) -> bool:
	## Mid-lane re-route. Cost continue = (1−p)+hops(B,D); reverse = p+hops(A,D).
	## Prefer continue on ties / equal cost. Route starts after this transit.
	var a := int(f.get("from_star", -1))
	var b := int(f.get("to_star", -1))
	if a < 0 or b < 0 or a == b:
		return false
	var hops_a := _lane_hop_count(a, target_star)
	var hops_b := _lane_hop_count(b, target_star)
	if hops_a < 0 and hops_b < 0:
		return false
	var p := transit_progress(f)
	var do_reverse := false
	if hops_b < 0:
		do_reverse = true
	elif hops_a >= 0:
		var cost_continue := (1.0 - p) + float(hops_b)
		var cost_reverse := p + float(hops_a)
		do_reverse = cost_reverse < cost_continue
	# Chosen arrival end before mutating transit direction.
	var arrival := a if do_reverse else b
	var via := b if do_reverse else a
	var route: Array = []
	if arrival == target_star:
		var final_pos := arrival_inward_pos(arrival, via)
		route.append({
			"kind": "system_cruise",
			"system": arrival,
			"to_x": final_pos.x,
			"to_z": final_pos.z,
		})
	else:
		var path := _galaxy_data.shortest_path(arrival, target_star)
		if path.size() < 2:
			return false
		route = _build_multi_hop_route(path)
	if do_reverse:
		_flip_transit_direction(f)
	f["route"] = route
	f["pursue_fleet_id"] = ""
	f["orbiting"] = false
	fleets_changed.emit()
	return true


func _lane_hop_count(from_star: int, to_star: int) -> int:
	## BFS edge count; 0 if same star; −1 if unreachable.
	if from_star == to_star:
		return 0
	var path := _galaxy_data.shortest_path(from_star, to_star)
	if path.is_empty():
		return -1
	return path.size() - 1


func _build_multi_hop_route(path: PackedInt32Array) -> Array:
	## path = [s0…sn], n≥1. Cruise+hyperlane per hop, then final inward cruise.
	var route: Array = []
	if path.size() < 2:
		return route
	for i in range(path.size() - 1):
		var s0 := int(path[i])
		var s1 := int(path[i + 1])
		var portal := portal_disk_pos(s0, s1)
		route.append({
			"kind": "system_cruise",
			"system": s0,
			"to_x": portal.x,
			"to_z": portal.z,
		})
		route.append({
			"kind": "hyperlane",
			"from": s0,
			"to": s1,
		})
	var final_star := int(path[path.size() - 1])
	var prev_star := int(path[path.size() - 2])
	var final_pos := arrival_inward_pos(final_star, prev_star)
	route.append({
		"kind": "system_cruise",
		"system": final_star,
		"to_x": final_pos.x,
		"to_z": final_pos.z,
	})
	return route


func _flip_transit_direction(f: Dictionary) -> void:
	## Swap ends and remap progress so the marker stays put. No emit / route clear.
	var from_star := int(f.get("from_star", -1))
	var to_star := int(f.get("to_star", -1))
	var p := transit_progress(f)
	var dur := maxf(float(f.get("transit_days", HYPERLANE_TRAVEL_DAYS)), 0.001)
	f["from_star"] = to_star
	f["to_star"] = from_star
	f["transit_start_day"] = day - (1.0 - p) * dur


func _apply_current_route_cruise(f: Dictionary) -> void:
	## If the head of the route is a system_cruise for the fleet's system, set dest.
	var route = f.get("route", [])
	if typeof(route) != TYPE_ARRAY or route.is_empty():
		return
	var hop: Dictionary = route[0]
	if String(hop.get("kind", "")) != "system_cruise":
		return
	var sys := int(hop.get("system", -1))
	if int(f.get("system_id", -1)) != sys:
		return
	f["ordered"] = true
	f["orbiting"] = false
	f["dest_x"] = float(hop.get("to_x", 0.0))
	f["dest_z"] = float(hop.get("to_z", 0.0))


func route_next_hyperlane_dest(fleet_id: String) -> int:
	## Expected portal target for the current hop (−1 if none / not matching).
	var route := fleet_route(fleet_id)
	if route.is_empty():
		return -1
	# Head may be system_cruise; next should be hyperlane.
	var i := 0
	if String(route[0].get("kind", "")) == "system_cruise":
		i = 1
	if i >= route.size():
		return -1
	var hop: Dictionary = route[i]
	if String(hop.get("kind", "")) != "hyperlane":
		return -1
	return int(hop.get("to", -1))


func on_fleet_reached_disk_dest(fleet_id: String) -> void:
	## Called when a fleet arrives at its cruise dest without entering a portal.
	## Pops a matching system_cruise; clears ordered when the route is done.
	if not fleets.has(fleet_id):
		return
	var f: Dictionary = fleets[fleet_id]
	var route = f.get("route", [])
	if typeof(route) != TYPE_ARRAY or route.is_empty():
		f["ordered"] = false
		return
	var hop: Dictionary = route[0]
	if String(hop.get("kind", "")) == "system_cruise":
		if int(hop.get("system", -1)) == int(f.get("system_id", -1)):
			route.remove_at(0)
			f["route"] = route
	if route.is_empty():
		f["ordered"] = false
		f["orbiting"] = false
	elif String(route[0].get("kind", "")) == "system_cruise":
		_apply_current_route_cruise(f)
	fleets_changed.emit()


func begin_hyperlane_transit(fleet_id: String, from_star: int, to_star: int) -> bool:
	if not fleets.has(fleet_id):
		return false
	if is_fleet_engaged(fleet_id):
		return false
	if bool(fleets[fleet_id].get("hostile", false)):
		return false
	if to_star < 0 or from_star < 0 or to_star == from_star:
		return false
	# Entry cooldown: block until ready; cruise tick keeps ordered at portal and retries.
	if not can_begin_hyperlane_transit(fleet_id):
		return false
	var f: Dictionary = fleets[fleet_id]
	_consume_route_on_transit_begin(f, from_star, to_star)
	f["status"] = "in_transit"
	f["system_id"] = -1
	f["from_star"] = from_star
	f["to_star"] = to_star
	f["transit_start_day"] = day
	f["transit_days"] = HYPERLANE_TRAVEL_DAYS
	f["last_hyperlane_enter_day"] = day
	f["needs_placement"] = true
	f["ordered"] = false
	f["pursue_fleet_id"] = ""
	f["orbiting"] = false
	# Anyone chasing this fleet stops at their current pose.
	_clear_pursuers_of(fleet_id)
	fleets_changed.emit()
	return true


func _consume_route_on_transit_begin(f: Dictionary, from_star: int, to_star: int) -> void:
	## Drop matching cruise + hyperlane hops; clear route on mismatch.
	var route = f.get("route", [])
	if typeof(route) != TYPE_ARRAY or route.is_empty():
		f["route"] = []
		return
	var i := 0
	if String(route[0].get("kind", "")) == "system_cruise":
		if int(route[0].get("system", -1)) != from_star:
			f["route"] = []
			return
		i = 1
	if i >= route.size():
		f["route"] = []
		return
	var hop: Dictionary = route[i]
	if String(hop.get("kind", "")) != "hyperlane":
		f["route"] = []
		return
	if int(hop.get("from", -1)) != from_star or int(hop.get("to", -1)) != to_star:
		f["route"] = []
		return
	# Remove consumed hops (cruise + hyperlane).
	var next: Array = []
	for j in range(i + 1, route.size()):
		next.append(route[j])
	f["route"] = next


func reverse_hyperlane_transit(fleet_id: String) -> bool:
	## Flip direction mid-lane. At progress p toward B, swap ends and set
	## progress' = 1−p so the marker stays put and remaining time is p·transit_days.
	## Clears any remaining multi-hop route (simplicity).
	if not fleets.has(fleet_id):
		return false
	var f: Dictionary = fleets[fleet_id]
	if String(f.get("status", "")) != "in_transit":
		return false
	if bool(f.get("hostile", false)):
		return false
	var from_star := int(f.get("from_star", -1))
	var to_star := int(f.get("to_star", -1))
	if from_star < 0 or to_star < 0 or from_star == to_star:
		return false
	_flip_transit_direction(f)
	f["route"] = []
	fleets_changed.emit()
	return true


func clear_fleet_pursuit(fleet_id: String) -> void:
	if not fleets.has(fleet_id):
		return
	var f: Dictionary = fleets[fleet_id]
	f["pursue_fleet_id"] = ""


func set_fleet_pursuit(fleet_id: String, target_id: String) -> bool:
	## Order fleet_id to chase target_id (disk travel). Clears fixed dest + route.
	if fleet_id.is_empty() or target_id.is_empty() or fleet_id == target_id:
		return false
	if not fleets.has(fleet_id) or not fleets.has(target_id):
		return false
	var f: Dictionary = fleets[fleet_id]
	if bool(f.get("hostile", false)) or bool(f.get("stationary", false)):
		return false
	if bool(f.get("engaged", false)):
		return false
	if String(f.get("status", "")) != "in_system":
		return false
	var t: Dictionary = fleets[target_id]
	if String(t.get("status", "")) != "in_system":
		return false
	f["route"] = []
	f["pursue_fleet_id"] = target_id
	f["ordered"] = true
	f["orbiting"] = false
	var px := float(f.get("pos_x", 0.0))
	var pz := float(f.get("pos_z", 0.0))
	var tx := float(t.get("pos_x", 0.0))
	var tz := float(t.get("pos_z", 0.0))
	var dest := _pursue_standoff_dest(Vector3(px, 0.0, pz), Vector3(tx, 0.0, tz))
	f["dest_x"] = dest.x
	f["dest_z"] = dest.z
	fleets_changed.emit()
	return true


func _clear_pursuers_of(target_id: String) -> void:
	## Stop every fleet that was chasing target_id (hyperspace / despawn).
	if target_id.is_empty():
		return
	for fid in fleets.keys():
		var f: Dictionary = fleets[fid]
		if String(f.get("pursue_fleet_id", "")) != target_id:
			continue
		f["pursue_fleet_id"] = ""
		f["ordered"] = false
		f["orbiting"] = false


func fleets_in_system(star_id: int) -> Array:
	var out: Array = []
	for fid in fleets.keys():
		var f: Dictionary = fleets[fid]
		if String(f.get("status", "")) == "in_system" and int(f.get("system_id", -1)) == star_id:
			out.append(f)
	return out


func friendly_fleets_in_system(star_id: int) -> Array:
	## Non-hostile fleets parked in-system (excludes transit).
	var out: Array = []
	for f in fleets_in_system(star_id):
		if bool(f.get("hostile", false)):
			continue
		out.append(f)
	out.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		return String(a.get("id", "")) < String(b.get("id", ""))
	)
	return out


func fleets_in_transit() -> Array:
	var out: Array = []
	for fid in fleets.keys():
		var f: Dictionary = fleets[fid]
		if String(f.get("status", "")) == "in_transit":
			out.append(f)
	return out


func content_fleet_id(star_id: int, fleet_name: String) -> String:
	return "%d:%s" % [star_id, fleet_name]


func seed_content_fleets(star_id: int = -1) -> void:
	## Register authored fleets from system contents (idempotent).
	## star_id < 0 → every system that lists fleets.
	_ensure_map_data()
	if _system_data == null or not _system_data.loaded:
		return
	var ids: Array = []
	if star_id >= 0:
		ids.append(star_id)
	else:
		# Walk all systems; only those with a fleets array matter.
		var i := 0
		while true:
			var c := _system_data.get_system(i)
			if c.is_empty():
				break
			ids.append(i)
			i += 1
	var any := false
	for sid_v in ids:
		var sid := int(sid_v)
		if _seed_content_fleets_for_system(sid):
			any = true
	if any:
		fleets_changed.emit()


func _seed_content_fleets_for_system(star_id: int) -> bool:
	var content := _system_data.get_system(star_id)
	if content.is_empty():
		return false
	var fleets_doc = content.get("fleets", [])
	if typeof(fleets_doc) != TYPE_ARRAY or fleets_doc.is_empty():
		return false
	var mu := float(content.get("mu", 0.0))
	if mu <= 0.0 and content.has("stars"):
		var stars_doc = content.get("stars", [])
		if typeof(stars_doc) == TYPE_ARRAY and not stars_doc.is_empty():
			mu = float((stars_doc[0] as Dictionary).get("mu", 0.0))
	var added := false
	for fl in fleets_doc:
		var fd: Dictionary = fl
		var fname := String(fd.get("name", "Fleet"))
		var fid := content_fleet_id(star_id, fname)
		if has_fleet(fid):
			continue
		var hostile := bool(fd.get("hostile", false))
		var stationary := bool(fd.get("stationary", false))
		var a := float(fd.get("orbital_radius", 1.0))
		var phase0 := float(fd.get("phase0", 0.0))
		var inc := float(fd.get("inclination", 0.02))
		var host_i := int(fd.get("host_star", 0))
		var local_mu := mu
		if host_i >= 0 and content.has("stars"):
			var stars_doc2 = content.get("stars", [])
			if typeof(stars_doc2) == TYPE_ARRAY and host_i < stars_doc2.size():
				local_mu = float((stars_doc2[host_i] as Dictionary).get("mu", mu))
		var period := 0.0
		if local_mu > 0.0 and not stationary and a > 0.0:
			period = TAU * sqrt((a * a * a) / local_mu)
		var pos := Vector3.ZERO
		if stationary and fd.has("position"):
			var p = fd.get("position", [0.0, 0.0, 0.0])
			pos = Vector3(float(p[0]), 0.0, float(p[2]) if p.size() > 2 else 0.0)
		elif period > 0.0:
			var th := phase0 + TAU * (day / period)
			pos = Vector3(a * cos(th), 0.0, a * sin(th))
		else:
			pos = Vector3(a * cos(phase0), 0.0, a * sin(phase0))
		pos.y = 0.0
		var ship_names: Array = []
		for s in fd.get("ships", []):
			ship_names.append(String(s.get("name", "Ship")))
		# Avoid register_fleet's emit; batch at end of seed_content_fleets.
		fleets[fid] = {
			"id": fid,
			"name": fname,
			"ships": ship_names,
			"ship_templates": fd.get("ships", []),
			"faction": String(fd.get("faction", "")),
			"role": String(fd.get("role", "")),
			"hostile": hostile,
			"stationary": stationary,
			"orbiting": not hostile and not stationary,
			"engaged": false,
			"battle_id": "",
			"ordered": false,
			"pursue_fleet_id": "",
			"status": "in_system",
			"system_id": star_id,
			"pos_x": pos.x,
			"pos_z": pos.z,
			"a": a,
			"phase0": phase0,
			"inclination": inc,
			"period": period,
			"host_star": host_i,
			"needs_placement": false,
			"last_hyperlane_enter_day": HYPERLANE_ENTER_READY_DAY,
		}
		added = true
	return added


func transit_progress(fleet: Dictionary) -> float:
	## 0 at depart … 1 at arrive.
	var start := float(fleet.get("transit_start_day", day))
	var dur := maxf(float(fleet.get("transit_days", HYPERLANE_TRAVEL_DAYS)), 0.001)
	return clampf((day - start) / dur, 0.0, 1.0)


func is_fleet_hostile(fleet_id: String) -> bool:
	if not fleets.has(fleet_id):
		return false
	return bool(fleets[fleet_id].get("hostile", false))


func is_fleet_engaged(fleet_id: String) -> bool:
	if not fleets.has(fleet_id):
		return false
	return bool(fleets[fleet_id].get("engaged", false))


func fleet_battle_id(fleet_id: String) -> String:
	if not fleets.has(fleet_id):
		return ""
	return String(fleets[fleet_id].get("battle_id", ""))


func remove_fleet(fleet_id: String) -> void:
	if not fleets.has(fleet_id):
		return
	_clear_pursuers_of(fleet_id)
	fleets.erase(fleet_id)
	if selected_fleet_id == fleet_id:
		clear_fleet_selection()
	fleets_changed.emit()


func set_fleet_ships(fleet_id: String, ship_names: Array, ship_templates: Array) -> void:
	if not fleets.has(fleet_id):
		return
	var f: Dictionary = fleets[fleet_id]
	f["ships"] = ship_names
	f["ship_templates"] = ship_templates


func try_join_proximity_battles(system_id: int) -> void:
	## Non-engaged fleets within BATTLE_JOIN_AU of a battle's nearest participant join.
	## Distance = nearest engaged fleet already in that battle (not centroid).
	if battles.is_empty():
		return
	var candidates: Array = []
	for f in fleets_in_system(system_id):
		var fd: Dictionary = f
		if bool(fd.get("engaged", false)):
			continue
		candidates.append(fd)
	if candidates.is_empty():
		return
	var joined_any := false
	for cand in candidates:
		var cd: Dictionary = cand
		var cid := String(cd.get("id", ""))
		if cid.is_empty() or is_fleet_engaged(cid):
			continue
		var cpos := Vector3(float(cd.get("pos_x", 0.0)), 0.0, float(cd.get("pos_z", 0.0)))
		var best_bid := ""
		var best_d := 1e9
		for bid in battles.keys():
			var b: Dictionary = battles[bid]
			if int(b.get("system_id", -1)) != system_id:
				continue
			# Skip if already listed (shouldn't happen for non-engaged).
			if _battle_has_fleet(b, cid):
				continue
			var d := _nearest_battle_participant_dist(b, cpos)
			if d <= BATTLE_JOIN_AU and d < best_d:
				best_d = d
				best_bid = String(bid)
		if not best_bid.is_empty():
			if _join_battle(cid, best_bid):
				joined_any = true
	if joined_any:
		battles_changed.emit()
		fleets_changed.emit()


func try_start_proximity_battles(system_id: int) -> void:
	## Call from system view each sim tick while fleets share a system.
	## Prefer join-ongoing (caller) before starting new 1v1 contacts.
	var friendlies: Array = []
	var hostiles: Array = []
	for f in fleets_in_system(system_id):
		var fd: Dictionary = f
		if bool(fd.get("engaged", false)):
			continue
		if bool(fd.get("hostile", false)):
			hostiles.append(fd)
		else:
			friendlies.append(fd)
	for fr in friendlies:
		var fa: Dictionary = fr
		if bool(fa.get("engaged", false)):
			continue
		var fpos := Vector3(float(fa.get("pos_x", 0.0)), 0.0, float(fa.get("pos_z", 0.0)))
		for ho in hostiles:
			var hb: Dictionary = ho
			if bool(hb.get("engaged", false)):
				continue
			var hpos := Vector3(float(hb.get("pos_x", 0.0)), 0.0, float(hb.get("pos_z", 0.0)))
			if fpos.distance_to(hpos) <= BATTLE_CONTACT_AU:
				_start_battle(String(fa.get("id", "")), String(hb.get("id", "")), system_id)
				# Hostile can only start one new fight at a time.
				break


func _battle_has_fleet(b: Dictionary, fleet_id: String) -> bool:
	for fid in b.get("friendly_ids", []):
		if String(fid) == fleet_id:
			return true
	for hid in b.get("hostile_ids", []):
		if String(hid) == fleet_id:
			return true
	# Legacy single-id fields.
	return (
		String(b.get("friendly_id", "")) == fleet_id
		or String(b.get("hostile_id", "")) == fleet_id
	)


func _nearest_battle_participant_dist(b: Dictionary, pos: Vector3) -> float:
	var best := 1e9
	var ids: Array = []
	for fid in b.get("friendly_ids", []):
		ids.append(String(fid))
	for hid in b.get("hostile_ids", []):
		ids.append(String(hid))
	if ids.is_empty():
		var a := String(b.get("friendly_id", ""))
		var h := String(b.get("hostile_id", ""))
		if not a.is_empty():
			ids.append(a)
		if not h.is_empty():
			ids.append(h)
	for fid in ids:
		if not fleets.has(fid):
			continue
		var f: Dictionary = fleets[fid]
		if String(f.get("status", "")) != "in_system":
			continue
		var fp := Vector3(float(f.get("pos_x", 0.0)), 0.0, float(f.get("pos_z", 0.0)))
		best = minf(best, pos.distance_to(fp))
	return best


func _engage_fleet_in_battle(fleet_id: String, battle_id: String) -> void:
	if not fleets.has(fleet_id):
		return
	var f: Dictionary = fleets[fleet_id]
	f["engaged"] = true
	f["battle_id"] = battle_id
	f["ordered"] = false
	f["pursue_fleet_id"] = ""
	f["orbiting"] = false  # leave Kepler; survivors keep battle pose
	f["route"] = []


func _join_battle(fleet_id: String, battle_id: String) -> bool:
	if not fleets.has(fleet_id) or not battles.has(battle_id):
		return false
	if is_fleet_engaged(fleet_id):
		return false
	var b: Dictionary = battles[battle_id]
	if _battle_has_fleet(b, fleet_id):
		return false
	var f: Dictionary = fleets[fleet_id]
	var hostile := bool(f.get("hostile", false))
	var fname := String(f.get("name", "Fleet"))
	var faction := String(f.get("faction", ""))
	var ships: Array = f.get("ship_templates", [])
	if hostile:
		var hids: Array = b.get("hostile_ids", [])
		hids.append(fleet_id)
		b["hostile_ids"] = hids
		if String(b.get("hostile_id", "")).is_empty():
			b["hostile_id"] = fleet_id
		BattleRound.append_fleet_to_side(
			b.get("side_b", {}), fname, faction if not faction.is_empty() else "Choir", ships, fleet_id
		)
	else:
		var fids: Array = b.get("friendly_ids", [])
		fids.append(fleet_id)
		b["friendly_ids"] = fids
		if String(b.get("friendly_id", "")).is_empty():
			b["friendly_id"] = fleet_id
		BattleRound.append_fleet_to_side(
			b.get("side_a", {}), fname, faction, ships, fleet_id
		)
	_engage_fleet_in_battle(fleet_id, battle_id)
	return true


func _start_battle(friendly_id: String, hostile_id: String, system_id: int) -> void:
	if not fleets.has(friendly_id) or not fleets.has(hostile_id):
		return
	if is_fleet_engaged(friendly_id) or is_fleet_engaged(hostile_id):
		return
	var ff: Dictionary = fleets[friendly_id]
	var hf: Dictionary = fleets[hostile_id]
	var bid := "%s|%s" % [friendly_id, hostile_id]
	var side_a := BattleRound.side_from_ships(
		String(ff.get("name", "Friendly")),
		String(ff.get("faction", "")),
		ff.get("ship_templates", []),
		friendly_id,
	)
	var side_b := BattleRound.side_from_ships(
		String(hf.get("name", "Hostile")),
		String(hf.get("faction", "Choir")),
		hf.get("ship_templates", []),
		hostile_id,
	)
	battles[bid] = {
		"id": bid,
		"friendly_id": friendly_id,
		"hostile_id": hostile_id,
		"friendly_ids": [friendly_id],
		"hostile_ids": [hostile_id],
		"system_id": system_id,
		"next_round_day": day + HALF_HOUR_DAYS,
		"round": 0,
		"side_a": side_a,
		"side_b": side_b,
		"last_summary": {},
	}
	_engage_fleet_in_battle(friendly_id, bid)
	_engage_fleet_in_battle(hostile_id, bid)
	battles_changed.emit()
	fleets_changed.emit()


func _tick_battles() -> void:
	if battles.is_empty():
		return
	var finished: Array = []
	var advanced := false
	var rng := RandomNumberGenerator.new()
	for bid in battles.keys():
		var b: Dictionary = battles[bid]
		if day + 1e-9 < float(b.get("next_round_day", day)):
			continue
		advanced = true
		rng.seed = hash("%s:%d:%.6f" % [bid, int(b.get("round", 0)), day])
		var side_a: Dictionary = b.get("side_a", {})
		var side_b: Dictionary = b.get("side_b", {})
		var summary := BattleRound.resolve_round(rng, side_a, side_b)
		b["side_a"] = side_a
		b["side_b"] = side_b
		b["round"] = int(b.get("round", 0)) + 1
		b["next_round_day"] = day + HALF_HOUR_DAYS
		b["last_summary"] = summary
		_sync_battle_ships(b)
		var outcome := String(summary.get("outcome", "ongoing"))
		if outcome != "ongoing":
			finished.append(bid)
	for bid2 in finished:
		_finish_battle(String(bid2))
	if advanced:
		battles_changed.emit()
		fleets_changed.emit()


func _battle_side_ids(b: Dictionary, friendly: bool) -> Array:
	var key := "friendly_ids" if friendly else "hostile_ids"
	var ids: Array = []
	for x in b.get(key, []):
		ids.append(String(x))
	if ids.is_empty():
		var single := String(b.get("friendly_id" if friendly else "hostile_id", ""))
		if not single.is_empty():
			ids.append(single)
	return ids


func _sync_battle_ships(b: Dictionary) -> void:
	var side_a: Dictionary = b.get("side_a", {})
	var side_b: Dictionary = b.get("side_b", {})
	for fid in _battle_side_ids(b, true):
		var ships_a := BattleRound.ships_from_side_for_fleet(side_a, fid)
		var names_a: Array = []
		for s in ships_a:
			names_a.append(String(s.get("name", "Ship")))
		set_fleet_ships(fid, names_a, ships_a)
	for hid in _battle_side_ids(b, false):
		var ships_b := BattleRound.ships_from_side_for_fleet(side_b, hid)
		var names_b: Array = []
		for s in ships_b:
			names_b.append(String(s.get("name", "Ship")))
		set_fleet_ships(hid, names_b, ships_b)


func _finish_battle(battle_id: String) -> void:
	if not battles.has(battle_id):
		return
	var b: Dictionary = battles[battle_id]
	var summary: Dictionary = b.get("last_summary", {})
	var outcome := String(summary.get("outcome", "ongoing"))
	var wipe_friendly := outcome in ["b_wins", "mutual_wipe"]
	var wipe_hostile := outcome in ["a_wins", "mutual_wipe"]
	var friendly_ids := _battle_side_ids(b, true)
	var hostile_ids := _battle_side_ids(b, false)
	for fid in friendly_ids:
		if fleets.has(fid):
			fleets[fid]["engaged"] = false
			fleets[fid]["battle_id"] = ""
	for hid in hostile_ids:
		if fleets.has(hid):
			fleets[hid]["engaged"] = false
			fleets[hid]["battle_id"] = ""
	battles.erase(battle_id)
	# Side wipe removes all fleets on that side; also drop any fleet with 0 hulls.
	for fid2 in friendly_ids:
		if not fleets.has(fid2):
			continue
		var fa: Dictionary = fleets[fid2]
		var n_a: Array = fa.get("ships", [])
		if wipe_friendly or n_a.is_empty():
			_clear_pursuers_of(fid2)
			fleets.erase(fid2)
	for hid2 in hostile_ids:
		if not fleets.has(hid2):
			continue
		var hb: Dictionary = fleets[hid2]
		var n_b: Array = hb.get("ships", [])
		if wipe_hostile or n_b.is_empty():
			_clear_pursuers_of(hid2)
			fleets.erase(hid2)
	if not selected_fleet_id.is_empty() and not fleets.has(selected_fleet_id):
		clear_fleet_selection()
	fleets_changed.emit()
	battles_changed.emit()


func _fleet_names_joined(ids: Array, fallback: String) -> String:
	var parts: PackedStringArray = PackedStringArray()
	for fid in ids:
		if fleets.has(fid):
			parts.append(String(fleets[fid].get("name", fid)))
		else:
			parts.append(String(fid))
	if parts.is_empty():
		return fallback
	return ", ".join(parts)


func battle_hud_line(system_id: int = -1) -> String:
	## Short status for system HUD.
	var lines: PackedStringArray = PackedStringArray()
	for bid in battles.keys():
		var b: Dictionary = battles[bid]
		if system_id >= 0 and int(b.get("system_id", -1)) != system_id:
			continue
		var fa := _fleet_names_joined(_battle_side_ids(b, true), "Friendly")
		var hb := _fleet_names_joined(_battle_side_ids(b, false), "Hostile")
		var rnd := int(b.get("round", 0))
		var sum: Dictionary = b.get("last_summary", {})
		if sum.is_empty():
			lines.append("Battle: %s vs %s (contact — round pending)" % [fa, hb])
		else:
			lines.append(
				"Battle R%d: %s (%d) vs %s (%d)" % [
					rnd, fa, int(sum.get("a_ships", 0)), hb, int(sum.get("b_ships", 0))
				]
			)
	return "\n".join(lines)


func _tick_fleet_arrivals() -> void:
	var changed := false
	for fid in fleets.keys():
		var f: Dictionary = fleets[fid]
		if String(f.get("status", "")) != "in_transit":
			continue
		if transit_progress(f) < 1.0:
			continue
		var dest := int(f.get("to_star", -1))
		var origin := int(f.get("from_star", -1))
		f["status"] = "in_system"
		f["system_id"] = dest
		f["arrived_from"] = origin
		f["needs_placement"] = true
		f["orbiting"] = false  # free-disk placement at portal; no Kepler resume
		f["from_star"] = -1
		f["to_star"] = -1
		# Place immediately so off-screen multi-hop cruise can continue.
		_resolve_fleet_placement(f)
		# Keep GameState.selected_fleet_id — selection persists across transit.
		_apply_route_after_arrival(f, dest)
		changed = true
	if changed:
		fleets_changed.emit()


func _apply_route_after_arrival(f: Dictionary, dest_star: int) -> void:
	## Continue multi-hop: next waypoint should be system_cruise in dest_star.
	var route = f.get("route", [])
	if typeof(route) != TYPE_ARRAY or route.is_empty():
		f["ordered"] = false
		return
	var hop: Dictionary = route[0]
	if String(hop.get("kind", "")) != "system_cruise":
		return
	if int(hop.get("system", -1)) != dest_star:
		# Desync — drop remaining route.
		f["route"] = []
		f["ordered"] = false
		return
	f["ordered"] = true
	f["orbiting"] = false
	f["dest_x"] = float(hop.get("to_x", 0.0))
	f["dest_z"] = float(hop.get("to_z", 0.0))
	# Pose already resolved via _resolve_fleet_placement on arrival.