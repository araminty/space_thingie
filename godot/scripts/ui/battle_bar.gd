extends PanelContainer
## Bottom HUD: friendly vs hostile compositions for the selected engaged fleet.

const MAX_FLEETS := 4
const FRIENDLY_TITLE := Color(0.78, 0.86, 0.95, 0.95)
const FRIENDLY_BODY := Color(0.62, 0.71, 0.85, 0.95)
const HOSTILE_TITLE := Color(0.78, 0.62, 0.95, 0.95)
const HOSTILE_BODY := Color(0.55, 0.82, 0.62, 0.92)
const VS_COLOR := Color(0.72, 0.76, 0.82, 0.75)
const SIZE_WEIGHT := {"H+": 2.4, "H": 2.0, "L": 1.5, "M": 1.35, "S": 0.65}
const ROSTER_FONT_SIZE := 11
const ROSTER_LINE_H := 13.0
const NAME_LINE_H := 16.0
const CARD_SEP := 2.0

@onready var _friendly_row: HBoxContainer = $Margin/RootRow/FriendlyRow
@onready var _hostile_row: HBoxContainer = $Margin/RootRow/HostileRow
@onready var _vs_lbl: Label = $Margin/RootRow/VsLabel
@onready var _round_lbl: Label = $Margin/RootRow/RoundLabel

var _shown_battle_id: String = ""


func _ready() -> void:
	visible = false
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	GameState.fleet_selection_changed.connect(_on_selection_changed)
	GameState.fleets_changed.connect(_refresh)
	GameState.battles_changed.connect(_refresh)
	_refresh()


func _on_selection_changed(_fleet_id: String) -> void:
	_refresh()


func _refresh() -> void:
	var fid := GameState.selected_fleet_id
	if fid.is_empty() or not GameState.has_fleet(fid) or not GameState.is_fleet_engaged(fid):
		_hide_bar()
		return
	var bid := GameState.fleet_battle_id(fid)
	if bid.is_empty() or not GameState.battles.has(bid):
		_hide_bar()
		return
	var battle: Dictionary = GameState.battles[bid]
	_shown_battle_id = bid
	_populate_side(_friendly_row, _side_ids(battle, true), battle, true)
	_populate_side(_hostile_row, _side_ids(battle, false), battle, false)
	if _round_lbl:
		_round_lbl.text = "R%d" % int(battle.get("round", 0))
	if _vs_lbl:
		_vs_lbl.text = "VS"
	visible = true


func _hide_bar() -> void:
	_shown_battle_id = ""
	visible = false
	_clear_row(_friendly_row)
	_clear_row(_hostile_row)


func _side_ids(battle: Dictionary, friendly: bool) -> Array:
	var key := "friendly_ids" if friendly else "hostile_ids"
	var ids: Array = []
	for x in battle.get(key, []):
		var s := String(x)
		if not s.is_empty():
			ids.append(s)
	if ids.is_empty():
		var single := String(battle.get("friendly_id" if friendly else "hostile_id", ""))
		if not single.is_empty():
			ids.append(single)
	return ids


func _populate_side(row: HBoxContainer, ids: Array, battle: Dictionary, friendly: bool) -> void:
	_clear_row(row)
	if row == null:
		return
	var ranked := _rank_fleets(ids, battle, friendly)
	var n := mini(ranked.size(), MAX_FLEETS)
	for i in n:
		row.add_child(_make_fleet_card(String(ranked[i]), battle, friendly))
	if ranked.size() > MAX_FLEETS:
		var more := Label.new()
		more.text = "+%d" % (ranked.size() - MAX_FLEETS)
		more.mouse_filter = Control.MOUSE_FILTER_IGNORE
		more.add_theme_font_size_override("font_size", 11)
		more.add_theme_color_override(
			"font_color", FRIENDLY_BODY if friendly else HOSTILE_BODY
		)
		more.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		row.add_child(more)


func _rank_fleets(ids: Array, battle: Dictionary, friendly: bool) -> Array:
	## Bigger first: ship count, then remaining HP / size weight.
	var scored: Array = []
	for fid in ids:
		var id_s := String(fid)
		if not GameState.has_fleet(id_s):
			continue
		var ships_n := _fleet_ship_count(id_s)
		var weight := _fleet_weight(id_s, battle, friendly)
		scored.append({"id": id_s, "n": ships_n, "w": weight})
	scored.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		if int(a["n"]) != int(b["n"]):
			return int(a["n"]) > int(b["n"])
		return float(a["w"]) > float(b["w"])
	)
	var out: Array = []
	for e in scored:
		out.append(String(e["id"]))
	return out


func _fleet_ship_count(fleet_id: String) -> int:
	var f: Dictionary = GameState.fleets[fleet_id]
	var templates = f.get("ship_templates", [])
	if typeof(templates) == TYPE_ARRAY and not templates.is_empty():
		return templates.size()
	var ships = f.get("ships", [])
	if typeof(ships) == TYPE_ARRAY:
		return ships.size()
	return 0


func _fleet_weight(fleet_id: String, battle: Dictionary, friendly: bool) -> float:
	## Prefer live battle-unit HP; fall back to size_scale sum on templates.
	var hp := _fleet_side_hp(fleet_id, battle, friendly)
	if hp > 0.0:
		return hp
	var f: Dictionary = GameState.fleets[fleet_id]
	var templates = f.get("ship_templates", [])
	var total := 0.0
	if typeof(templates) == TYPE_ARRAY:
		for t in templates:
			var td: Dictionary = t
			if td.has("size_scale"):
				total += float(td.get("size_scale", 1.0))
			else:
				var sz := String(td.get("size", "M"))
				total += float(SIZE_WEIGHT.get(sz, 1.0))
	return total


func _fleet_side_hp(fleet_id: String, battle: Dictionary, friendly: bool) -> float:
	var side: Dictionary = battle.get("side_a" if friendly else "side_b", {})
	var total := 0.0
	for u in side.get("units", []):
		var ud: Dictionary = u
		if String(ud.get("fleet_id", "")) != fleet_id:
			continue
		if bool(ud.get("gone", false)) or bool(ud.get("struck", false)):
			continue
		total += maxf(float(ud.get("hp", 0.0)), 0.0)
	return total


func _fleet_side_morale(fleet_id: String, battle: Dictionary, friendly: bool) -> float:
	var side: Dictionary = battle.get("side_a" if friendly else "side_b", {})
	var s := 0.0
	var n := 0
	for u in side.get("units", []):
		var ud: Dictionary = u
		if String(ud.get("fleet_id", "")) != fleet_id:
			continue
		if bool(ud.get("gone", false)) or bool(ud.get("struck", false)):
			continue
		if int(ud.get("count", 0)) <= 0 or float(ud.get("hp", 0.0)) <= 0.0:
			continue
		s += float(ud.get("morale", 90.0))
		n += 1
	if n <= 0:
		return float(side.get("morale", 90.0))
	return s / float(n)


func _make_fleet_card(fleet_id: String, battle: Dictionary, friendly: bool) -> Control:
	var f: Dictionary = GameState.fleets[fleet_id]
	var box := VBoxContainer.new()
	box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	box.size_flags_vertical = Control.SIZE_EXPAND_FILL
	box.clip_contents = true
	box.add_theme_constant_override("separation", int(CARD_SEP))
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE

	var name_lbl := Label.new()
	var side_hp := _fleet_side_hp(fleet_id, battle, friendly)
	var side_m := _fleet_side_morale(fleet_id, battle, friendly)
	name_lbl.text = "%s  M%.0f" % [String(f.get("name", "Fleet")), side_m]
	name_lbl.tooltip_text = "HP pool %.0f · avg morale %.0f" % [side_hp, side_m]
	name_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	name_lbl.add_theme_font_size_override("font_size", 12)
	name_lbl.add_theme_color_override(
		"font_color", FRIENDLY_TITLE if friendly else HOSTILE_TITLE
	)
	name_lbl.clip_text = true
	name_lbl.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	box.add_child(name_lbl)

	var max_lines := _roster_max_lines()
	var roster := Label.new()
	roster.text = _roster_lines(fleet_id, f, battle, friendly, max_lines)
	roster.mouse_filter = Control.MOUSE_FILTER_IGNORE
	roster.add_theme_font_size_override("font_size", ROSTER_FONT_SIZE)
	roster.add_theme_color_override(
		"font_color", FRIENDLY_BODY if friendly else HOSTILE_BODY
	)
	roster.autowrap_mode = TextServer.AUTOWRAP_OFF
	roster.max_lines_visible = max_lines
	roster.clip_text = true
	roster.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	roster.size_flags_vertical = Control.SIZE_EXPAND_FILL
	roster.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	box.add_child(roster)
	return box


func _roster_max_lines() -> int:
	## How many class×count lines fit under the fleet name in this bar.
	var bar_h := size.y if size.y > 1.0 else 110.0
	var margin_h := 16.0
	if has_node("Margin"):
		var m: MarginContainer = $Margin
		margin_h = float(
			m.get_theme_constant("margin_top") + m.get_theme_constant("margin_bottom")
		)
	var avail := bar_h - margin_h - NAME_LINE_H - CARD_SEP
	return maxi(1, int(floor(avail / ROSTER_LINE_H)))


func _roster_lines(
	fleet_id: String, fleet: Dictionary, battle: Dictionary, friendly: bool, max_lines: int
) -> String:
	## Vertical class×count list; prefer live battle units, else templates/ships.
	var by_class := _class_counts(fleet_id, fleet, battle, friendly)
	if by_class.is_empty():
		return "—"
	var keys: Array = by_class.keys()
	keys.sort()
	var parts: PackedStringArray = PackedStringArray()
	var n := keys.size()
	var show_n := mini(n, maxi(1, max_lines))
	for i in show_n:
		var cls := String(keys[i])
		parts.append("%s×%d" % [cls, int(by_class[cls])])
	if n > show_n:
		# Last visible line gets an ellipsis when more classes remain.
		var last_i := parts.size() - 1
		parts[last_i] = "%s…" % parts[last_i]
	return "\n".join(parts)


func _class_counts(
	fleet_id: String, fleet: Dictionary, battle: Dictionary, friendly: bool
) -> Dictionary:
	var by_class: Dictionary = {}
	var side: Dictionary = battle.get("side_a" if friendly else "side_b", {})
	var units = side.get("units", [])
	if typeof(units) == TYPE_ARRAY:
		for u in units:
			var ud: Dictionary = u
			if String(ud.get("fleet_id", "")) != fleet_id:
				continue
			if bool(ud.get("gone", false)):
				continue
			var cnt := int(ud.get("count", 0))
			if cnt <= 0 or float(ud.get("hp", 0.0)) <= 0.0:
				continue
			var cls := String(ud.get("class", "Ship"))
			if cls.is_empty():
				cls = "Ship"
			if not by_class.has(cls):
				by_class[cls] = 0
			by_class[cls] = int(by_class[cls]) + cnt
	if not by_class.is_empty():
		return by_class

	var templates = fleet.get("ship_templates", [])
	if typeof(templates) == TYPE_ARRAY and not templates.is_empty():
		for t in templates:
			var td: Dictionary = t
			var cls := String(td.get("class", ""))
			if cls.is_empty():
				cls = String(td.get("name", "Ship"))
			if not by_class.has(cls):
				by_class[cls] = 0
			by_class[cls] = int(by_class[cls]) + 1
		return by_class

	var ships = fleet.get("ships", [])
	if typeof(ships) == TYPE_ARRAY:
		for s in ships:
			var nm := String(s)
			var cls := nm
			if cls.contains("-"):
				var base := cls.rsplit("-", true, 1)[0]
				if not base.is_empty():
					cls = base
			if not by_class.has(cls):
				by_class[cls] = 0
			by_class[cls] = int(by_class[cls]) + 1
	return by_class


func _clear_row(row: HBoxContainer) -> void:
	if row == null:
		return
	for c in row.get_children():
		row.remove_child(c)
		c.queue_free()
