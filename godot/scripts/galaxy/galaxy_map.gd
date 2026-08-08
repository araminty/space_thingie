extends Node3D
## Builds the galaxy star MultiMesh + lane line mesh from exported JSON.
## Fog of war: undiscovered stars are deep-maroon single spheres and not clickable.
## In-transit fleets and parked friendly fleets use PlanetFlag zoom-inset markers.

const FOG_COLOR := Color(0.42, 0.04, 0.12, 1.0)
const FLEET_ACCENT := Color(0.55, 0.85, 0.95)
const FLEET_COLOR_A := Color(0.72, 0.82, 0.92)
const FLEET_COLOR_B := Color(0.12, 0.18, 0.28)
## Camera distance at/above which star glyphs use full authored size.
const STAR_ZOOM_REF_DIST := 1.6
## Floor on size when fully zoomed in (1 = no shrink).
const STAR_ZOOM_MIN_FACTOR := 0.55
## MultiMesh star sphere radius (diameter = 2× this × glyph scale × zoom).
const STAR_SPHERE_RADIUS := 0.0045
## Label3D font size; capital height ≈ font_size × pixel_size in world units.
const STAR_LABEL_FONT_SIZE := 36
## Cap height as a fraction of the displayed star diameter (~1.0 = match).
const STAR_LABEL_CAP_TO_DIAMETER := 1.0
## Gap between star edge and left edge of name (fraction of displayed diameter).
const STAR_LABEL_GAP_TO_DIAMETER := 0.08
## Visual-only inset for in-transit fleet flags along a lane (fraction of length).
## Keeps markers off star centers: display t ∈ [margin, 1−margin]. Star sphere
## radius is STAR_SPHERE_RADIUS (glyph scale up to ~1.9); 0.12 clears typical lane medians.
const TRANSIT_LANE_MARGIN := 0.12
## Max friendly fleet flags shown per known star on the galaxy map.
const SYSTEM_FLEET_FLAG_CAP := 3
## Galaxy Tab: wait this long for a second press before single-Tab (hover enter).
const TAB_DOUBLE_WINDOW_SEC := 0.4

@onready var _stars_mmi: MultiMeshInstance3D = $Stars
@onready var _lanes_mi: MeshInstance3D = $Lanes
@onready var _camera_rig: Node3D = $"../OrbitCamera"
@onready var _hud: Label = $"../../UI/GalaxyHud"
@onready var _transit_flags_root: Control = $"../../UI/GalaxyTransitFlags"
@onready var _fleet_panel: PanelContainer = $"../../UI/GalaxyFleetPanel"
@onready var _fleet_panel_title: Label = $"../../UI/GalaxyFleetPanel/Margin/VBox/Head/Titles/PanelTitle"
@onready var _fleet_panel_kind: Label = $"../../UI/GalaxyFleetPanel/Margin/VBox/Head/Titles/PanelKind"
@onready var _fleet_panel_close: Button = $"../../UI/GalaxyFleetPanel/Margin/VBox/Head/Close"
@onready var _fleet_panel_preview: TextureRect = $"../../UI/GalaxyFleetPanel/Margin/VBox/Preview"
@onready var _fleet_panel_stats: RichTextLabel = $"../../UI/GalaxyFleetPanel/Margin/VBox/Stats"
@onready var _fleet_panel_empty: Label = $"../../UI/GalaxyFleetPanel/Margin/VBox/Empty"
@onready var _fleet_panel_turn: Button = $"../../UI/GalaxyFleetPanel/Margin/VBox/TurnAround"

var _data := GalaxyData.new()
var _star_positions: PackedVector3Array = PackedVector3Array()
var _pick_enabled := true
var _labels_root: Node3D
## Homeworld Label3Ds: {node, pos, base_scale} — sized with star zoom.
var _star_labels: Array = []
## fleet_id -> {flag: PlanetFlag, fleet_id: String}
var _transit_markers: Dictionary = {}
## fleet_id -> {flag: PlanetFlag, fleet_id: String, star_id: int}
var _system_fleet_markers: Dictionary = {}
## star_id -> start_index into friendly list (cycle window when count > cap).
var _system_fleet_scroll: Dictionary = {}
## star_id -> {root: Control, up: Button, down: Button}
var _system_cycle_arrows: Dictionary = {}
## Galaxy camera pose captured when entering a system (restored on return).
var _saved_camera: Dictionary = {}
## Per MultiMesh instance: authored world position + base glyph scale.
var _glyph_pos: PackedVector3Array = PackedVector3Array()
var _glyph_base_scale: PackedFloat32Array = PackedFloat32Array()
var _last_star_zoom_factor: float = -1.0
var _panel_fleet_id: String = ""
## Star under cursor (−1 = none). Same enterable rules as LMB pick.
var _hovered_star_id: int = -1
## Armed single-Tab: hover id captured at first press; cleared on double or timeout.
var _tab_armed: bool = false
var _tab_arm_hover_id: int = -1
## Bumped to invalidate a pending single-Tab timeout after double-Tab / leave.
var _tab_gen: int = 0


func _ready() -> void:
	var err := _data.load_all()
	if err != OK:
		if _hud:
			_hud.text = "Missing galaxy export.\nRun: .venv/bin/python export_godot.py"
		return
	GameState.discovered = _data.revealed.duplicate()
	_labels_root = Node3D.new()
	_labels_root.name = "HomeworldLabels"
	add_child(_labels_root)
	_build_lanes()
	_build_stars()
	if _camera_rig:
		# Start angled + zoomed on Sol's home cluster (not the whole disk).
		var focus: Dictionary = _data.sol_home_focus()
		var center: Vector3 = focus.get("center", _data.map_center())
		var region := float(focus.get("region", 0.25))
		if _camera_rig.has_method("set_view"):
			_camera_rig.call_deferred("set_view", center, region, -55.0, 48.0)
		elif _camera_rig.has_method("set_focus"):
			_camera_rig.pitch_deg = 48.0
			_camera_rig.yaw_deg = -55.0
			_camera_rig.call_deferred("set_focus", center, region)
	if _hud:
		var named := 0
		for s in _data.stars:
			if bool(s.get("homeworld", false)) and _data.is_revealed(int(s.get("id", -1))):
				named += 1
		var known := _data.revealed_count()
		_hud.text = (
			"Stars %d · Known %d · Fog %d · Homeworlds %d · LMB open · RMB path (fleet) · transit select · ▶/Space · WASD/RMB/Wheel"
			% [_data.stars.size(), known, _data.stars.size() - known, named]
		)
	if _fleet_panel_close:
		_fleet_panel_close.focus_mode = Control.FOCUS_NONE
		_fleet_panel_close.pressed.connect(_close_fleet_panel)
	if _fleet_panel_turn:
		_fleet_panel_turn.focus_mode = Control.FOCUS_NONE
		_fleet_panel_turn.pressed.connect(_on_turn_around_pressed)
	_close_fleet_panel()
	GameState.entered_system.connect(_on_enter_system)
	GameState.returned_to_galaxy.connect(_on_return_galaxy)
	GameState.day_changed.connect(_on_day_changed)
	GameState.fleets_changed.connect(_on_fleets_changed)
	GameState.fleet_selection_changed.connect(_on_fleet_selection_changed)
	# Seed authored fleets so galaxy system flags appear before visiting Sol.
	GameState.seed_content_fleets()
	_refresh_transit_markers()
	_refresh_system_fleet_markers()


func _process(_delta: float) -> void:
	if not visible or not is_visible_in_tree():
		return
	_apply_star_zoom_scales()
	_place_transit_flags_on_screen()
	_place_system_fleet_flags_on_screen()
	_update_hovered_star()


func _on_day_changed(_day: float) -> void:
	_update_transit_marker_poses()
	if not _panel_fleet_id.is_empty():
		_refresh_fleet_panel()


func _on_fleets_changed() -> void:
	_refresh_transit_markers()
	_refresh_system_fleet_markers()
	if not _panel_fleet_id.is_empty():
		if not GameState.has_fleet(_panel_fleet_id):
			_close_fleet_panel()
		else:
			_refresh_fleet_panel()


func _on_fleet_selection_changed(fleet_id: String) -> void:
	if not _pick_enabled or not visible:
		return
	if fleet_id.is_empty():
		if not _panel_fleet_id.is_empty():
			_hide_fleet_panel_ui()
		return
	if not GameState.has_fleet(fleet_id):
		return
	_open_fleet_panel(fleet_id)


func _on_enter_system(_star_id: int) -> void:
	_pick_enabled = false
	_clear_tab_arm()
	_hovered_star_id = -1
	if _camera_rig and _camera_rig.has_method("snapshot"):
		_saved_camera = _camera_rig.snapshot()
	visible = false
	if _camera_rig:
		_camera_rig.visible = false
	_hide_transit_flags()
	_hide_system_fleet_flags()
	_hide_fleet_panel_ui()


func _on_return_galaxy() -> void:
	_pick_enabled = true
	visible = true
	if _camera_rig:
		_camera_rig.visible = true
		# Keep last galaxy pan/zoom/orbit — do not recenter on the map.
		if not _saved_camera.is_empty() and _camera_rig.has_method("restore"):
			_camera_rig.restore(_saved_camera)
	_refresh_transit_markers()
	_refresh_system_fleet_markers()
	var sel := GameState.selected_fleet_id
	if not sel.is_empty() and GameState.has_fleet(sel):
		_open_fleet_panel(sel)


func _star_world_pos(star_id: int) -> Vector3:
	if star_id < 0 or star_id >= _star_positions.size():
		return Vector3.ZERO
	return _star_positions[star_id]


func _refresh_transit_markers() -> void:
	if _transit_flags_root == null:
		return
	var live: Dictionary = {}
	for f in GameState.fleets_in_transit():
		var fid := String(f.get("id", ""))
		if fid.is_empty():
			continue
		live[fid] = f
		if not _transit_markers.has(fid):
			_transit_markers[fid] = _make_transit_marker(f)
	# Remove finished.
	var to_drop: Array = []
	for fid in _transit_markers.keys():
		if not live.has(fid):
			to_drop.append(fid)
	for fid2 in to_drop:
		var entry: Dictionary = _transit_markers[fid2]
		var flag: PlanetFlag = entry.get("flag") as PlanetFlag
		if is_instance_valid(flag):
			flag.queue_free()
		_transit_markers.erase(fid2)
	_update_transit_marker_poses()
	_place_transit_flags_on_screen()


func _make_transit_marker(fleet: Dictionary) -> Dictionary:
	var fname := String(fleet.get("name", "Fleet"))
	var fid := String(fleet.get("id", ""))
	var hostile := bool(fleet.get("hostile", false))
	var meta := {
		"name": fname,
		"marker": "fleet",
		"kind": "fleet_transit",
		"fleet_id": fid,
		"hostile": hostile,
	}
	var flag := PlanetFlag.new()
	_transit_flags_root.add_child(flag)
	flag.setup(meta, Vector3.ZERO, FLEET_ACCENT, FLEET_COLOR_A, FLEET_COLOR_B)
	flag.set_system_position_indicator(0.0, 0.0, 0.0, false)
	flag.visible = false
	# Selectable like system fleets (hostiles inspect-only if they ever transit).
	flag.opened.connect(func() -> void: _on_transit_flag_opened(fid))
	if flag.has_node("Frame"):
		var frame := flag.get_node("Frame") as Control
		if frame:
			if hostile:
				frame.tooltip_text = "Inspect hostile fleet in transit"
			else:
				frame.tooltip_text = "Select fleet in transit"
	return {"flag": flag, "fleet_id": fid, "name": fname}


func _on_transit_flag_opened(fleet_id: String) -> void:
	if not _pick_enabled or not visible:
		return
	# select_fleet → fleet_selection_changed opens the transit panel.
	GameState.select_fleet(fleet_id)
	if _panel_fleet_id != fleet_id:
		_open_fleet_panel(fleet_id)


func _update_transit_marker_poses() -> void:
	for f in GameState.fleets_in_transit():
		var fid := String(f.get("id", ""))
		if not _transit_markers.has(fid):
			continue
		var entry: Dictionary = _transit_markers[fid]
		var flag: PlanetFlag = entry.get("flag") as PlanetFlag
		if not is_instance_valid(flag):
			continue
		var a := int(f.get("from_star", -1))
		var b := int(f.get("to_star", -1))
		var t := GameState.transit_progress(f)
		var pa := _star_world_pos(a)
		var pb := _star_world_pos(b)
		# Remap progress for display only — arrival/timing still use raw t.
		var m := TRANSIT_LANE_MARGIN
		var display_t := m + clampf(t, 0.0, 1.0) * (1.0 - 2.0 * m)
		flag.world_pos = pa.lerp(pb, display_t)
		var left := maxf(0.0, float(f.get("transit_days", 28.0)) * (1.0 - t))
		var label_text := "%s  (%.0fd)" % [String(f.get("name", "Fleet")), ceilf(left)]
		flag.set_name_text(label_text)
		if flag.has_node("Frame"):
			var frame := flag.get_node("Frame") as Control
			if frame:
				var hostile := bool(f.get("hostile", false))
				if hostile:
					frame.tooltip_text = "Hostile · in transit · ETA %.0f days" % ceilf(left)
				else:
					frame.tooltip_text = "In transit · ETA %.0f days · click to select" % ceilf(left)


func _place_transit_flags_on_screen() -> void:
	if not visible or _transit_flags_root == null or not _transit_flags_root.visible:
		return
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return
	var vp := get_viewport().get_visible_rect().size
	var fleet_items: Array = []
	for fid in _transit_markers.keys():
		var entry: Dictionary = _transit_markers[fid]
		var flag: PlanetFlag = entry.get("flag") as PlanetFlag
		if not is_instance_valid(flag):
			continue
		var wp: Vector3 = flag.world_pos
		if cam.is_position_behind(wp):
			flag.visible = false
			continue
		var tip := cam.unproject_position(wp)
		if tip.x < -80.0 or tip.y < -80.0 or tip.x > vp.x + 80.0 or tip.y > vp.y + 80.0:
			flag.visible = false
			continue
		fleet_items.append({"flag": flag, "tip": tip})
	PlanetFlag.apply_fleet_flag_layout(fleet_items, vp)


func _hide_transit_flags() -> void:
	for fid in _transit_markers.keys():
		var entry: Dictionary = _transit_markers[fid]
		var flag: PlanetFlag = entry.get("flag") as PlanetFlag
		if is_instance_valid(flag):
			flag.visible = false


func _refresh_system_fleet_markers() -> void:
	## Up to SYSTEM_FLEET_FLAG_CAP friendly parked fleets per known star.
	if _transit_flags_root == null:
		return
	var live: Dictionary = {}  # fleet_id -> star_id
	var by_star: Dictionary = {}  # star_id -> Array of fleet dicts
	for s in _data.stars:
		var sid := int(s.get("id", -1))
		if sid < 0 or not _data.is_revealed(sid):
			continue
		var friendlies: Array = GameState.friendly_fleets_in_system(sid)
		if friendlies.is_empty():
			continue
		by_star[sid] = friendlies
		var n := friendlies.size()
		var start := int(_system_fleet_scroll.get(sid, 0))
		if n > 0:
			start = posmod(start, n)
		_system_fleet_scroll[sid] = start
		var show_n := mini(SYSTEM_FLEET_FLAG_CAP, n)
		for i in show_n:
			var f: Dictionary = friendlies[(start + i) % n]
			var fid := String(f.get("id", ""))
			if fid.is_empty():
				continue
			live[fid] = sid
			if not _system_fleet_markers.has(fid):
				_system_fleet_markers[fid] = _make_system_fleet_marker(f, sid)
			else:
				var entry: Dictionary = _system_fleet_markers[fid]
				entry["star_id"] = sid
				_system_fleet_markers[fid] = entry
	# Drop fleets no longer in the visible window / left system / fogged.
	var to_drop: Array = []
	for fid in _system_fleet_markers.keys():
		if not live.has(fid):
			to_drop.append(fid)
	for fid2 in to_drop:
		var entry2: Dictionary = _system_fleet_markers[fid2]
		var flag: PlanetFlag = entry2.get("flag") as PlanetFlag
		if is_instance_valid(flag):
			flag.queue_free()
		_system_fleet_markers.erase(fid2)
	_sync_system_cycle_arrows(by_star)
	_place_system_fleet_flags_on_screen()


func _make_system_fleet_marker(fleet: Dictionary, star_id: int) -> Dictionary:
	var fname := String(fleet.get("name", "Fleet"))
	var fid := String(fleet.get("id", ""))
	var meta := {
		"name": fname,
		"marker": "fleet",
		"kind": "fleet_system",
		"fleet_id": fid,
		"star_id": star_id,
		"hostile": false,
	}
	var flag := PlanetFlag.new()
	_transit_flags_root.add_child(flag)
	flag.setup(meta, _star_world_pos(star_id), FLEET_ACCENT, FLEET_COLOR_A, FLEET_COLOR_B)
	flag.visible = false
	# Enable dial once we have live pose in _place_system_fleet_flags_on_screen.
	flag.set_system_position_indicator(0.0, 0.0, PlanetFlag.DIAL_FALLBACK_MAX_AU, true)
	flag.opened.connect(func() -> void: _on_system_fleet_flag_opened(fid))
	if flag.has_node("Frame"):
		var frame := flag.get_node("Frame") as Control
		if frame:
			frame.tooltip_text = "Select fleet in system"
	return {"flag": flag, "fleet_id": fid, "star_id": star_id, "name": fname}


func _on_system_fleet_flag_opened(fleet_id: String) -> void:
	if not _pick_enabled or not visible:
		return
	GameState.select_fleet(fleet_id)
	if _panel_fleet_id != fleet_id:
		_open_fleet_panel(fleet_id)


func _sync_system_cycle_arrows(by_star: Dictionary) -> void:
	## Show ▲/▼ only when a known system has more friendly fleets than the cap.
	var keep: Dictionary = {}
	for sid_v in by_star.keys():
		var sid := int(sid_v)
		var list: Array = by_star[sid]
		if list.size() <= SYSTEM_FLEET_FLAG_CAP:
			continue
		keep[sid] = true
		if not _system_cycle_arrows.has(sid):
			_system_cycle_arrows[sid] = _make_cycle_arrow_controls(sid)
	var drop: Array = []
	for sid2 in _system_cycle_arrows.keys():
		if not keep.has(sid2):
			drop.append(sid2)
	for sid3 in drop:
		var entry: Dictionary = _system_cycle_arrows[sid3]
		var root: Control = entry.get("root") as Control
		if is_instance_valid(root):
			root.queue_free()
		_system_cycle_arrows.erase(sid3)


func _make_cycle_arrow_controls(star_id: int) -> Dictionary:
	var root := Control.new()
	root.name = "FleetCycle_%d" % star_id
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_transit_flags_root.add_child(root)
	var vbox := VBoxContainer.new()
	vbox.mouse_filter = Control.MOUSE_FILTER_IGNORE
	vbox.add_theme_constant_override("separation", 2)
	root.add_child(vbox)
	var up := Button.new()
	up.text = "▲"
	up.focus_mode = Control.FOCUS_NONE
	up.custom_minimum_size = Vector2(22, 18)
	up.tooltip_text = "Show previous fleet"
	up.pressed.connect(func() -> void: _cycle_system_fleets(star_id, -1))
	vbox.add_child(up)
	var down := Button.new()
	down.text = "▼"
	down.focus_mode = Control.FOCUS_NONE
	down.custom_minimum_size = Vector2(22, 18)
	down.tooltip_text = "Show next fleet"
	down.pressed.connect(func() -> void: _cycle_system_fleets(star_id, 1))
	vbox.add_child(down)
	root.visible = false
	return {"root": root, "up": up, "down": down, "vbox": vbox}


func _cycle_system_fleets(star_id: int, delta: int) -> void:
	var list: Array = GameState.friendly_fleets_in_system(star_id)
	var n := list.size()
	if n <= SYSTEM_FLEET_FLAG_CAP:
		return
	var start := int(_system_fleet_scroll.get(star_id, 0))
	_system_fleet_scroll[star_id] = posmod(start + delta, n)
	_refresh_system_fleet_markers()


func _place_system_fleet_flags_on_screen() -> void:
	if not visible or _transit_flags_root == null or not _transit_flags_root.visible:
		return
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return
	var vp := get_viewport().get_visible_rect().size
	## star_id -> tips / flags for layout + arrow placement.
	var tips_by_star: Dictionary = {}
	for fid in _system_fleet_markers.keys():
		var entry: Dictionary = _system_fleet_markers[fid]
		var flag: PlanetFlag = entry.get("flag") as PlanetFlag
		if not is_instance_valid(flag):
			continue
		var sid := int(entry.get("star_id", -1))
		if sid < 0 or not _data.is_revealed(sid):
			flag.visible = false
			continue
		var star_wp := _star_world_pos(sid)
		if cam.is_position_behind(star_wp):
			flag.visible = false
			continue
		# Tip / world anchor = star center; lens stack offsets beside the glyph.
		var tip := cam.unproject_position(star_wp)
		if tip.x < -80.0 or tip.y < -80.0 or tip.x > vp.x + 80.0 or tip.y > vp.y + 80.0:
			flag.visible = false
			continue
		flag.world_pos = star_wp
		# Live in-system pose → round dial (rim = system cruise edge / ring).
		var px := 0.0
		var pz := 0.0
		if GameState.has_fleet(fid):
			var f: Dictionary = GameState.fleets[fid]
			px = float(f.get("pos_x", 0.0))
			pz = float(f.get("pos_z", 0.0))
		var max_au := GameState.system_cruise_edge_au(sid)
		if max_au < 1e-3:
			max_au = PlanetFlag.DIAL_FALLBACK_MAX_AU
		flag.set_system_position_indicator(px, pz, max_au, true)
		if not tips_by_star.has(sid):
			tips_by_star[sid] = []
		(tips_by_star[sid] as Array).append({"flag": flag, "tip": tip})
	# Layout per star so neighboring systems never merge stacks.
	for sid2 in tips_by_star.keys():
		PlanetFlag.apply_fleet_flag_layout(tips_by_star[sid2], vp)
	_place_system_cycle_arrows(tips_by_star, vp)


func _place_system_cycle_arrows(tips_by_star: Dictionary, viewport_size: Vector2) -> void:
	for sid in _system_cycle_arrows.keys():
		var entry: Dictionary = _system_cycle_arrows[sid]
		var root: Control = entry.get("root") as Control
		if not is_instance_valid(root):
			continue
		if not tips_by_star.has(sid):
			root.visible = false
			continue
		var items: Array = tips_by_star[sid]
		if items.is_empty():
			root.visible = false
			continue
		# Place arrows beside the stacked lenses (opposite the tip side).
		var min_x := INF
		var max_x := -INF
		var min_y := INF
		var max_y := -INF
		var tip_x_sum := 0.0
		for it in items:
			var flag: PlanetFlag = it.get("flag") as PlanetFlag
			if not is_instance_valid(flag) or not flag.visible:
				continue
			var r := flag.get_global_rect()
			min_x = minf(min_x, r.position.x)
			max_x = maxf(max_x, r.position.x + r.size.x)
			min_y = minf(min_y, r.position.y)
			max_y = maxf(max_y, r.position.y + r.size.y)
			tip_x_sum += (it.get("tip") as Vector2).x
		if min_x == INF:
			root.visible = false
			continue
		var vbox: Control = entry.get("vbox") as Control
		var arrow_w := 24.0
		var arrow_h := 40.0
		if vbox:
			arrow_w = maxf(24.0, vbox.get_combined_minimum_size().x)
			arrow_h = maxf(40.0, vbox.get_combined_minimum_size().y)
		var mid_y := (min_y + max_y) * 0.5 - arrow_h * 0.5
		var avg_tip_x := tip_x_sum / float(items.size())
		var ax: float
		# Prefer the side opposite the tip (stack lenses sit away from tip).
		if avg_tip_x < (min_x + max_x) * 0.5:
			# Tips left of lenses → arrows to the right of stack.
			ax = max_x + 4.0
		else:
			ax = min_x - arrow_w - 4.0
		ax = clampf(ax, 4.0, viewport_size.x - arrow_w - 4.0)
		mid_y = clampf(mid_y, 4.0, viewport_size.y - arrow_h - 4.0)
		root.position = Vector2(ax, mid_y)
		root.size = Vector2(arrow_w, arrow_h)
		root.visible = true


func _hide_system_fleet_flags() -> void:
	for fid in _system_fleet_markers.keys():
		var entry: Dictionary = _system_fleet_markers[fid]
		var flag: PlanetFlag = entry.get("flag") as PlanetFlag
		if is_instance_valid(flag):
			flag.visible = false
	for sid in _system_cycle_arrows.keys():
		var entry2: Dictionary = _system_cycle_arrows[sid]
		var root: Control = entry2.get("root") as Control
		if is_instance_valid(root):
			root.visible = false


func _star_label(star_id: int) -> String:
	if star_id < 0 or star_id >= _data.stars.size():
		return "System %d" % star_id if star_id >= 0 else "?"
	var s: Dictionary = _data.stars[star_id]
	var text := String(s.get("map_label", ""))
	if text.is_empty():
		text = String(s.get("label", ""))
	if text.is_empty():
		var special := String(s.get("special", ""))
		if not special.is_empty():
			text = special.capitalize()
	if text.is_empty():
		text = "System %d" % star_id
	return text


func _open_fleet_panel(fleet_id: String) -> void:
	if _fleet_panel == null or not GameState.has_fleet(fleet_id):
		return
	_panel_fleet_id = fleet_id
	_fleet_panel.visible = true
	_refresh_fleet_panel()


func _fleet_ship_lines(f: Dictionary) -> Array:
	## Returns [ship_count: int, ship_lines: String].
	var ships = f.get("ships", [])
	var templates = f.get("ship_templates", [])
	var ship_count := 0
	var ship_lines := ""
	if typeof(templates) == TYPE_ARRAY and not templates.is_empty():
		ship_count = templates.size()
		for t in templates:
			var td: Dictionary = t
			var nm := String(td.get("name", "Ship"))
			var cls := String(td.get("class", ""))
			var sz := String(td.get("size", ""))
			if not cls.is_empty() and not sz.is_empty():
				ship_lines += "\n  · %s  (%s · %s)" % [nm, cls, sz]
			elif not sz.is_empty():
				ship_lines += "\n  · %s  (%s)" % [nm, sz]
			elif not cls.is_empty():
				ship_lines += "\n  · %s  (%s)" % [nm, cls]
			else:
				ship_lines += "\n  · %s" % nm
	elif typeof(ships) == TYPE_ARRAY:
		ship_count = ships.size()
		for s in ships:
			ship_lines += "\n  · %s" % String(s)
	return [ship_count, ship_lines]


func _route_final_star(fleet_id: String) -> int:
	var route := GameState.fleet_route(fleet_id)
	var last := -1
	for hop in route:
		if typeof(hop) != TYPE_DICTIONARY:
			continue
		if String(hop.get("kind", "")) == "hyperlane":
			last = int(hop.get("to", -1))
	return last


func _refresh_fleet_panel() -> void:
	if _fleet_panel == null or _panel_fleet_id.is_empty():
		return
	if not GameState.has_fleet(_panel_fleet_id):
		_close_fleet_panel()
		return
	var f: Dictionary = GameState.fleets[_panel_fleet_id]
	var status := String(f.get("status", ""))
	var in_transit := status == "in_transit"
	var fname := String(f.get("name", "Fleet"))
	var hostile := bool(f.get("hostile", false))
	var engaged := bool(f.get("engaged", false))
	var faction := String(f.get("faction", ""))
	var ship_info: Array = _fleet_ship_lines(f)
	var ship_count: int = ship_info[0]
	var ship_lines: String = ship_info[1]
	var loc_short := ""
	var loc_line := ""
	var dest_line := "—"
	var eta_line := "—"
	var progress_line := ""
	var cooldown_line := ""
	var cd_left := GameState.hyperlane_entry_cooldown_left(_panel_fleet_id)
	if cd_left > 0.0 and not in_transit:
		cooldown_line = (
			"[color=#9eb6d8]Hyperlane ready[/color]  in %.0f days\n" % ceilf(cd_left)
		)
	if in_transit:
		var from_id := int(f.get("from_star", -1))
		var to_id := int(f.get("to_star", -1))
		var from_lbl := _star_label(from_id)
		var to_lbl := _star_label(to_id)
		loc_short = "in transit"
		loc_line = "in transit %s → %s" % [from_lbl, to_lbl]
		dest_line = "%s → %s" % [from_lbl, to_lbl]
		var p := GameState.transit_progress(f)
		var dur := maxf(float(f.get("transit_days", GameState.HYPERLANE_TRAVEL_DAYS)), 0.001)
		var left := maxf(0.0, dur * (1.0 - p))
		progress_line = "[color=#9eb6d8]Progress[/color]  %.0f%%\n" % (p * 100.0)
		eta_line = "%.0f days" % ceilf(left)
		var route_n := GameState.fleet_route(_panel_fleet_id).size()
		if route_n > 0:
			var final_id := _route_final_star(_panel_fleet_id)
			if final_id >= 0 and final_id != to_id:
				dest_line = "%s → %s · then %s (%d hops left)" % [
					from_lbl, to_lbl, _star_label(final_id), route_n
				]
	else:
		var sys_id := int(f.get("system_id", -1))
		var sys_lbl := _star_label(sys_id) if sys_id >= 0 else "?"
		loc_short = sys_lbl
		loc_line = sys_lbl
		var pursue_id := String(f.get("pursue_fleet_id", ""))
		var route_n2 := GameState.fleet_route(_panel_fleet_id).size()
		if hostile:
			dest_line = "stationary (hostile)"
		elif engaged:
			dest_line = "locked (battle)"
			var bid := GameState.fleet_battle_id(_panel_fleet_id)
			if not bid.is_empty() and GameState.battles.has(bid):
				eta_line = "round %d" % int(GameState.battles[bid].get("round", 0))
		elif not pursue_id.is_empty():
			var tname := pursue_id
			if GameState.has_fleet(pursue_id):
				tname = String(GameState.fleets[pursue_id].get("name", pursue_id))
			dest_line = "Pursuing %s" % tname
		elif route_n2 > 0:
			var final_id2 := _route_final_star(_panel_fleet_id)
			var next_hop := GameState.route_next_hyperlane_dest(_panel_fleet_id)
			var lane_hops := 0
			for hop in GameState.fleet_route(_panel_fleet_id):
				if typeof(hop) == TYPE_DICTIONARY and String(hop.get("kind", "")) == "hyperlane":
					lane_hops += 1
			var hops_n := lane_hops if lane_hops > 0 else route_n2
			if final_id2 >= 0:
				dest_line = "Route to %s · %d hop%s left" % [
					_star_label(final_id2), hops_n, "" if hops_n == 1 else "s"
				]
			elif next_hop >= 0:
				dest_line = "Route · next %s · %d hop%s left" % [
					_star_label(next_hop), hops_n, "" if hops_n == 1 else "s"
				]
			else:
				dest_line = "Route · %d hop%s left" % [hops_n, "" if hops_n == 1 else "s"]
		elif bool(f.get("ordered", false)):
			dest_line = "Disk dest (%.2f, %.2f) AU" % [
				float(f.get("dest_x", 0.0)), float(f.get("dest_z", 0.0))
			]
		else:
			dest_line = "—"
	if _fleet_panel_title:
		_fleet_panel_title.text = fname
	if _fleet_panel_kind:
		var head := faction if not faction.is_empty() else "Fleet"
		var bits: PackedStringArray = PackedStringArray([head])
		if hostile:
			bits.append("hostile")
		if engaged:
			bits.append("engaged")
		bits.append(loc_short)
		bits.append("%d ships" % ship_count)
		_fleet_panel_kind.text = " · ".join(bits)
	if _fleet_panel_preview:
		_fleet_panel_preview.texture = PlanetFlag.make_fleet_texture(128, FLEET_COLOR_A, FLEET_COLOR_B)
	if _fleet_panel_stats:
		_fleet_panel_stats.text = (
			"[color=#9eb6d8]Ships[/color]  %d%s\n"
			+ "[color=#9eb6d8]Location[/color]  %s\n"
			+ "[color=#9eb6d8]Destination[/color]  %s\n"
			+ "%s"
			+ "%s"
			+ "[color=#9eb6d8]ETA[/color]  %s\n"
			+ "[color=#9eb6d8]Sample day[/color]  %s"
		) % [
			ship_count,
			ship_lines,
			loc_line,
			dest_line,
			progress_line,
			cooldown_line,
			eta_line,
			GameState.day_label_text(),
		]
	if _fleet_panel_empty:
		if hostile:
			if in_transit:
				_fleet_panel_empty.text = "Inspect only — hostiles cannot be ordered while in transit."
			else:
				_fleet_panel_empty.text = "Inspect only — hostiles cannot be ordered."
		elif engaged:
			_fleet_panel_empty.text = "Engaged in battle — destinations locked until resolved."
		elif in_transit:
			_fleet_panel_empty.text = (
				"Turn around / Reverse heads back to origin.\n"
				+ "Button below, or RMB on this fleet’s transit flag."
			)
		else:
			_fleet_panel_empty.text = (
				"RMB a star to path there · Enter a system to manage locally.\n"
				+ "LMB empty / Esc deselects."
			)
	if _fleet_panel_turn:
		# Turn around only while mid-hyperlane (friendly).
		var can_turn := in_transit and not hostile
		_fleet_panel_turn.visible = can_turn
		_fleet_panel_turn.disabled = not can_turn
		_fleet_panel_turn.text = "Turn around"


func _close_fleet_panel() -> void:
	var was := _panel_fleet_id
	_hide_fleet_panel_ui()
	if not was.is_empty() and GameState.selected_fleet_id == was:
		GameState.clear_fleet_selection()


func _hide_fleet_panel_ui() -> void:
	_panel_fleet_id = ""
	if _fleet_panel:
		_fleet_panel.visible = false


func _on_turn_around_pressed() -> void:
	_try_reverse_selected_transit()


func _try_reverse_selected_transit() -> bool:
	var fid := _panel_fleet_id
	if fid.is_empty():
		fid = GameState.selected_fleet_id
	if fid.is_empty() or not GameState.has_fleet(fid):
		return false
	if bool(GameState.fleets[fid].get("hostile", false)):
		return false
	if not GameState.reverse_hyperlane_transit(fid):
		return false
	_panel_fleet_id = fid
	if _fleet_panel:
		_fleet_panel.visible = true
	_refresh_fleet_panel()
	return true


func _transit_flag_at_global(global_pos: Vector2) -> String:
	## Transit flag under global screen point (PlanetFlag frame hit).
	var best := ""
	for fid in _transit_markers.keys():
		var entry: Dictionary = _transit_markers[fid]
		var flag: PlanetFlag = entry.get("flag") as PlanetFlag
		if not is_instance_valid(flag) or not flag.visible:
			continue
		if flag.hit_test_global(global_pos):
			best = String(fid)
	return best


func _input(event: InputEvent) -> void:
	## RMB: reverse selected transit flag; else path selected fleet (in-system or
	## mid-transit) to a revealed star.
	if not _pick_enabled or not visible:
		return
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.pressed and mb.button_index == MOUSE_BUTTON_RIGHT:
			var hit := _transit_flag_at_global(mb.global_position)
			var sel := GameState.selected_fleet_id
			if not hit.is_empty() and not sel.is_empty() and hit == sel:
				if _try_reverse_selected_transit():
					get_viewport().set_input_as_handled()
				return
			if _try_rmb_path_to_star(mb.position):
				get_viewport().set_input_as_handled()


func _try_rmb_path_to_star(screen_pos: Vector2) -> bool:
	## Friendly movable fleet in-system or mid-transit → multi-hop path to star.
	var sel := GameState.selected_fleet_id
	if sel.is_empty() or not GameState.has_fleet(sel):
		return false
	var f: Dictionary = GameState.fleets[sel]
	if bool(f.get("hostile", false)) or bool(f.get("stationary", false)):
		return false
	if bool(f.get("engaged", false)):
		return false
	var status := String(f.get("status", ""))
	if status != "in_system" and status != "in_transit":
		return false
	var star_id := _pick_star(screen_pos)
	if star_id < 0:
		return false
	if not GameState.order_fleet_path_to_star(sel, star_id):
		return false
	# Keep / refresh sidebar for the still-selected fleet.
	_open_fleet_panel(sel)
	return true


func _unhandled_input(event: InputEvent) -> void:
	if not _pick_enabled or not visible:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_ESCAPE:
				if not _panel_fleet_id.is_empty() or (_fleet_panel != null and _fleet_panel.visible):
					_close_fleet_panel()
					get_viewport().set_input_as_handled()
				return
			KEY_TAB:
				_on_galaxy_tab()
				get_viewport().set_input_as_handled()
				return
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
			var id := _pick_star(mb.position)
			if id >= 0:
				GameState.enter_system(id)
				get_viewport().set_input_as_handled()
			elif not _panel_fleet_id.is_empty():
				# LMB empty space deselects transit fleet (same as system view).
				_close_fleet_panel()
				get_viewport().set_input_as_handled()


func _update_hovered_star() -> void:
	if not _pick_enabled or not visible:
		_hovered_star_id = -1
		return
	var mouse := get_viewport().get_mouse_position()
	_hovered_star_id = _pick_star(mouse)


func _clear_tab_arm() -> void:
	_tab_armed = false
	_tab_arm_hover_id = -1
	_tab_gen += 1


func _on_galaxy_tab() -> void:
	## Single Tab (after window): enter hovered known star. Double Tab: last viewed.
	if _tab_armed:
		_clear_tab_arm()
		var last := GameState.last_system_id
		if last >= 0:
			GameState.enter_system(last)
		return
	_tab_armed = true
	_tab_arm_hover_id = _hovered_star_id
	var gen := _tab_gen
	get_tree().create_timer(TAB_DOUBLE_WINDOW_SEC).timeout.connect(
		func() -> void: _on_tab_single_timeout(gen)
	)


func _on_tab_single_timeout(gen: int) -> void:
	if gen != _tab_gen or not _tab_armed:
		return
	var hover := _tab_arm_hover_id
	_tab_armed = false
	_tab_arm_hover_id = -1
	if not _pick_enabled or not visible:
		return
	if hover >= 0:
		GameState.enter_system(hover)


func _pick_star(screen_pos: Vector2) -> int:
	var cam := get_viewport().get_camera_3d()
	if cam == null or _star_positions.is_empty():
		return -1
	var from := cam.project_ray_origin(screen_pos)
	var dir := cam.project_ray_normal(screen_pos)
	var dist_cam := cam.global_position.distance_to(
		_camera_rig.target if _camera_rig else from
	)
	var threshold := maxf(0.006, dist_cam * 0.0045)
	var best_i := -1
	var best_d := threshold
	for i in _star_positions.size():
		if not _data.is_revealed(i):
			continue
		var p := _star_positions[i]
		var w := p - from
		var proj := w.dot(dir)
		if proj < 0.0:
			continue
		var closest := from + dir * proj
		var d := closest.distance_to(p)
		if d < best_d:
			best_d = d
			best_i = i
	if best_i < 0:
		return -1
	return int(_data.stars[best_i].get("id", best_i))


func _build_stars() -> void:
	var n := _data.stars.size()
	if n == 0:
		return

	var sphere := SphereMesh.new()
	sphere.radius = STAR_SPHERE_RADIUS
	sphere.height = STAR_SPHERE_RADIUS * 2.0
	sphere.radial_segments = 8
	sphere.rings = 4

	var mat := StandardMaterial3D.new()
	mat.vertex_color_use_as_albedo = true
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.emission_enabled = true
	mat.emission = Color(1, 1, 1)
	mat.emission_energy_multiplier = 0.85
	sphere.material = mat

	var instance_count := 0
	for i in n:
		var s: Dictionary = _data.stars[i]
		if _data.is_revealed(int(s.get("id", i))):
			instance_count += clampi(int(s.get("multiplicity", 1)), 1, 3)
		else:
			instance_count += 1

	for c in _labels_root.get_children():
		c.queue_free()
	_star_labels.clear()

	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	mm.mesh = sphere
	mm.instance_count = instance_count
	_star_positions.resize(n)
	_glyph_pos.resize(instance_count)
	_glyph_base_scale.resize(instance_count)
	_last_star_zoom_factor = -1.0

	var inst := 0
	for i in n:
		var s: Dictionary = _data.stars[i]
		var sid := int(s.get("id", i))
		var pos := Vector3(float(s.x), float(s.z), float(s.y))
		_star_positions[i] = pos
		var fogged := not _data.is_revealed(sid)

		if fogged:
			# Undiscovered: deep maroon single sphere (hide multiplicity).
			_glyph_pos[inst] = pos
			_glyph_base_scale[inst] = 0.85
			mm.set_instance_color(inst, FOG_COLOR)
			inst += 1
			continue

		var glyph_scale := 1.0
		var label := String(s.get("label", ""))
		var special := String(s.get("special", ""))
		var is_homeworld := bool(s.get("homeworld", false))
		var mult := clampi(int(s.get("multiplicity", 1)), 1, 3)
		if label.begins_with("ancient") and label.contains("core"):
			glyph_scale = 1.55
		elif special == "sol":
			glyph_scale = 1.9
		elif special == "neverdark" or label.begins_with("Neverdark"):
			glyph_scale = 1.85
		elif is_homeworld:
			glyph_scale = 1.55
		elif label == "treasure":
			glyph_scale = 1.7
		elif label == "ring network":
			glyph_scale = 1.2
		elif label.begins_with("locked frontier"):
			glyph_scale = 0.75
		elif label == "galactic core":
			glyph_scale = 0.7
		elif label == "locked wall" or label == "outer rim":
			glyph_scale = 0.75
		var col := _color_from_entry(s)
		var sep := 0.0038 * glyph_scale
		var offsets := _multiplicity_offsets(mult, sep, sid)
		var comp_scale := glyph_scale if mult == 1 else glyph_scale * 0.78
		var primary_scale := comp_scale * (1.12 if mult > 1 else 1.0)
		for oi in offsets.size():
			var o: Vector3 = offsets[oi]
			# Primary component slightly larger in multi-star glyphs.
			var s_i := comp_scale * (1.12 if oi == 0 and mult > 1 else 1.0)
			_glyph_pos[inst] = pos + o
			_glyph_base_scale[inst] = s_i
			mm.set_instance_color(inst, col)
			inst += 1

		if is_homeworld:
			var text := String(s.get("map_label", label))
			if text.is_empty():
				text = label
			var lbl := Label3D.new()
			lbl.text = text
			lbl.billboard = BaseMaterial3D.BILLBOARD_ENABLED
			lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
			lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
			lbl.font_size = STAR_LABEL_FONT_SIZE
			lbl.outline_size = 8
			lbl.modulate = Color(0.95, 0.97, 1.0, 0.95)
			lbl.no_depth_test = true
			_labels_root.add_child(lbl)
			_star_labels.append({
				"node": lbl,
				"pos": pos,
				"base_scale": primary_scale,
			})

	_stars_mmi.multimesh = mm
	_apply_star_zoom_scales(true)


func _star_zoom_factor() -> float:
	var dist := STAR_ZOOM_REF_DIST
	if _camera_rig != null:
		dist = float(_camera_rig.get("distance"))
	# Zoomed out (≥ ref) → full size; zoomed in → shrink toward MIN_FACTOR.
	return clampf(dist / STAR_ZOOM_REF_DIST, STAR_ZOOM_MIN_FACTOR, 1.0)


func _apply_star_zoom_scales(force: bool = false) -> void:
	if _stars_mmi == null or _stars_mmi.multimesh == null:
		return
	var zf := _star_zoom_factor()
	if not force and absf(zf - _last_star_zoom_factor) < 0.002:
		return
	_last_star_zoom_factor = zf
	var mm := _stars_mmi.multimesh
	var n := mini(mm.instance_count, _glyph_pos.size())
	for i in n:
		var s := _glyph_base_scale[i] * zf
		mm.set_instance_transform(
			i, Transform3D(Basis.IDENTITY.scaled(Vector3.ONE * s), _glyph_pos[i])
		)
	_apply_star_label_scales(zf)


func _apply_star_label_scales(zf: float) -> void:
	## Capital letter height ≈ displayed primary-star diameter (same zoom as glyphs).
	## Left-aligned origin sits just right of the star edge (world +X).
	for entry in _star_labels:
		var lbl: Label3D = entry.get("node")
		if lbl == null or not is_instance_valid(lbl):
			continue
		var s := float(entry.get("base_scale", 1.0)) * zf
		var radius := STAR_SPHERE_RADIUS * s
		var diameter := 2.0 * radius
		var cap_h := diameter * STAR_LABEL_CAP_TO_DIAMETER
		var fs := maxi(lbl.font_size, 1)
		lbl.pixel_size = cap_h / float(fs)
		# LEFT align: origin = left edge of text → clear star by radius + gap.
		var x_off := radius + diameter * STAR_LABEL_GAP_TO_DIAMETER
		lbl.position = entry.get("pos", Vector3.ZERO) + Vector3(x_off, 0.0, 0.0)


func _multiplicity_offsets(mult: int, sep: float, star_id: int) -> Array[Vector3]:
	## Screen-plane (XZ) companion offsets; yaw varies by star so glyphs don't all align.
	if mult <= 1:
		return [Vector3.ZERO]
	var yaw := fposmod(float(star_id) * 2.3999632, TAU)
	var c := cos(yaw)
	var s := sin(yaw)
	var out: Array[Vector3] = []
	if mult == 2:
		var half := sep * 1.05
		out.append(Vector3(-half * c, 0.0, -half * s))
		out.append(Vector3(half * c, 0.0, half * s))
		return out
	# Trinary: small equilateral triangle about the system center.
	var r := sep * 1.25
	for k in 3:
		var a := yaw + float(k) * TAU / 3.0
		out.append(Vector3(r * cos(a), 0.0, r * sin(a)))
	return out


func _build_lanes() -> void:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_LINES)
	var star_pos: Dictionary = {}
	for s in _data.stars:
		star_pos[int(s.id)] = Vector3(float(s.x), float(s.z), float(s.y))

	for lane in _data.lanes:
		var a: int = int(lane.a)
		var b: int = int(lane.b)
		if not star_pos.has(a) or not star_pos.has(b):
			continue
		var a_known := _data.is_revealed(a)
		var b_known := _data.is_revealed(b)
		# Hide lanes that don't touch the revealed neighborhood.
		if not a_known and not b_known:
			continue
		var col := _color_from_entry(lane)
		if not a_known or not b_known:
			# Edge of fog: mute the spur into unknown space.
			col = FOG_COLOR
			col.a = 0.28
		elif String(lane.get("paint", "")) == "black":
			col.a = 0.22
		elif not bool(lane.get("unlocked", false)):
			col.a = 0.55
		else:
			col.a = 0.9
		st.set_color(col)
		st.add_vertex(star_pos[a])
		st.set_color(col)
		st.add_vertex(star_pos[b])

	var mesh := st.commit()
	var mat := StandardMaterial3D.new()
	mat.vertex_color_use_as_albedo = true
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = Color(1, 1, 1, 1)
	_lanes_mi.mesh = mesh
	_lanes_mi.material_override = mat


func _color_from_entry(entry: Dictionary) -> Color:
	if entry.has("rgba"):
		var rgba: Array = entry.rgba
		return Color(float(rgba[0]), float(rgba[1]), float(rgba[2]), float(rgba[3]))
	var hex := String(entry.get("color", "#ffffff"))
	return Color.html(hex)
