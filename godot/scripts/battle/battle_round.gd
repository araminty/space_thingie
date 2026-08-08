extends RefCounted
class_name BattleRound
## Lightweight per-round combat stub ported from battle_sim fire_exchange /
## resolve_lane essentials (no dynamics/gambits/escape). One call ≈ one round.

## class -> {prot, mob, reac, hvy, med, scrn, skirm, size, hull, redun}
const CLASSES := {
	"Ward-keel": {"prot": 8, "mob": 3, "reac": 4, "hvy": 9, "med": 7, "scrn": 5, "skirm": 2, "size": "H", "hull": "warship", "redun": "mid"},
	"Lockbar": {"prot": 9, "mob": 1, "reac": 3, "hvy": 8, "med": 6, "scrn": 4, "skirm": 1, "size": "H", "hull": "monitor", "redun": "high"},
	"Ledger": {"prot": 5, "mob": 5, "reac": 5, "hvy": 5, "med": 5, "scrn": 5, "skirm": 3, "size": "M", "hull": "warship", "redun": "mid"},
	"Quill": {"prot": 2, "mob": 6, "reac": 8, "hvy": 1, "med": 3, "scrn": 4, "skirm": 7, "size": "S", "hull": "picket", "redun": "low"},
	"Cutter-fly": {"prot": 1, "mob": 8, "reac": 9, "hvy": 0, "med": 2, "scrn": 3, "skirm": 8, "size": "S", "hull": "flight", "redun": "low"},
	"Grain-gun": {"prot": 4, "mob": 2, "reac": 3, "hvy": 2, "med": 6, "scrn": 3, "skirm": 1, "size": "L", "hull": "scow", "redun": "high"},
	"Packet": {"prot": 3, "mob": 3, "reac": 4, "hvy": 1, "med": 5, "scrn": 4, "skirm": 2, "size": "M", "hull": "scow", "redun": "high"},
	"Pennant": {"prot": 7, "mob": 4, "reac": 5, "hvy": 9, "med": 7, "scrn": 4, "skirm": 3, "size": "H", "hull": "warship", "redun": "mid"},
	"Anvil": {"prot": 9, "mob": 1, "reac": 2, "hvy": 9, "med": 7, "scrn": 3, "skirm": 1, "size": "H", "hull": "monitor", "redun": "high"},
	"Lancer": {"prot": 4, "mob": 6, "reac": 5, "hvy": 6, "med": 6, "scrn": 4, "skirm": 3, "size": "M", "hull": "warship", "redun": "low"},
	"Whip": {"prot": 2, "mob": 8, "reac": 6, "hvy": 2, "med": 4, "scrn": 5, "skirm": 4, "size": "S", "hull": "chase", "redun": "low"},
	"Outrider": {"prot": 2, "mob": 7, "reac": 8, "hvy": 1, "med": 3, "scrn": 5, "skirm": 8, "size": "S", "hull": "picket", "redun": "low"},
	"Lance-fly": {"prot": 1, "mob": 8, "reac": 9, "hvy": 0, "med": 2, "scrn": 4, "skirm": 8, "size": "S", "hull": "flight", "redun": "low"},
	"Border": {"prot": 4, "mob": 2, "reac": 3, "hvy": 4, "med": 6, "scrn": 3, "skirm": 1, "size": "L", "hull": "scow", "redun": "high"},
	"Nidus": {"prot": 5, "mob": 2, "reac": 6, "hvy": 3, "med": 7, "scrn": 4, "skirm": 5, "size": "H+", "hull": "scow", "redun": "high"},
	"Chorus-hull": {"prot": 6, "mob": 1, "reac": 7, "hvy": 2, "med": 8, "scrn": 5, "skirm": 6, "size": "H+", "hull": "scow", "redun": "high"},
	"Thread": {"prot": 2, "mob": 7, "reac": 9, "hvy": 0, "med": 2, "scrn": 4, "skirm": 8, "size": "S", "hull": "picket", "redun": "low"},
	"Sting-fly": {"prot": 1, "mob": 9, "reac": 9, "hvy": 0, "med": 1, "scrn": 3, "skirm": 9, "size": "S", "hull": "flight", "redun": "low"},
	"Bleed-fly": {"prot": 1, "mob": 8, "reac": 8, "hvy": 0, "med": 2, "scrn": 5, "skirm": 8, "size": "S", "hull": "flight", "redun": "low"},
}

const SIZE_SCALE := {"H+": 2.4, "H": 2.0, "L": 1.5, "M": 1.35, "S": 0.65}


static func side_from_ships(
	name: String, faction: String, ships: Array, fleet_id: String = ""
) -> Dictionary:
	## Aggregate per-class units from ship_templates list (tagged by fleet_id).
	var by_class: Dictionary = {}
	for s in ships:
		var sd: Dictionary = s
		var cls := String(sd.get("class", sd.get("name", "Unknown")))
		if cls.contains("-") and not CLASSES.has(cls):
			# "Packet-1" → "Packet" when class missing
			var base := cls.rsplit("-", true, 1)[0]
			if CLASSES.has(base):
				cls = base
		if not by_class.has(cls):
			by_class[cls] = 0
		by_class[cls] = int(by_class[cls]) + 1
	var units: Array = []
	for cls in by_class.keys():
		var sheet: Dictionary = CLASSES.get(cls, {
			"prot": 3, "mob": 3, "reac": 3, "hvy": 2, "med": 3, "scrn": 3, "skirm": 2,
			"size": "M", "hull": "warship", "redun": "mid",
		})
		var count := int(by_class[cls])
		units.append({
			"class": cls,
			"count": count,
			"hp": float(int(sheet.get("prot", 3)) * count),
			"sheet": sheet,
			"gone": false,
			"fleet_id": fleet_id,
		})
	return {
		"name": name,
		"faction": faction,
		"morale": 90.0,
		"units": units,
		"log": [],
	}


static func append_fleet_to_side(
	side: Dictionary, name: String, faction: String, ships: Array, fleet_id: String
) -> void:
	## Merge a joiner's ships into an existing side, keeping per-fleet unit identity.
	var added := side_from_ships(name, faction, ships, fleet_id)
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
	# Refresh aggregate label when joiners arrive.
	var nm := String(side.get("name", ""))
	if not name.is_empty() and not nm.contains(name):
		side["name"] = "%s + %s" % [nm, name] if not nm.is_empty() else name
	if String(side.get("faction", "")).is_empty() and not faction.is_empty():
		side["faction"] = faction


static func ships_from_side(side: Dictionary) -> Array:
	## Expand living units back into per-hull ship_templates (all fleets).
	return _ships_from_units(side.get("units", []), "")


static func ships_from_side_for_fleet(side: Dictionary, fleet_id: String) -> Array:
	## Expand living units belonging to one fleet_id.
	return _ships_from_units(side.get("units", []), fleet_id)


static func _ships_from_units(units: Array, fleet_id_filter: String) -> Array:
	var ships: Array = []
	for u in units:
		var ud: Dictionary = u
		if bool(ud.get("gone", false)) or int(ud.get("count", 0)) <= 0:
			continue
		if float(ud.get("hp", 0.0)) <= 0.0:
			continue
		if not fleet_id_filter.is_empty() and String(ud.get("fleet_id", "")) != fleet_id_filter:
			continue
		var cls := String(ud.get("class", "Ship"))
		var sheet: Dictionary = ud.get("sheet", {})
		var size := String(sheet.get("size", "M"))
		var hull := String(sheet.get("hull", "warship"))
		var scale := float(SIZE_SCALE.get(size, 1.0))
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
			})
	_layout_offsets(ships)
	return ships


static func living_count(side: Dictionary) -> int:
	var n := 0
	for u in side.get("units", []):
		var ud: Dictionary = u
		if bool(ud.get("gone", false)):
			continue
		if int(ud.get("count", 0)) > 0 and float(ud.get("hp", 0.0)) > 0.0:
			n += int(ud.get("count", 0))
	return n


static func resolve_round(rng: RandomNumberGenerator, a: Dictionary, b: Dictionary) -> Dictionary:
	## Mutual slug fire + light morale bleed. Returns summary dict.
	a["log"] = []
	b["log"] = []
	_fire_exchange(rng, a, b)
	_fire_exchange(rng, b, a)
	_morale_bleed(a)
	_morale_bleed(b)
	var ca := living_count(a)
	var cb := living_count(b)
	var outcome := "ongoing"
	if ca <= 0 and cb <= 0:
		outcome = "mutual_wipe"
	elif ca <= 0:
		outcome = "b_wins"
	elif cb <= 0:
		outcome = "a_wins"
	elif float(a.get("morale", 90.0)) <= 0.0:
		outcome = "b_wins"
	elif float(b.get("morale", 90.0)) <= 0.0:
		outcome = "a_wins"
	return {
		"outcome": outcome,
		"a_ships": ca,
		"b_ships": cb,
		"a_morale": float(a.get("morale", 0.0)),
		"b_morale": float(b.get("morale", 0.0)),
		"log_a": a.get("log", []),
		"log_b": b.get("log", []),
	}


static func _note(side: Dictionary, msg: String) -> void:
	var log_lines: Array = side.get("log", [])
	log_lines.append(msg)
	side["log"] = log_lines


static func _alive_units(side: Dictionary) -> Array:
	var out: Array = []
	for u in side.get("units", []):
		var ud: Dictionary = u
		if bool(ud.get("gone", false)):
			continue
		if int(ud.get("count", 0)) > 0 and float(ud.get("hp", 0.0)) > 0.0:
			out.append(ud)
	return out


static func _gun(u: Dictionary) -> int:
	var sheet: Dictionary = u.get("sheet", {})
	return maxi(int(sheet.get("hvy", 0)), int(sheet.get("med", 0)))


static func _pick_slugger(side: Dictionary) -> Dictionary:
	var living := _alive_units(side)
	if living.is_empty():
		return {}
	var best: Dictionary = living[0]
	var best_g := _gun(best) * int(best.get("count", 1))
	for u in living:
		var ud: Dictionary = u
		var g := _gun(ud) * int(ud.get("count", 1))
		if g > best_g:
			best = ud
			best_g = g
	return best


static func _pick_target(side: Dictionary) -> Dictionary:
	var living := _alive_units(side)
	if living.is_empty():
		return {}
	var best: Dictionary = living[0]
	var best_score := _target_score(best)
	for u in living:
		var ud: Dictionary = u
		var sc := _target_score(ud)
		if sc > best_score:
			best = ud
			best_score = sc
	return best


static func _target_score(u: Dictionary) -> float:
	var sheet: Dictionary = u.get("sheet", {})
	var hull := String(sheet.get("hull", ""))
	var pri := 1
	match hull:
		"monitor", "warship":
			pri = 3
		"scow":
			pri = 2
		"chase":
			pri = 1
		_:
			pri = 0
	return float(pri) * 1000.0 + float(u.get("hp", 0.0))


static func _roll2d6(rng: RandomNumberGenerator) -> int:
	return rng.randi_range(1, 6) + rng.randi_range(1, 6)


static func _resolve_lane(rng: RandomNumberGenerator, att: int, deff: int) -> bool:
	var delta := att - deff
	var thresh := 8
	if delta <= -4:
		thresh = 12
	elif delta <= -2:
		thresh = 10
	elif delta <= 1:
		thresh = 8
	elif delta <= 3:
		thresh = 6
	else:
		thresh = 3
	return _roll2d6(rng) >= thresh


static func _fire_exchange(rng: RandomNumberGenerator, a: Dictionary, b: Dictionary) -> void:
	var att_u := _pick_slugger(a)
	var def_u := _pick_target(b)
	if att_u.is_empty() or def_u.is_empty():
		return
	var sheet_d: Dictionary = def_u.get("sheet", {})
	var att := _gun(att_u)
	var deff := int(sheet_d.get("prot", 3))
	var hull_d := String(sheet_d.get("hull", ""))
	if hull_d == "flight":
		att = maxi(1, att - 2)
		deff = int(sheet_d.get("reac", 3))
	var hit := _resolve_lane(rng, att, deff)
	var cls_a := String(att_u.get("class", "?"))
	var cls_d := String(def_u.get("class", "?"))
	_note(a, "%s vs %s — %s" % [cls_a, cls_d, "hit" if hit else "miss"])
	if not hit:
		return
	var dmg := 1.0 + float(maxi(0, att - deff)) * 0.35
	if String(sheet_d.get("redun", "mid")) == "high":
		dmg *= 0.65
	dmg *= float(int(att_u.get("count", 1)))
	def_u["hp"] = float(def_u.get("hp", 0.0)) - dmg
	_note(a, "  dmg %.1f → %s (hp %.1f)" % [dmg, cls_d, float(def_u.get("hp", 0.0))])
	b["morale"] = float(b.get("morale", 90.0)) - minf(2.5, 0.35 * dmg)
	if float(def_u.get("hp", 0.0)) <= 0.0:
		var lost := int(def_u.get("count", 1))
		if String(sheet_d.get("redun", "mid")) == "high":
			lost = maxi(1, int(lost / 2.0))
		def_u["count"] = maxi(0, int(def_u.get("count", 0)) - lost)
		var prot := int(sheet_d.get("prot", 3))
		def_u["hp"] = float(prot * maxi(int(def_u.get("count", 0)), 0))
		_note(a, "  %s attrition → count %d" % [cls_d, int(def_u.get("count", 0))])
		b["morale"] = float(b.get("morale", 90.0)) - (4.0 if hull_d in ["warship", "monitor"] else 2.0)


static func _morale_bleed(side: Dictionary) -> void:
	var bleed := 0.1
	if String(side.get("faction", "")) == "Choir":
		var nest := false
		for u in _alive_units(side):
			var sheet: Dictionary = u.get("sheet", {})
			if String(sheet.get("hull", "")) == "scow":
				nest = true
				break
		bleed = 0.1 if nest else 2.0
	if living_count(side) <= 0:
		side["morale"] = 0.0
	else:
		side["morale"] = clampf(float(side.get("morale", 90.0)) - bleed, 0.0, 100.0)


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
