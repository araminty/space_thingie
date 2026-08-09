extends RefCounted
class_name BattleRound
## Runtime combat aligned with battle_sim.py (v3 mounts, per-ship morale,
## doctrine soft-outs, 1D axis, escape/disengage). Simplified vs full Python sim.

const BANDS := ["Point", "Close", "Medium", "Long", "Extreme"]

## weapon_id -> {kind, size, track, acc, pen, dmg_avg, spray, dist_track, dist_acc, anchor, pref}
const WEAPONS := {
	"P5C": {"kind": "plasma", "size": 5, "track": 8, "acc": 6, "pen": 10, "dmg": 10.5, "spray": 0, "dt": 1, "da": 1, "anchor": 1, "pref": 3},
	"P5B": {"kind": "plasma", "size": 5, "track": 7, "acc": 6, "pen": 10, "dmg": 8.0, "spray": 0, "dt": 1, "da": 1, "anchor": 1, "pref": 3},
	"P5A": {"kind": "plasma", "size": 5, "track": 7, "acc": 5, "pen": 9, "dmg": 8.0, "spray": 0, "dt": 1, "da": 1, "anchor": 1, "pref": 3},
	"P4C": {"kind": "plasma", "size": 4, "track": 7, "acc": 6, "pen": 9, "dmg": 7.0, "spray": 0, "dt": 1, "da": 1, "anchor": 1, "pref": 3},
	"P4B": {"kind": "plasma", "size": 4, "track": 7, "acc": 5, "pen": 9, "dmg": 7.0, "spray": 0, "dt": 1, "da": 1, "anchor": 1, "pref": 3},
	"P4A": {"kind": "plasma", "size": 4, "track": 6, "acc": 5, "pen": 8, "dmg": 7.0, "spray": 0, "dt": 1, "da": 1, "anchor": 1, "pref": 3},
	"P3C": {"kind": "plasma", "size": 3, "track": 7, "acc": 6, "pen": 8, "dmg": 7.0, "spray": 0, "dt": 1, "da": 1, "anchor": 1, "pref": 3},
	"P3B": {"kind": "plasma", "size": 3, "track": 6, "acc": 6, "pen": 8, "dmg": 7.0, "spray": 0, "dt": 1, "da": 1, "anchor": 1, "pref": 3},
	"P3A": {"kind": "plasma", "size": 3, "track": 6, "acc": 5, "pen": 7, "dmg": 7.0, "spray": 0, "dt": 1, "da": 1, "anchor": 1, "pref": 3},
	"P2B": {"kind": "plasma", "size": 2, "track": 6, "acc": 5, "pen": 6, "dmg": 7.0, "spray": 0, "dt": 2, "da": 1, "anchor": 1, "pref": 3},
	"P2A": {"kind": "plasma", "size": 2, "track": 5, "acc": 5, "pen": 6, "dmg": 4.5, "spray": 0, "dt": 2, "da": 1, "anchor": 1, "pref": 3},
	"P1A": {"kind": "plasma", "size": 1, "track": 5, "acc": 4, "pen": 5, "dmg": 4.5, "spray": 0, "dt": 2, "da": 2, "anchor": 1, "pref": 3},
	"C2C": {"kind": "cannon", "size": 2, "track": 6, "acc": 5, "pen": 10, "dmg": 8.0, "spray": 7, "dt": 2, "da": 2, "anchor": 1, "pref": 1},
	"C2B": {"kind": "cannon", "size": 2, "track": 5, "acc": 5, "pen": 10, "dmg": 7.0, "spray": 6, "dt": 2, "da": 2, "anchor": 1, "pref": 1},
	"C2A": {"kind": "cannon", "size": 2, "track": 5, "acc": 4, "pen": 9, "dmg": 7.0, "spray": 6, "dt": 2, "da": 2, "anchor": 1, "pref": 1},
	"C1C": {"kind": "cannon", "size": 1, "track": 6, "acc": 5, "pen": 5, "dmg": 3.5, "spray": 7, "dt": 2, "da": 2, "anchor": 1, "pref": 1},
	"C1B": {"kind": "cannon", "size": 1, "track": 5, "acc": 5, "pen": 4, "dmg": 3.5, "spray": 6, "dt": 2, "da": 2, "anchor": 1, "pref": 1},
	"C1A": {"kind": "cannon", "size": 1, "track": 5, "acc": 4, "pen": 4, "dmg": 3.5, "spray": 6, "dt": 2, "da": 2, "anchor": 1, "pref": 1},
}

## class -> sheet with mounts: Array of [weapon_id, count]
const CLASSES := {
	"Ward-keel": {"prot": 8, "mob": 3, "reac": 4, "skirm": 2, "size": "H", "hull": "warship", "redun": "mid", "fog": "line", "mounts": [["P4A", 2], ["C2A", 1], ["C1A", 4]]},
	"Lockbar": {"prot": 9, "mob": 1, "reac": 3, "skirm": 1, "size": "H", "hull": "monitor", "redun": "high", "fog": "line", "mounts": [["P5A", 1], ["C2A", 1], ["C1A", 2]]},
	"Ledger": {"prot": 5, "mob": 5, "reac": 5, "skirm": 3, "size": "M", "hull": "warship", "redun": "mid", "fog": "line", "mounts": [["P3A", 1], ["C2A", 1], ["C1A", 3]]},
	"Quill": {"prot": 2, "mob": 6, "reac": 8, "skirm": 7, "size": "S", "hull": "picket", "redun": "low", "fog": "picket", "mounts": [["C1A", 2], ["C2A", 1]]},
	"Cutter-fly": {"prot": 1, "mob": 8, "reac": 9, "skirm": 8, "size": "S", "hull": "flight", "redun": "low", "fog": "none", "mounts": [["C1A", 1]]},
	"Grain-gun": {"prot": 4, "mob": 2, "reac": 3, "skirm": 1, "size": "L", "hull": "scow", "redun": "high", "fog": "convoy", "mounts": [["P1A", 1], ["C2A", 1], ["C1A", 4]]},
	"Packet": {"prot": 3, "mob": 3, "reac": 4, "skirm": 2, "size": "M", "hull": "scow", "redun": "high", "fog": "convoy", "mounts": [["C2A", 1], ["C1A", 3]]},
	"Pennant": {"prot": 7, "mob": 4, "reac": 5, "skirm": 3, "size": "H", "hull": "warship", "redun": "mid", "fog": "line", "mounts": [["P4B", 2], ["C2B", 1], ["C1B", 3]]},
	"Anvil": {"prot": 9, "mob": 1, "reac": 2, "skirm": 1, "size": "H", "hull": "monitor", "redun": "high", "fog": "line", "mounts": [["P5B", 1], ["C2A", 1], ["C1A", 2]]},
	"Lancer": {"prot": 4, "mob": 6, "reac": 5, "skirm": 3, "size": "M", "hull": "warship", "redun": "low", "fog": "line", "mounts": [["P3B", 1], ["C2A", 1], ["C1B", 2]]},
	"Whip": {"prot": 2, "mob": 8, "reac": 6, "skirm": 4, "size": "S", "hull": "chase", "redun": "low", "fog": "none", "mounts": [["P1A", 1], ["C1B", 2]]},
	"Outrider": {"prot": 2, "mob": 7, "reac": 8, "skirm": 8, "size": "S", "hull": "picket", "redun": "low", "fog": "picket", "mounts": [["C1B", 2], ["C2A", 1]]},
	"Lance-fly": {"prot": 1, "mob": 8, "reac": 9, "skirm": 8, "size": "S", "hull": "flight", "redun": "low", "fog": "none", "mounts": [["C1A", 1]]},
	"Border": {"prot": 4, "mob": 2, "reac": 3, "skirm": 1, "size": "L", "hull": "scow", "redun": "high", "fog": "convoy", "mounts": [["P1A", 1], ["C2A", 2], ["C1A", 2]]},
	"Nidus": {"prot": 5, "mob": 2, "reac": 6, "skirm": 5, "size": "H+", "hull": "scow", "redun": "high", "fog": "convoy", "mounts": [["P2A", 1], ["C2A", 1], ["C1A", 4]]},
	"Chorus-hull": {"prot": 6, "mob": 1, "reac": 7, "skirm": 6, "size": "H+", "hull": "scow", "redun": "high", "fog": "convoy", "mounts": [["P2A", 1], ["C2A", 2], ["C1A", 5]]},
	"Thread": {"prot": 2, "mob": 7, "reac": 9, "skirm": 8, "size": "S", "hull": "picket", "redun": "low", "fog": "picket", "mounts": [["C1A", 2], ["C2A", 1]]},
	"Sting-fly": {"prot": 1, "mob": 9, "reac": 9, "skirm": 9, "size": "S", "hull": "flight", "redun": "low", "fog": "none", "mounts": [["C1A", 1]]},
	"Bleed-fly": {"prot": 1, "mob": 8, "reac": 8, "skirm": 8, "size": "S", "hull": "flight", "redun": "low", "fog": "none", "mounts": [["C1A", 1], ["C2A", 1]]},
}

const SIZE_SCALE := {"H+": 2.4, "H": 2.0, "L": 1.5, "M": 1.35, "S": 0.65}
const LANE_DIFF := {
	"H": [2, 3, 4, 5, 6],
	"H+": [2, 3, 4, 5, 6],
	"M": [3, 4, 5, 7, 8],
	"L": [3, 4, 6, 8, 9],
	"S": [5, 7, 9, 11, 12],
}
const FLEE_DYNAMICS := {
	"Escape": true,
	"Flee towards reinforcements": true,
	"Flee towards defenses": true,
}
const PRESS_DYNAMICS := {
	"Pursue": true, "Raid": true, "Hunt birds": true, "Overwhelm": true,
	"Finish before relief": true, "Intercept the join": true,
	"Deny the fort": true, "Deny escape": true,
}
const RELUCTANT := {
	"Slug": true, "Escort": true, "Hold ground": true, "Hold for relief": true,
	"Raid": true, "Overwhelm": true,
}


static func side_from_ships(
	name: String,
	faction: String,
	ships: Array,
	fleet_id: String = "",
	doctrine: String = "",
	axis_sign: int = -1,
) -> Dictionary:
	## Group by class; prefer exported per-ship mounts/stats when present.
	var by_class: Dictionary = {}
	var sheet_by_class: Dictionary = {}
	for s in ships:
		var sd: Dictionary = s
		var cls := String(sd.get("class", sd.get("name", "Unknown")))
		if cls.contains("-") and not CLASSES.has(cls):
			var base := cls.rsplit("-", true, 1)[0]
			if CLASSES.has(base):
				cls = base
		if not by_class.has(cls):
			by_class[cls] = 0
			var base_sheet: Dictionary = CLASSES.get(cls, {
				"prot": 3, "mob": 3, "reac": 3, "skirm": 2,
				"size": "M", "hull": "warship", "redun": "mid", "fog": "none",
				"mounts": [["C1A", 1]],
			}).duplicate(true)
			if sd.has("mounts"):
				base_sheet["mounts"] = sd.get("mounts", base_sheet.get("mounts", []))
			for key in ["prot", "mob", "reac", "skirm", "size", "hull", "redun", "fog"]:
				if sd.has(key):
					base_sheet[key] = sd.get(key)
			sheet_by_class[cls] = base_sheet
		by_class[cls] = int(by_class[cls]) + 1
	var doc := doctrine
	if doc.is_empty():
		doc = _default_doctrine(faction)
	var units: Array = []
	for cls in by_class.keys():
		var sheet: Dictionary = sheet_by_class.get(cls, {}).duplicate(true)
		var count := int(by_class[cls])
		var depth := _deploy_depth(sheet)
		var x := -depth if axis_sign < 0 else depth
		units.append({
			"class": cls,
			"count": count,
			"hp": float(int(sheet.get("prot", 3)) * count),
			"sheet": sheet,
			"mob": int(sheet.get("mob", 3)),
			"reac": int(sheet.get("reac", 3)),
			"skirm": int(sheet.get("skirm", 2)),
			"morale": 90.0,
			"x": x,
			"station": "front",
			"bird": false,
			"struck": false,
			"gone": false,
			"reinforcement": false,
			"fleet_id": fleet_id,
		})
	return {
		"name": name,
		"faction": faction,
		"doctrine": doc,
		"axis_sign": axis_sign,
		"fog": false,
		"fog_stock": 2,
		"initial_ships": _ship_count_units(units),
		"units": units,
		"log": [],
		# Aggregate for HUD compatibility
		"morale": 90.0,
	}


static func append_fleet_to_side(
	side: Dictionary, name: String, faction: String, ships: Array, fleet_id: String
) -> void:
	var sign := int(side.get("axis_sign", -1))
	var doc := String(side.get("doctrine", ""))
	var added := side_from_ships(name, faction, ships, fleet_id, doc, sign)
	var units: Array = side.get("units", [])
	for u in added.get("units", []):
		var ud: Dictionary = u
		var cls := String(ud.get("class", ""))
		var merged := false
		for i in units.size():
			var ex: Dictionary = units[i]
			if (
				String(ex.get("fleet_id", "")) == fleet_id
				and String(ex.get("class", "")) == cls
				and not bool(ex.get("gone", false))
				and not bool(ex.get("struck", false))
			):
				var add_n := int(ud.get("count", 0))
				ex["count"] = int(ex.get("count", 0)) + add_n
				ex["hp"] = float(ex.get("hp", 0.0)) + float(ud.get("hp", 0.0))
				units[i] = ex
				merged = true
				break
		if not merged:
			units.append(ud)
	side["units"] = units
	side["initial_ships"] = int(side.get("initial_ships", 0)) + int(added.get("initial_ships", 0))
	var nm := String(side.get("name", ""))
	if not name.is_empty() and not nm.contains(name):
		side["name"] = "%s + %s" % [nm, name] if not nm.is_empty() else name
	if String(side.get("faction", "")).is_empty() and not faction.is_empty():
		side["faction"] = faction


static func ships_from_side(side: Dictionary) -> Array:
	return _ships_from_units(side.get("units", []), "")


static func ships_from_side_for_fleet(side: Dictionary, fleet_id: String) -> Array:
	return _ships_from_units(side.get("units", []), fleet_id)


static func _ships_from_units(units: Array, fleet_id_filter: String) -> Array:
	var ships: Array = []
	for u in units:
		var ud: Dictionary = u
		if bool(ud.get("gone", false)) or bool(ud.get("struck", false)):
			continue
		if int(ud.get("count", 0)) <= 0 or float(ud.get("hp", 0.0)) <= 0.0:
			continue
		if not fleet_id_filter.is_empty() and String(ud.get("fleet_id", "")) != fleet_id_filter:
			continue
		var cls := String(ud.get("class", "Ship"))
		var sheet: Dictionary = ud.get("sheet", {})
		var size := String(sheet.get("size", "M"))
		var hull := String(sheet.get("hull", "warship"))
		var scale := float(SIZE_SCALE.get(size, 1.0))
		var mounts: Array = sheet.get("mounts", [])
		var n := int(ud.get("count", 0))
		for k in n:
			ships.append({
				"name": "%s-%d" % [cls, k + 1],
				"class": cls,
				"hull": hull,
				"size": size,
				"size_scale": scale,
				"template": "basic_spaceship",
				"offset": [0.0, 0.0, 0.0],
				"fleet_id": String(ud.get("fleet_id", "")),
				"mounts": mounts,
			})
	_layout_offsets(ships)
	return ships


static func living_count(side: Dictionary) -> int:
	var n := 0
	for u in _alive_units(side):
		n += int(u.get("count", 0))
	return n


static func avg_morale(side: Dictionary) -> float:
	var living := _alive_units(side)
	if living.is_empty():
		return 0.0
	var s := 0.0
	for u in living:
		s += float(u.get("morale", 90.0))
	return s / float(living.size())


static func resolve_round(rng: RandomNumberGenerator, a: Dictionary, b: Dictionary) -> Dictionary:
	a["log"] = []
	b["log"] = []
	if int(a.get("initial_ships", 0)) <= 0:
		a["initial_ships"] = living_count(a)
	if int(b.get("initial_ships", 0)) <= 0:
		b["initial_ships"] = living_count(b)

	var da_pack := _choose_dynamic(a, b)
	var db_pack := _choose_dynamic(b, a)
	var da: String = da_pack[0]
	var db: String = db_pack[0]
	# Raid press vs directed flee / abort vs generic Escape
	var react_a := _react_to_flee(a, da, db)
	var react_b := _react_to_flee(b, db, da)
	da = react_a
	db = react_b
	_set_stations(a, da)
	_set_stations(b, db)
	_note(a, "Dynamic: %s" % da)
	_note(b, "Dynamic: %s" % db)

	# Escape checks before combat
	var esc := _try_side_escape(rng, a, b, da, db)
	if esc != "":
		a["morale"] = avg_morale(a)
		b["morale"] = avg_morale(b)
		return _summary(esc, a, b)

	_apply_thrust(a, da)
	_apply_thrust(b, db)
	_fire_all(rng, a, b)
	_fire_all(rng, b, a)
	_morale_tick(a)
	_morale_tick(b)
	a["morale"] = avg_morale(a)
	b["morale"] = avg_morale(b)

	var ca := living_count(a)
	var cb := living_count(b)
	var outcome := "ongoing"
	if ca <= 0 and cb <= 0:
		outcome = "mutual_wipe"
	elif ca <= 0:
		outcome = "b_wins"
	elif cb <= 0:
		outcome = "a_wins"
	elif _all_shattered(a):
		outcome = "a_escapes" if _avg_dash(a) >= 3.0 else "b_wins"
	elif _all_shattered(b):
		outcome = "b_escapes" if _avg_dash(b) >= 3.0 else "a_wins"
	return _summary(outcome, a, b)


static func _summary(outcome: String, a: Dictionary, b: Dictionary) -> Dictionary:
	return {
		"outcome": outcome,
		"a_ships": living_count(a),
		"b_ships": living_count(b),
		"a_morale": float(a.get("morale", 0.0)),
		"b_morale": float(b.get("morale", 0.0)),
		"log_a": a.get("log", []),
		"log_b": b.get("log", []),
		"disengage": outcome in ["a_escapes", "b_escapes", "mutual_break"],
	}


static func _default_doctrine(faction: String) -> String:
	match faction:
		"Choir":
			return "choir"
		"March":
			return "raid"
		_:
			return "escort"


static func _deploy_depth(sheet: Dictionary) -> float:
	var hull := String(sheet.get("hull", ""))
	match hull:
		"monitor":
			return 3.0
		"warship":
			return 3.5
		"chase":
			return 4.0
		"picket":
			return 4.5
		"flight":
			return 4.0
		"scow":
			return 5.5
		_:
			return 4.5


static func _note(side: Dictionary, msg: String) -> void:
	var log_lines: Array = side.get("log", [])
	log_lines.append(msg)
	side["log"] = log_lines


static func _alive_units(side: Dictionary) -> Array:
	var out: Array = []
	for u in side.get("units", []):
		var ud: Dictionary = u
		if bool(ud.get("gone", false)) or bool(ud.get("struck", false)):
			continue
		if int(ud.get("count", 0)) > 0 and float(ud.get("hp", 0.0)) > 0.0:
			out.append(ud)
	return out


static func _ship_count_units(units: Array) -> int:
	var n := 0
	for u in units:
		n += int(u.get("count", 0))
	return n


static func _band_code(m: float) -> String:
	if m >= 80.0:
		return "M5"
	if m >= 60.0:
		return "M4"
	if m >= 40.0:
		return "M3"
	if m >= 20.0:
		return "M2"
	if m >= 1.0:
		return "M1"
	return "M0"


static func _band_rank(code: String) -> int:
	match code:
		"M5":
			return 5
		"M4":
			return 4
		"M3":
			return 3
		"M2":
			return 2
		"M1":
			return 1
		_:
			return 0


static func _band_meets(morale: float, min_code: String) -> bool:
	return _band_rank(_band_code(morale)) >= _band_rank(min_code)


static func _all_shattered(side: Dictionary) -> bool:
	var nb: Array = []
	for u in _alive_units(side):
		if not bool(u.get("bird", false)):
			nb.append(u)
	if nb.is_empty():
		return true
	for u in nb:
		if _band_rank(_band_code(float(u.get("morale", 90.0)))) >= 2:
			return false
	return true


static func _avg_dash(side: Dictionary) -> float:
	var living := _alive_units(side)
	if living.is_empty():
		return 0.0
	var s := 0.0
	var n := 0
	for u in living:
		var c := int(u.get("count", 1))
		s += float(u.get("mob", 3)) * float(c)
		n += c
	return s / float(maxi(n, 1))


static func _force_weight(side: Dictionary) -> float:
	var t := 0.0
	for u in _alive_units(side):
		var sheet: Dictionary = u.get("sheet", {})
		var punch := _best_plasma_pen(sheet)
		var stand := int(sheet.get("prot", 3))
		var mob := float(u.get("mob", 3))
		t += (float(punch) + float(stand) + 0.4 * mob) * float(int(u.get("count", 1)))
	return t


static func _best_plasma_pen(sheet: Dictionary) -> int:
	var best := 0
	for m in sheet.get("mounts", []):
		if typeof(m) != TYPE_ARRAY or m.size() < 1:
			continue
		var wid := String(m[0])
		if not WEAPONS.has(wid):
			continue
		var w: Dictionary = WEAPONS[wid]
		if String(w.get("kind", "")) == "plasma":
			best = maxi(best, int(w.get("pen", 0)))
	return best


static func _loss_fraction(side: Dictionary) -> float:
	var init := int(side.get("initial_ships", 0))
	if init <= 0:
		return 0.0
	return maxf(0.0, 1.0 - float(living_count(side)) / float(init))


static func _has_hull(side: Dictionary, hull: String) -> bool:
	for u in _alive_units(side):
		var sheet: Dictionary = u.get("sheet", {})
		if String(sheet.get("hull", "")) == hull:
			return true
	return false


static func _scow_count(side: Dictionary) -> int:
	var n := 0
	for u in _alive_units(side):
		var sheet: Dictionary = u.get("sheet", {})
		if String(sheet.get("hull", "")) == "scow":
			n += int(u.get("count", 0))
	return n


static func _soft_raid_target(foe: Dictionary) -> bool:
	if _has_hull(foe, "monitor"):
		# Only local (non-reinforcement) monitors harden
		for u in _alive_units(foe):
			var sheet: Dictionary = u.get("sheet", {})
			if String(sheet.get("hull", "")) == "monitor" and not bool(u.get("reinforcement", false)):
				return false
	var total := living_count(foe)
	if total <= 0:
		return false
	var scow := _scow_count(foe)
	var steel := 0
	for u in _alive_units(foe):
		var sheet: Dictionary = u.get("sheet", {})
		var hull := String(sheet.get("hull", ""))
		if hull == "warship" or (hull == "monitor" and not bool(u.get("reinforcement", false))):
			steel += int(u.get("count", 0))
	return float(scow) >= 0.45 * float(total) and steel <= 2


static func _choose_dynamic(side: Dictionary, foe: Dictionary) -> Array:
	## Returns [dynamic, reason]
	if _all_shattered(side):
		if _avg_dash(side) >= 3.0:
			return ["Escape", "morale_force_shattered"]
		return ["Withdraw", "morale_force_shattered"]
	var doc := String(side.get("doctrine", "escort"))
	var m4_ok := false
	for u in _alive_units(side):
		if not bool(u.get("bird", false)) and _band_meets(float(u.get("morale", 90.0)), "M4"):
			m4_ok = true
			break

	if doc in ["flee_reinforcements", "flee_defenses"]:
		return [
			"Flee towards reinforcements" if doc == "flee_reinforcements" else "Flee towards defenses",
			"doctrine_flee",
		]
	if doc == "hold_relief":
		if _loss_fraction(side) >= 0.3 or _force_weight(side) < 0.55 * _force_weight(foe):
			return ["Flee towards reinforcements", "hold_break"]
		return ["Hold for relief", "doctrine_hold"]
	if doc == "finish_before_relief":
		if _loss_fraction(side) >= 0.2 or _force_weight(side) < 0.75 * _force_weight(foe):
			return ["Escape", "raid_abort"]
		return ["Finish before relief" if m4_ok else "Raid", "doctrine_finish"]
	if doc == "battleline":
		if _loss_fraction(side) >= 0.45 or avg_morale(side) < 40.0:
			return ["Escape", "line_break"]
		return ["Slug", "doctrine_battleline"]
	if doc == "hold_choke":
		if _loss_fraction(side) >= 0.35:
			return ["Escape", "choke_break"]
		return ["Hold ground" if _has_hull(side, "monitor") else "Escort", "doctrine_choke"]
	if doc == "garrison":
		if _loss_fraction(side) >= 0.2 or _force_weight(side) < 0.8 * _force_weight(foe):
			return ["Escape", "garrison_break"]
		return ["Escort", "doctrine_garrison"]
	if doc == "choir":
		if not _has_hull(side, "scow") or _loss_fraction(side) >= 0.45 or avg_morale(side) < 35.0:
			return ["Escape", "choir_break"]
		return ["Overwhelm", "doctrine_choir"]
	if doc == "consigned":
		return ["Overwhelm", "doctrine_consigned"]
	if doc == "raid":
		if _has_hull(foe, "monitor") and not _soft_raid_target(foe):
			return ["Escape", "raid_abort_monitor"]
		if _loss_fraction(side) >= 0.25 or avg_morale(side) < 55.0:
			return ["Escape", "raid_abort_losses"]
		if not _soft_raid_target(foe) and _has_hull(foe, "warship") and _force_weight(side) < _force_weight(foe):
			return ["Escape", "raid_abort_hard"]
		return ["Raid", "doctrine_raid"]
	# escort / convoy default — run unless very tempting
	if _tempting_for_convoy(side, foe):
		if _scow_count(side) >= 8 and m4_ok and _force_weight(side) > 1.5 * _force_weight(foe):
			return ["Overwhelm", "convoy_tempting"]
		return ["Escort", "convoy_tempting_hold"]
	return ["Escape", "convoy_run_default"]


static func _tempting_for_convoy(side: Dictionary, foe: Dictionary) -> bool:
	var living := _alive_units(foe)
	if living.is_empty():
		return false
	var birds := 0
	var total := 0
	for u in living:
		var c := int(u.get("count", 0))
		total += c
		if bool(u.get("bird", false)):
			birds += c
	if total > 0 and float(birds) / float(total) >= 0.45 and _has_hull(side, "chase"):
		return true
	if avg_morale(foe) < 40.0 and _force_weight(side) >= 2.0 * maxf(1.0, _force_weight(foe)):
		return true
	return false


static func _react_to_flee(side: Dictionary, dyn: String, foe_dyn: String) -> String:
	var doc := String(side.get("doctrine", ""))
	if doc not in ["raid", "finish_before_relief", "intercept_join", "deny_fort"]:
		return dyn
	if not FLEE_DYNAMICS.has(foe_dyn):
		return dyn
	if foe_dyn == "Flee towards defenses":
		return "Deny the fort"
	if foe_dyn == "Flee towards reinforcements":
		return "Intercept the join"
	if PRESS_DYNAMICS.has(dyn):
		return "Escape"
	return dyn


static func _set_stations(side: Dictionary, dynamic: String) -> void:
	var min_b := "M3"
	if FLEE_DYNAMICS.has(dynamic):
		min_b = "M1"
	elif dynamic in ["Escort", "Hold ground", "Hold for relief"]:
		min_b = "M2"
	elif dynamic in ["Pursue", "Deny escape", "Hunt birds", "Overwhelm", "Deny the fort", "Intercept the join"]:
		min_b = "M4"
	for u in side.get("units", []):
		var ud: Dictionary = u
		if bool(ud.get("struck", false)) or bool(ud.get("gone", false)):
			ud["station"] = "fallback"
			continue
		if bool(ud.get("reinforcement", false)) and _band_meets(float(ud.get("morale", 90.0)), "M2"):
			ud["station"] = "front"
			continue
		if _band_meets(float(ud.get("morale", 90.0)), min_b):
			ud["station"] = "front"
		else:
			ud["station"] = "fallback"


static func _apply_thrust(side: Dictionary, dynamic: String) -> void:
	var flee := FLEE_DYNAMICS.has(dynamic)
	var bonus := 1 if flee or dynamic in ["Pursue", "Deny escape", "Deny the fort"] else 0
	var sign := int(side.get("axis_sign", -1))
	for u in _alive_units(side):
		var step_bonus := 0 if bool(u.get("reinforcement", false)) else bonus
		var step := maxi(1, int(floor(float(u.get("mob", 3)) / 3.0))) + step_bonus
		if bool(u.get("bird", false)):
			step = maxi(1, int(floor(float(step) / 2.0)))
		var x := float(u.get("x", 0.0))
		if bool(u.get("reinforcement", false)):
			# Close on contact
			if x > 0.0:
				x = maxf(0.0, x - float(step))
			elif x < 0.0:
				x = minf(0.0, x + float(step))
		elif flee or String(u.get("station", "")) == "fallback":
			x += float(sign) * float(step)
		else:
			if x > 0.0:
				x = maxf(0.0, x - float(step))
			elif x < 0.0:
				x = minf(0.0, x + float(step))
		u["x"] = x


static func _abs_dx_to_band(dx: float) -> int:
	var d := absf(dx)
	if d <= 1.0:
		return 0
	if d <= 3.0:
		return 1
	if d <= 5.0:
		return 2
	if d <= 8.0:
		return 3
	return 4


static func _roll4d6(rng: RandomNumberGenerator) -> int:
	return (
		rng.randi_range(1, 6) + rng.randi_range(1, 6)
		+ rng.randi_range(1, 6) + rng.randi_range(1, 6)
	)


static func _resolve_lane(rng: RandomNumberGenerator, att: int, deff: int) -> bool:
	var delta := att - deff
	var need := 15
	if delta <= -4:
		need = 24
	elif delta <= -2:
		need = 18
	elif delta <= 1:
		need = 15 if delta == 0 else (14 if delta > 0 else 17)
	elif delta <= 3:
		need = 12
	else:
		need = 8
	return _roll4d6(rng) >= need


static func _try_side_escape(
	rng: RandomNumberGenerator, a: Dictionary, b: Dictionary, da: String, db: String
) -> String:
	for pack in [[a, b, da, db, "a_escapes"], [b, a, db, da, "b_escapes"]]:
		var fleer: Dictionary = pack[0]
		var hunter: Dictionary = pack[1]
		var fd: String = pack[2]
		var hd: String = pack[3]
		var out_code: String = pack[4]
		if not FLEE_DYNAMICS.has(fd):
			continue
		var reluctant := RELUCTANT.has(hd) or FLEE_DYNAMICS.has(hd)
		if hd in ["Deny escape", "Intercept the join", "Deny the fort", "Pursue"]:
			reluctant = false
		if _escape_check(rng, fleer, hunter, reluctant):
			_note(fleer, "Escape succeeds (%s)" % ("reluctant" if reluctant else "hot"))
			return out_code
		_note(fleer, "Escape fails")
	return ""


static func _escape_check(
	rng: RandomNumberGenerator, fleer: Dictionary, hunter: Dictionary, reluctant: bool
) -> bool:
	var fd := _avg_dash(fleer)
	var hd := _avg_dash(hunter)
	var att := int(fd) + (2 if bool(fleer.get("fog", false)) else 0)
	var deff := int(hd)
	if reluctant:
		deff = maxi(1, deff - 3)
		att += 1
	return _resolve_lane(rng, att, deff)


static func _fire_all(rng: RandomNumberGenerator, att_side: Dictionary, def_side: Dictionary) -> void:
	var shooters: Array = []
	for u in _alive_units(att_side):
		if String(u.get("station", "")) == "front" or bool(u.get("bird", false)):
			shooters.append(u)
	# Cap shots per round for performance / report noise
	var fired := 0
	for u in shooters:
		if fired >= 6:
			break
		if _fire_unit(rng, att_side, def_side, u):
			fired += 1


static func _fire_unit(
	rng: RandomNumberGenerator, att_side: Dictionary, def_side: Dictionary, att_u: Dictionary
) -> bool:
	var targets := _alive_units(def_side)
	if targets.is_empty():
		return false
	var sheet: Dictionary = att_u.get("sheet", {})
	var mounts: Array = sheet.get("mounts", [])
	if mounts.is_empty():
		return false
	# Pick best legal mount + target
	var best_wid := ""
	var best_w: Dictionary = {}
	var best_tgt: Dictionary = {}
	var best_band := 3
	var best_score := -9999
	for m in mounts:
		if typeof(m) != TYPE_ARRAY or m.size() < 1:
			continue
		var wid := String(m[0])
		if not WEAPONS.has(wid):
			continue
		var w: Dictionary = WEAPONS[wid]
		for t in targets:
			var band := _abs_dx_to_band(float(att_u.get("x", 0.0)) - float(t.get("x", 0.0)))
			if not _mount_legal(w, t, band, bool(def_side.get("fog", false))):
				continue
			var sc := int(w.get("pen", 0)) * 10 - band * 2
			var th: Dictionary = t.get("sheet", {})
			var hull := String(th.get("hull", ""))
			if hull in ["warship", "monitor"]:
				sc += 5
			if sc > best_score:
				best_score = sc
				best_wid = wid
				best_w = w
				best_tgt = t
				best_band = band
	if best_wid.is_empty() or best_tgt.is_empty():
		return false
	return _resolve_shot(rng, att_side, def_side, att_u, best_tgt, best_wid, best_w, best_band)


static func _mount_legal(w: Dictionary, tgt: Dictionary, band: int, fog: bool) -> bool:
	var sheet: Dictionary = tgt.get("sheet", {})
	var hull := String(sheet.get("hull", ""))
	var size := String(sheet.get("size", "M"))
	var small := hull in ["flight", "picket"] or size == "S"
	var kind := String(w.get("kind", ""))
	if kind == "plasma" and small and not (band <= 1 and int(w.get("size", 1)) <= 2):
		return false
	if kind == "cannon" and not small:
		if band >= 3:
			return false
		if band >= 2 and not fog:
			return false
	return true


static func _resolve_shot(
	rng: RandomNumberGenerator,
	att_side: Dictionary,
	def_side: Dictionary,
	att_u: Dictionary,
	def_u: Dictionary,
	wid: String,
	w: Dictionary,
	band: int,
) -> bool:
	var sheet_d: Dictionary = def_u.get("sheet", {})
	var size := String(sheet_d.get("size", "M"))
	var diffs: Array = LANE_DIFF.get(size, LANE_DIFF["M"])
	var lane := int(diffs[clampi(band, 0, 4)])
	var fo := maxi(0, band - int(w.get("anchor", 1)))
	var fog_n := 1 if bool(def_side.get("fog", false)) else 0
	var kind := String(w.get("kind", ""))
	var hit := false
	if kind == "cannon" and (fog_n > 0 or band <= 1):
		var spr := int(w.get("spray", 0)) - (2 if band >= 2 else 0)
		hit = _resolve_lane(rng, spr, lane)
		if hit:
			hit = _resolve_lane(rng, maxi(1, int(w.get("pen", 1))), int(sheet_d.get("prot", 3)))
	else:
		var tr := int(w.get("track", 5)) - int(w.get("dt", 1)) * fo
		var ac := int(w.get("acc", 4)) - int(w.get("da", 1)) * fo
		hit = _resolve_lane(rng, tr, lane)
		if hit:
			hit = _resolve_lane(rng, ac, int(def_u.get("reac", 3)))
		if hit:
			hit = _resolve_lane(rng, maxi(1, int(w.get("pen", 1))), int(sheet_d.get("prot", 3)))
	var cls_a := String(att_u.get("class", "?"))
	var cls_d := String(def_u.get("class", "?"))
	_note(att_side, "%s %s→%s %s [%s]" % [
		cls_a, wid, cls_d, "hit" if hit else "miss", BANDS[clampi(band, 0, 4)]
	])
	if not hit:
		return true
	var mount_n := 1
	for m in att_u.get("sheet", {}).get("mounts", []):
		if typeof(m) == TYPE_ARRAY and m.size() >= 2 and String(m[0]) == wid:
			mount_n = int(m[1])
			break
	var stack := mini(3, maxi(1, int(att_u.get("count", 1))))
	var dmg := float(w.get("dmg", 3.0)) * float(mount_n) * (1.0 + 0.35 * float(stack - 1))
	if String(sheet_d.get("redun", "mid")) == "high":
		dmg *= 0.65
	def_u["hp"] = float(def_u.get("hp", 0.0)) - dmg
	def_u["morale"] = maxf(0.0, float(def_u.get("morale", 90.0)) - minf(2.5, 0.35 * dmg))
	_note(att_side, "  dmg %.1f %s → %s (hp %.1f)" % [dmg, kind, cls_d, float(def_u.get("hp", 0.0))])
	# Bird chance
	if String(sheet_d.get("hull", "")) != "flight" and rng.randf() < 0.12:
		def_u["mob"] = maxi(0, int(def_u.get("mob", 3)) - 2)
		var sheet_m := int(sheet_d.get("mob", 3))
		def_u["bird"] = int(def_u.get("mob", 0)) <= maxi(1, int(floor(float(sheet_m) / 3.0)))
		if bool(def_u.get("bird", false)):
			_note(att_side, "  BIRDED %s" % cls_d)
			def_u["morale"] = maxf(0.0, float(def_u.get("morale", 90.0)) - 1.5)
	if float(def_u.get("hp", 0.0)) <= 0.0:
		var lost := int(def_u.get("count", 1))
		if String(sheet_d.get("redun", "mid")) == "high":
			lost = maxi(1, int(lost / 2.0))
		def_u["count"] = maxi(0, int(def_u.get("count", 0)) - lost)
		def_u["hp"] = float(int(sheet_d.get("prot", 3)) * maxi(int(def_u.get("count", 0)), 0))
		def_u["morale"] = maxf(
			0.0,
			float(def_u.get("morale", 90.0))
			- (4.0 if String(sheet_d.get("hull", "")) in ["warship", "monitor"] else 2.0)
		)
		_note(att_side, "  %s attrition → %d" % [cls_d, int(def_u.get("count", 0))])
	if float(def_u.get("morale", 90.0)) <= 0.0 and int(def_u.get("count", 0)) > 0:
		def_u["struck"] = true
		_note(def_side, "M0 STRIKE %s" % cls_d)
	return true


static func _morale_tick(side: Dictionary) -> void:
	var nest := _has_hull(side, "scow")
	var faction := String(side.get("faction", ""))
	for u in side.get("units", []):
		var ud: Dictionary = u
		if bool(ud.get("struck", false)) or bool(ud.get("gone", false)):
			continue
		if int(ud.get("count", 0)) <= 0:
			continue
		var bleed := 0.1
		if faction == "Choir":
			bleed = 0.1 if nest else 2.0
		ud["morale"] = clampf(float(ud.get("morale", 90.0)) - bleed, 0.0, 100.0)
		if float(ud.get("morale", 0.0)) <= 0.0:
			ud["struck"] = true
			_note(side, "M0 STRIKE %s" % String(ud.get("class", "?")))


static func _layout_offsets(ships: Array, spacing: float = 0.0035) -> void:
	if ships.is_empty():
		return
	var rank := {"H+": 5, "H": 4, "L": 3, "M": 2, "S": 1}
	var order: Array = []
	for i in ships.size():
		order.append(i)
	order.sort_custom(func(ia: int, ib: int) -> bool:
		var sa := String(ships[ia].get("size", ""))
		var sb := String(ships[ib].get("size", ""))
		var ra := int(rank.get(sa, 0))
		var rb := int(rank.get(sb, 0))
		if ra != rb:
			return ra > rb
		return ia < ib
	)
	var n := ships.size()
	var cols := mini(4, maxi(1, int(ceil(sqrt(float(n))))))
	for place in order.size():
		var idx: int = order[place]
		var row := int(place / float(cols))
		var col_in_row := place % cols
		var row_start := row * cols
		var row_count := mini(cols, n - row_start)
		var x := (float(col_in_row) - float(row_count - 1) * 0.5) * spacing
		var z := float(row) * spacing
		ships[idx]["offset"] = [x, 0.0, z]
