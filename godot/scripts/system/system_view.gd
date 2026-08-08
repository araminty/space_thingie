extends Node3D
## Solar-system view: stars, orbits, planets, asteroid fields, hyperlane ovals,
## planet/fleet zoom-inset flags (hockey-stick leaders), and tiny ship meshes.

const MU_SOLAR := 0.00029591220828559115  # AU^3 / day^2
const SHIP_SCENE := preload("res://scenes/ships/basic_spaceship.tscn")
## Ship mesh is ~1 unit long; at system scale it must be microscopic.
const SHIP_WORLD_SCALE := 0.00085
## Edge-to-edge (diameter) crossing time at fleet cruise speed.
const FLEET_CROSSING_DAYS := 20.0
const FLEET_ARRIVE_EPS_AU := 0.002
## Pursue/follow holds this far from the target (cruise dest = standoff point).
const FOLLOW_STANDOFF_AU := 0.02

@onready var _bodies: Node3D = $Bodies
@onready var _camera_rig: Node3D = $"../OrbitCamera"
@onready var _title: Label = $"../../UI/SystemHud/Title"
@onready var _info: RichTextLabel = $"../../UI/SystemHud/Info"
@onready var _back: Button = $"../../UI/SystemHud/BackButton"
@onready var _flags_root: Control = $"../../UI/SystemHud/Flags"
@onready var _flag_hud: Label = $"../../UI/SystemHud/FlagHud"
@onready var _panel: PanelContainer = $"../../UI/SystemHud/PlanetPanel"
@onready var _panel_title: Label = $"../../UI/SystemHud/PlanetPanel/Margin/VBox/Head/Titles/PanelTitle"
@onready var _panel_kind: Label = $"../../UI/SystemHud/PlanetPanel/Margin/VBox/Head/Titles/PanelKind"
@onready var _panel_close: Button = $"../../UI/SystemHud/PlanetPanel/Margin/VBox/Head/Close"
@onready var _panel_preview: TextureRect = $"../../UI/SystemHud/PlanetPanel/Margin/VBox/Preview"
@onready var _panel_stats: RichTextLabel = $"../../UI/SystemHud/PlanetPanel/Margin/VBox/Stats"
@onready var _panel_empty: Label = $"../../UI/SystemHud/PlanetPanel/Margin/VBox/Empty"

var _data := SystemData.new()
var _star_id: int = -1
var _pickables: Array = []
var _flags: Array = []
var _panel_open := false
var _panel_meta: Dictionary = {}
## "planet" | "asteroid" | "fleet"
var _panel_mode := ""
## Planet orbiters: {mi, a, phase0, inc, period, pick_i, flag_i, meta}
var _planet_orbiters: Array = []
## Fleet orbiters: {root, a, phase0, inc, period, host, pick_i, flag_i, meta,
##   ordered, destination, dest_marker, hostile, stationary, engaged, orbiting,
##   pursue_fleet_id}
var _fleet_orbiters: Array = []
## Field orbiters: {mmi, template, period, inc, host, pick_i}
var _field_orbiters: Array = []
## Host star positions in Godot space (XZ disk).
var _host_positions: Array = []
var _host_mus: Array = []
## Max radial extent of the current system (AU); diameter = 2× this.
var _system_edge_au: float = 36.0
var _fleet_speed_au_per_day: float = 2.0 * 36.0 / FLEET_CROSSING_DAYS
var _selected_fleet_i: int = -1
## Hyperlane portals: {center, radius, target_star, target_label}
var _hyperlane_portals: Array = []


func _ready() -> void:
	visible = false
	if _back:
		_back.focus_mode = Control.FOCUS_NONE
		_back.pressed.connect(_on_back)
	if _panel_close:
		_panel_close.focus_mode = Control.FOCUS_NONE
		_panel_close.pressed.connect(close_panel)
	_close_panel_ui()
	GameState.entered_system.connect(_on_enter)
	GameState.returned_to_galaxy.connect(_on_leave)
	GameState.day_changed.connect(_on_day_changed)
	GameState.fleets_changed.connect(_on_fleets_changed)
	GameState.battles_changed.connect(_on_battles_changed)
	GameState.fleet_selection_changed.connect(_on_fleet_selection_changed)
	_data.load_all()


func _on_enter(star_id: int) -> void:
	_star_id = star_id
	visible = true
	_build(star_id)


func _on_leave() -> void:
	visible = false
	# Keep GameState.selected_fleet_id across galaxy ↔ system switches.
	_hide_panel_keep_selection()
	_clear_bodies()
	_star_id = -1
	_selected_fleet_i = -1


func _on_fleet_selection_changed(fleet_id: String) -> void:
	## Sync panel when selection changes while this system is open (e.g. arrivals).
	if not visible or not is_visible_in_tree() or _star_id < 0:
		return
	if fleet_id.is_empty():
		if _panel_mode == "fleet":
			_hide_panel_keep_selection()
		return
	var i := _fleet_index_by_id(fleet_id)
	if i < 0:
		return
	if _selected_fleet_i == i and _panel_mode == "fleet" and _panel_open:
		return
	_open_fleet_panel(_fleet_orbiters[i].meta)


func _on_back() -> void:
	GameState.return_to_galaxy()


func _on_day_changed(_day: float) -> void:
	if visible and is_visible_in_tree():
		_apply_orbits()
		_sync_fleets_from_state()
		# Fresh Kepler poses (GameState already ran contact; catch same-tick joins).
		GameState.try_join_proximity_battles(_star_id)
		GameState.try_start_proximity_battles(_star_id)
		_refresh_battle_hud()
		if _panel_open and not _panel_meta.is_empty():
			match _panel_mode:
				"planet":
					_refresh_planet_stats(_panel_meta)
				"asteroid":
					_refresh_asteroid_stats(_panel_meta)
				"fleet":
					_refresh_fleet_stats(_panel_meta)


func _process(_delta: float) -> void:
	if not visible or not is_visible_in_tree():
		return
	_update_flag_positions()


func _input(event: InputEvent) -> void:
	## RMB: pursue if on another fleet marker; else fixed disk dest (consumes orbit RMB).
	if not visible or not is_visible_in_tree():
		return
	if _panel_mode != "fleet" or _selected_fleet_i < 0:
		return
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.pressed and mb.button_index == MOUSE_BUTTON_RIGHT:
			if _try_rmb_fleet_order(mb.position):
				get_viewport().set_input_as_handled()


func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_ESCAPE:
				if _panel_open:
					close_panel()
				else:
					GameState.return_to_galaxy()
				get_viewport().set_input_as_handled()
				return
			KEY_TAB:
				# Always leave system view (even if a panel is open).
				GameState.return_to_galaxy()
				get_viewport().set_input_as_handled()
				return
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
			_try_pick(mb.position)
			get_viewport().set_input_as_handled()


func _on_fleets_changed() -> void:
	## Spawn arrivals; despawn wiped/left fleets; refresh ship meshes after rounds.
	if not visible or not is_visible_in_tree() or _star_id < 0:
		return
	_despawn_missing_live_fleets()
	_spawn_missing_live_fleets()
	_sync_fleet_visuals_from_state()
	_refresh_battle_hud()
	_restore_selected_fleet_panel()


func _on_battles_changed() -> void:
	if not visible or not is_visible_in_tree() or _star_id < 0:
		return
	_sync_fleet_visuals_from_state()
	_freeze_engaged_destinations()
	_refresh_battle_hud()
	if _panel_open and _panel_mode == "fleet" and not _panel_meta.is_empty():
		_refresh_fleet_stats(_panel_meta)


func _freeze_engaged_destinations() -> void:
	## Clear ordered motion / pursue / hide dest rings while a fleet is engaged.
	## Leaving orbit (orbiting=false) so post-battle survivors stay at contact pose.
	for i in _fleet_orbiters.size():
		var orb: Dictionary = _fleet_orbiters[i]
		var fid := String(orb.get("fleet_id", ""))
		var engaged := GameState.is_fleet_engaged(fid) or bool(orb.get("engaged", false))
		orb["engaged"] = engaged
		var meta: Dictionary = orb.get("meta", {})
		meta["engaged"] = engaged
		if engaged:
			orb["ordered"] = false
			orb["orbiting"] = false
			orb["pursue_fleet_id"] = ""
			meta["ordered"] = false
			meta["orbiting"] = false
			meta["pursue_fleet_id"] = ""
			var marker: MeshInstance3D = orb.get("dest_marker") as MeshInstance3D
			if is_instance_valid(marker):
				marker.visible = false
			if GameState.has_fleet(fid):
				GameState.fleets[fid]["ordered"] = false
				GameState.fleets[fid]["orbiting"] = false
				GameState.fleets[fid]["pursue_fleet_id"] = ""
				GameState.fleets[fid]["route"] = []
		orb["meta"] = meta
		_fleet_orbiters[i] = orb

func _clear_bodies() -> void:
	for c in _bodies.get_children():
		c.queue_free()
	_pickables.clear()
	_planet_orbiters.clear()
	_fleet_orbiters.clear()
	_field_orbiters.clear()
	_host_positions.clear()
	_host_mus.clear()
	_hyperlane_portals.clear()
	_selected_fleet_i = -1
	for f in _flags:
		if is_instance_valid(f):
			f.queue_free()
	_flags.clear()
	if _flag_hud:
		_flag_hud.text = ""


func _build(star_id: int) -> void:
	_clear_bodies()
	_hide_panel_keep_selection()
	var content: Dictionary = _data.get_system(star_id)
	if content.is_empty():
		if _title:
			_title.text = "System %d — missing data" % star_id
		if _info:
			_info.text = "Re-run export_godot.py"
		return

	var mult := int(content.get("multiplicity", 1))
	var mu := float(content.get("mu", MU_SOLAR))
	var planets: Array = content.get("planets", [])
	var fields: Array = content.get("asteroid_fields", [])
	var fleets: Array = content.get("fleets", [])
	var hyperlanes: Array = content.get("hyperlanes", [])
	var stars_doc: Array = content.get("stars", [])

	if _title:
		var special := String(content.get("special", ""))
		if special == "neverdark":
			_title.text = "System %d  ·  Neverdark / Brightstep  ·  horseshoe trinary" % star_id
		elif special == "sol":
			_title.text = "System %d  ·  Sol  ·  Solar System" % star_id
		else:
			_title.text = "System %d  ·  %s  ·  μ=%.4g" % [
				star_id, _mult_label(mult), mu
			]
	if _info:
		_info.text = "Shared ▶ Play / Space advances galaxy time.\nOrbits lerp between whole days.\nEsc closes panel, then galaxy."

	_setup_hosts(stars_doc, mult, mu)
	_add_stars_visual()
	var extent := 1.0
	for i in _host_positions.size():
		var hp: Vector3 = _host_positions[i]
		extent = maxf(extent, hp.length() + 0.5)
	for p in planets:
		var host_i := int(p.get("host_star", 0))
		var host := Vector3.ZERO if host_i < 0 else _host_of(host_i)
		var a := float(p.get("orbital_radius", 1.0))
		extent = maxf(extent, host.length() + a)
		var local_mu := mu if host_i < 0 else _mu_of(host_i)
		_add_planet(p, local_mu, host)
	for af in fields:
		var host_i := int(af.get("host_star", 0))
		var host := Vector3.ZERO if host_i < 0 else _host_of(host_i)
		var a := float(af.get("orbital_radius", 1.0))
		var half_w := 0.5 * float(af.get("radial_width", 0.5))
		extent = maxf(extent, host.length() + a + half_w)
		var local_mu := mu if host_i < 0 else _mu_of(host_i)
		_add_asteroid_field(af, local_mu, host)
	for hl in hyperlanes:
		var hx := float(hl.get("x", 0.0))
		var hy := float(hl.get("y", 0.0))
		extent = maxf(extent, sqrt(hx * hx + hy * hy) + 1.0)
		_add_hyperlane(hl)

	var ring_r := float(content.get("hyperlane_ring_radius", 0.0))
	extent = maxf(extent, ring_r)
	_system_edge_au = maxf(extent, 1.0)
	_fleet_speed_au_per_day = (2.0 * _system_edge_au) / FLEET_CROSSING_DAYS

	# Seed content fleets into GameState once, then spawn whatever is live here.
	_seed_content_fleets(fleets, mu)
	_spawn_missing_live_fleets()

	_apply_orbits()
	_set_initial_camera(content, extent)
	_restore_selected_fleet_panel()


func _restore_selected_fleet_panel() -> void:
	## Re-open panel for GameState.selected_fleet_id if that fleet is here.
	var sel := GameState.selected_fleet_id
	if sel.is_empty():
		return
	var i := _fleet_index_by_id(sel)
	if i < 0:
		return
	if _selected_fleet_i == i and _panel_mode == "fleet" and _panel_open:
		return
	_open_fleet_panel(_fleet_orbiters[i].meta)


func _set_initial_camera(content: Dictionary, extent: float) -> void:
	## Angled view zoomed so a Jupiter-scale orbit (~inner system) fills the frame.
	if _camera_rig == null:
		return
	var view_r := _initial_view_radius_au(content, extent)
	if _camera_rig.has_method("set_view"):
		_camera_rig.call_deferred("set_view", Vector3.ZERO, view_r, -50.0, 38.0)
	elif _camera_rig.has_method("set_focus"):
		_camera_rig.pitch_deg = 38.0
		_camera_rig.yaw_deg = -50.0
		_camera_rig.call_deferred("set_focus", Vector3.ZERO, view_r)


func _initial_view_radius_au(content: Dictionary, extent: float) -> float:
	## Prefer Jupiter's orbit; else outermost gas giant; else a slice of system extent.
	var jupiter_a := -1.0
	var giant_a := -1.0
	for p in content.get("planets", []):
		var a := float(p.get("orbital_radius", 0.0))
		if a <= 0.0:
			continue
		if String(p.get("name", "")) == "Jupiter":
			jupiter_a = a
		if String(p.get("kind", "")) == "gas_giant":
			giant_a = maxf(giant_a, a)
	if jupiter_a > 0.0:
		return jupiter_a * 1.12
	if giant_a > 0.0:
		return giant_a * 1.12
	return clampf(extent * 0.28, 3.0, maxf(extent, 3.0))


func _setup_hosts(stars_doc: Array, mult: int, fallback_mu: float) -> void:
	_host_positions.clear()
	_host_mus.clear()
	if stars_doc.is_empty():
		# Legacy fallback: tight visual binary.
		var sep := 0.28 if mult >= 2 else 0.0
		_host_positions.append(Vector3(-sep * 0.55, 0, 0))
		_host_mus.append(fallback_mu)
		if mult >= 2:
			_host_positions.append(Vector3(sep * 0.45, 0, 0))
			_host_mus.append(fallback_mu)
		if mult >= 3:
			_host_positions.append(Vector3(0, 0, sep * 0.55))
			_host_mus.append(fallback_mu)
		return
	for s in stars_doc:
		# Python (x,y) disk → Godot (x, 0, y)
		_host_positions.append(Vector3(float(s.get("x", 0.0)), 0.0, float(s.get("y", 0.0))))
		_host_mus.append(float(s.get("mu", fallback_mu)))


func _host_of(host_i: int) -> Vector3:
	if host_i < 0 or host_i >= _host_positions.size():
		return Vector3.ZERO
	return _host_positions[host_i]


func _mu_of(host_i: int) -> float:
	if host_i < 0 or host_i >= _host_mus.size():
		return MU_SOLAR
	return float(_host_mus[host_i])


func _mult_label(mult: int) -> String:
	match mult:
		2:
			return "binary"
		3:
			return "trinary"
		_:
			return "single"


func _add_stars_visual() -> void:
	var fallback_colors := [
		Color(1.0, 0.70, 0.28),
		Color(1.0, 0.82, 0.48),
		Color(1.0, 0.88, 0.62),
	]
	for i in _host_positions.size():
		var pos: Vector3 = _host_positions[i]
		var r := 0.10 if i == 0 else (0.07 if i == 1 else 0.055)
		var col: Color = fallback_colors[mini(i, fallback_colors.size() - 1)]
		var mesh := SphereMesh.new()
		mesh.radius = r
		mesh.height = r * 2.0
		var mat := StandardMaterial3D.new()
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.albedo_color = col
		mat.emission_enabled = true
		mat.emission = col
		mat.emission_energy_multiplier = 1.4
		mesh.material = mat
		var mi := MeshInstance3D.new()
		mi.mesh = mesh
		mi.position = pos
		mi.name = "Star_%d" % i
		_bodies.add_child(mi)


func _orbit_point(a: float, phase: float, inclination: float) -> Vector3:
	var c := cos(phase)
	var s := sin(phase)
	var ci := cos(inclination)
	var si := sin(inclination)
	return Vector3(a * c, a * s * si, a * s * ci)


func _planet_colors(kind: String) -> Dictionary:
	if kind == "neverdark":
		return {
			"tip": Color(0.95, 0.72, 0.35),
			"a": Color(0.95, 0.55, 0.25),
			"b": Color(0.55, 0.82, 0.95),
		}
	if kind == "goldilocks":
		return {
			"tip": Color(0.43, 0.78, 1.0),
			"a": Color(0.56, 0.83, 0.66),
			"b": Color(0.12, 0.24, 0.16),
		}
	if kind == "rocky":
		return {
			"tip": Color(0.78, 0.62, 0.48),
			"a": Color(0.72, 0.55, 0.42),
			"b": Color(0.28, 0.2, 0.14),
		}
	return {
		"tip": Color(0.77, 0.63, 1.0),
		"a": Color(0.79, 0.71, 1.0),
		"b": Color(0.16, 0.125, 0.25),
	}


func _add_planet(p: Dictionary, mu: float, host: Vector3) -> void:
	var a := float(p.get("orbital_radius", 1.0))
	var phase0 := float(p.get("phase0", 0.0))
	var inc := float(p.get("inclination", 0.08))
	var kind := String(p.get("kind", "goldilocks"))
	var body_name := String(p.get("name", "World"))
	var orbit_mode := String(p.get("orbit_mode", "kepler"))
	var half_period := float(p.get("horseshoe_half_period_days", 30.0))
	var arc_frac := float(p.get("horseshoe_arc_frac", (360.0 - 50.0) / 360.0))
	var period := 0.0
	if orbit_mode == "horseshoe":
		period = 2.0 * maxf(half_period, 1.0)
	elif mu > 0.0:
		period = TAU * sqrt((a * a * a) / mu)

	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_LINE_STRIP)
	var col := Color(0.55, 0.65, 0.85, 0.35)
	if orbit_mode == "horseshoe":
		# Open arc covering horseshoe_arc_frac of a circle (not closed).
		var n_arc := 128
		var arc := TAU * arc_frac
		for i in n_arc:
			var u := float(i) / float(n_arc - 1)
			var th := phase0 + arc * u
			st.set_color(col)
			st.add_vertex(host + _orbit_point(a, th, inc))
	else:
		var n := maxi(48, int(ceil(period)) if period > 0.0 else 96)
		n = mini(n, 720)
		for i in n + 1:
			var th := phase0 + TAU * float(i) / float(n)
			st.set_color(col)
			st.add_vertex(host + _orbit_point(a, th, inc))
	var orbit_mi := MeshInstance3D.new()
	orbit_mi.mesh = st.commit()
	var omat := StandardMaterial3D.new()
	omat.vertex_color_use_as_albedo = true
	omat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	omat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	orbit_mi.material_override = omat
	orbit_mi.name = "%s_orbit" % body_name
	_bodies.add_child(orbit_mi)

	var pos := host + _planet_pos_at_day_ex(
		a, phase0, inc, period, 0.0, orbit_mode, half_period, arc_frac
	)
	var colors := _planet_colors(kind)
	var tip: Color = colors.tip
	var pr := 0.045 if kind == "gas_giant" else (0.022 if kind == "neverdark" else 0.012)
	var sphere := SphereMesh.new()
	sphere.radius = pr
	sphere.height = pr * 2.0
	var pmat := StandardMaterial3D.new()
	pmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	pmat.albedo_color = tip
	pmat.emission_enabled = true
	pmat.emission = tip
	pmat.emission_energy_multiplier = 0.9
	sphere.material = pmat
	var pmi := MeshInstance3D.new()
	pmi.mesh = sphere
	pmi.position = pos
	pmi.name = body_name
	_bodies.add_child(pmi)

	var meta := {
		"name": body_name,
		"kind": kind,
		"a": a,
		"period": period,
		"phase0": phase0,
		"host_star": int(p.get("host_star", 0)),
		"orbit_mode": orbit_mode,
		"horseshoe_half_period_days": half_period,
		"horseshoe_arc_frac": arc_frac,
		"homeworld": String(p.get("homeworld", "")),
		"climate": p.get("climate", {}),
		"notes": String(p.get("notes", "")),
		"size": float(p.get("size_radius", 1.0)),
		"day": int(floor(GameState.day)),
		"color_a": colors.a,
		"color_b": colors.b,
		"accent": tip,
	}
	var pick_i := _pickables.size()
	_pickables.append({
		"kind": "planet",
		"center": pos,
		"radius": maxf(pr * 4.0, 0.08),
		"meta": meta,
	})
	var flag_i := _flags.size()
	_spawn_flag(meta, pos, tip, colors.a, colors.b)
	_planet_orbiters.append({
		"mi": pmi,
		"a": a,
		"phase0": phase0,
		"inc": inc,
		"period": period,
		"orbit_mode": orbit_mode,
		"horseshoe_half_period_days": half_period,
		"horseshoe_arc_frac": arc_frac,
		"host": host,
		"pick_i": pick_i,
		"flag_i": flag_i,
		"meta": meta,
	})


func _spawn_flag(meta: Dictionary, world: Vector3, accent: Color, ca: Color, cb: Color) -> void:
	if _flags_root == null:
		return
	var flag := PlanetFlag.new()
	_flags_root.add_child(flag)
	flag.setup(meta, world, accent, ca, cb)
	flag.visible = false
	var marker := String(meta.get("marker", "planet"))
	if marker == "fleet":
		flag.opened.connect(func() -> void: _open_fleet_panel(meta))
	else:
		flag.opened.connect(func() -> void: _open_planet_panel(meta))
	_flags.append(flag)


func _fleet_colors(faction: String = "") -> Dictionary:
	## Subtle faction tint; default keeps the original cyan/slate look.
	if faction == "Compact":
		return {
			"tip": Color(0.45, 0.88, 0.78),
			"a": Color(0.62, 0.88, 0.82),
			"b": Color(0.08, 0.20, 0.22),
		}
	if faction == "March":
		return {
			"tip": Color(0.95, 0.70, 0.45),
			"a": Color(0.92, 0.78, 0.62),
			"b": Color(0.22, 0.14, 0.10),
		}
	if faction == "Choir":
		return {
			"tip": Color(0.72, 0.45, 0.95),
			"a": Color(0.55, 0.85, 0.55),
			"b": Color(0.18, 0.08, 0.22),
		}
	return {
		"tip": Color(0.55, 0.85, 0.95),
		"a": Color(0.72, 0.82, 0.92),
		"b": Color(0.12, 0.18, 0.28),
	}


func _fleet_id_for_content(star_id: int, fleet_name: String) -> String:
	return "%d:%s" % [star_id, fleet_name]


func _seed_content_fleets(fleets_doc: Array, mu: float) -> void:
	for fl in fleets_doc:
		var fd: Dictionary = fl
		var fname := String(fd.get("name", "Fleet"))
		var fid := _fleet_id_for_content(_star_id, fname)
		if GameState.has_fleet(fid):
			continue
		var host_i := int(fd.get("host_star", 0))
		var host := Vector3.ZERO if host_i < 0 else _host_of(host_i)
		var hostile := bool(fd.get("hostile", false))
		var stationary := bool(fd.get("stationary", false))
		var a := float(fd.get("orbital_radius", 1.0))
		var phase0 := float(fd.get("phase0", 0.0))
		var inc := float(fd.get("inclination", 0.02))
		var local_mu := mu if host_i < 0 else _mu_of(host_i)
		var period := 0.0
		if local_mu > 0.0 and not stationary:
			period = TAU * sqrt((a * a * a) / local_mu)
		var pos: Vector3
		if stationary and fd.has("position"):
			var p = fd.get("position", [0.0, 0.0, 0.0])
			pos = host + Vector3(float(p[0]), 0.0, float(p[2]) if p.size() > 2 else 0.0)
		else:
			pos = host + _planet_pos_at_day(a, phase0, inc, period, GameState.day)
		pos.y = 0.0
		var ship_names: Array = []
		for s in fd.get("ships", []):
			ship_names.append(String(s.get("name", "Ship")))
		GameState.register_fleet({
			"id": fid,
			"name": fname,
			"ships": ship_names,
			"ship_templates": fd.get("ships", []),
			"faction": String(fd.get("faction", "")),
			"role": String(fd.get("role", "")),
			"hostile": hostile,
			"stationary": stationary,
			# Kepler only until ordered / engaged; hostiles never orbit.
			"orbiting": not hostile and not stationary,
			"engaged": false,
			"battle_id": "",
			"ordered": false,
			"pursue_fleet_id": "",
			"status": "in_system",
			"system_id": _star_id,
			"pos_x": pos.x,
			"pos_z": pos.z,
			"a": a,
			"phase0": phase0,
			"inclination": inc,
			"period": period,
			"host_star": host_i,
			"needs_placement": false,
			"last_hyperlane_enter_day": GameState.HYPERLANE_ENTER_READY_DAY,
		})


func _spawn_missing_live_fleets() -> void:
	var present: Dictionary = {}
	for orb in _fleet_orbiters:
		present[String(orb.get("fleet_id", ""))] = true
	for f in GameState.fleets_in_system(_star_id):
		var fid := String(f.get("id", ""))
		if fid.is_empty() or present.has(fid):
			continue
		_spawn_fleet_record(f)


func _despawn_missing_live_fleets() -> void:
	## Remove visuals for fleets wiped in battle or that left the system.
	var live: Dictionary = {}
	for f in GameState.fleets_in_system(_star_id):
		live[String(f.get("id", ""))] = true
	var i := _fleet_orbiters.size() - 1
	while i >= 0:
		var fid := String(_fleet_orbiters[i].get("fleet_id", ""))
		if not live.has(fid):
			_despawn_fleet_at(i)
		i -= 1


func _sync_fleet_visuals_from_state() -> void:
	## Rebuild ship meshes / meta when battle rounds change ship lists.
	## Also mirror ordered / pursue / orbiting after hyperspace cancels.
	for i in _fleet_orbiters.size():
		var orb: Dictionary = _fleet_orbiters[i]
		var fid := String(orb.get("fleet_id", ""))
		if fid.is_empty() or not GameState.has_fleet(fid):
			continue
		var f: Dictionary = GameState.fleets[fid]
		var templates: Array = f.get("ship_templates", [])
		var names: Array = f.get("ships", [])
		var meta: Dictionary = orb.get("meta", {})
		meta["ship_templates"] = templates
		meta["ships"] = names
		meta["ship_count"] = names.size()
		meta["engaged"] = bool(f.get("engaged", false))
		meta["orbiting"] = bool(f.get("orbiting", meta.get("orbiting", true)))
		meta["ordered"] = bool(f.get("ordered", false))
		meta["pursue_fleet_id"] = String(f.get("pursue_fleet_id", ""))
		meta["dest_x"] = float(f.get("dest_x", meta.get("dest_x", 0.0)))
		meta["dest_z"] = float(f.get("dest_z", meta.get("dest_z", 0.0)))
		orb["meta"] = meta
		orb["engaged"] = bool(f.get("engaged", false))
		orb["hostile"] = bool(f.get("hostile", false))
		orb["stationary"] = bool(f.get("stationary", false))
		orb["orbiting"] = bool(f.get("orbiting", orb.get("orbiting", true)))
		orb["ordered"] = bool(f.get("ordered", false))
		orb["pursue_fleet_id"] = String(f.get("pursue_fleet_id", ""))
		orb["destination"] = Vector3(
			float(f.get("dest_x", 0.0)), 0.0, float(f.get("dest_z", 0.0))
		)
		var marker: MeshInstance3D = orb.get("dest_marker") as MeshInstance3D
		if not bool(orb["ordered"]) or bool(orb["engaged"]):
			if is_instance_valid(marker):
				marker.visible = false
		elif is_instance_valid(marker):
			marker.position = orb["destination"]
			marker.visible = true
		_rebuild_fleet_ships(orb, templates)
		_fleet_orbiters[i] = orb


func _rebuild_fleet_ships(orb: Dictionary, ships_doc: Array) -> void:
	var root: Node3D = orb.get("root") as Node3D
	if not is_instance_valid(root):
		return
	var old := root.get_children()
	for c in old:
		root.remove_child(c)
		c.free()
	for s in ships_doc:
		var sd: Dictionary = s
		var ship := SHIP_SCENE.instantiate() as Node3D
		ship.name = String(sd.get("name", "Ship"))
		var size_mul := float(sd.get("size_scale", 1.0))
		ship.scale = Vector3.ONE * SHIP_WORLD_SCALE * size_mul
		var off = sd.get("offset", [0.0, 0.0, 0.0])
		var ox := float(off[0]) if typeof(off) == TYPE_ARRAY and off.size() > 0 else 0.0
		var oy := float(off[1]) if typeof(off) == TYPE_ARRAY and off.size() > 1 else 0.0
		var oz := float(off[2]) if typeof(off) == TYPE_ARRAY and off.size() > 2 else 0.0
		ship.position = Vector3(ox, oy, oz)
		root.add_child(ship)


func _spawn_fleet_record(f: Dictionary) -> void:
	var host_i := int(f.get("host_star", 0))
	var host := Vector3.ZERO
	if host_i >= 0 and host_i < _host_positions.size():
		host = _host_of(host_i)
	var pos := Vector3(float(f.get("pos_x", 0.0)), 0.0, float(f.get("pos_z", 0.0)))
	if bool(f.get("needs_placement", false)):
		pos = _arrival_position(int(f.get("arrived_from", -1)))
		f["pos_x"] = pos.x
		f["pos_z"] = pos.z
		f["needs_placement"] = false
		GameState.update_fleet_system_pose(String(f.get("id", "")), _star_id, pos)
	_spawn_fleet_visual(f, host)


func _arrival_position(arrived_from: int) -> Vector3:
	## Arrive inward of the return portal (closer to system center than the oval).
	for p in _hyperlane_portals:
		if int(p.get("target_star", -1)) == arrived_from:
			var c: Vector3 = p.center
			return c * GameState.ARRIVAL_INSET
	if not _hyperlane_portals.is_empty():
		var c2: Vector3 = _hyperlane_portals[0].center
		return c2 * GameState.ARRIVAL_INSET
	return Vector3(_system_edge_au * 0.5, 0.0, 0.0)


func _spawn_fleet_visual(f: Dictionary, host: Vector3) -> void:
	var fleet_name := String(f.get("name", "Fleet"))
	var fleet_id := String(f.get("id", fleet_name))
	var a := float(f.get("a", 1.0))
	var phase0 := float(f.get("phase0", 0.0))
	var inc := float(f.get("inclination", 0.02))
	var period := float(f.get("period", 0.0))
	var pos := Vector3(float(f.get("pos_x", 0.0)), 0.0, float(f.get("pos_z", 0.0)))
	pos.y = 0.0
	var faction := String(f.get("faction", ""))
	var hostile := bool(f.get("hostile", false))
	var stationary := bool(f.get("stationary", false))
	var engaged := bool(f.get("engaged", false))
	var orbiting := bool(f.get("orbiting", not hostile and not stationary))
	var colors := _fleet_colors(faction)
	var tip: Color = colors.tip

	var root := Node3D.new()
	root.name = fleet_name
	root.position = pos
	_bodies.add_child(root)

	var ships_doc: Array = f.get("ship_templates", [])
	var ship_names: Array = f.get("ships", [])
	if ships_doc.is_empty() and typeof(ship_names) == TYPE_ARRAY:
		for sn in ship_names:
			ships_doc.append({"name": String(sn), "template": "basic_spaceship", "offset": [0.0, 0.0, 0.0]})
	if ships_doc.is_empty():
		ships_doc = [
			{"name": "Ship-1", "offset": [0.0, 0.0, 0.0]},
			{"name": "Ship-2", "offset": [-0.0035, 0.0, 0.0035]},
			{"name": "Ship-3", "offset": [0.0035, 0.0, 0.0035]},
		]
	var resolved_names: Array = []
	for s in ships_doc:
		var sd: Dictionary = s
		var ship_name := String(sd.get("name", "Ship"))
		resolved_names.append(ship_name)
		var ship := SHIP_SCENE.instantiate() as Node3D
		ship.name = ship_name
		var size_mul := float(sd.get("size_scale", 1.0))
		ship.scale = Vector3.ONE * SHIP_WORLD_SCALE * size_mul
		var off = sd.get("offset", [0.0, 0.0, 0.0])
		var ox := float(off[0]) if typeof(off) == TYPE_ARRAY and off.size() > 0 else 0.0
		var oy := float(off[1]) if typeof(off) == TYPE_ARRAY and off.size() > 1 else 0.0
		var oz := float(off[2]) if typeof(off) == TYPE_ARRAY and off.size() > 2 else 0.0
		ship.position = Vector3(ox, oy, oz)
		root.add_child(ship)

	var fleet_i := _fleet_orbiters.size()
	var meta := {
		"name": fleet_name,
		"marker": "fleet",
		"kind": "fleet",
		"fleet_i": fleet_i,
		"fleet_id": fleet_id,
		"a": a,
		"period": period,
		"phase0": phase0,
		"host_star": int(f.get("host_star", 0)),
		"ship_count": resolved_names.size(),
		"ships": resolved_names,
		"ship_templates": ships_doc,
		"faction": faction,
		"role": String(f.get("role", "")),
		"hostile": hostile,
		"stationary": stationary,
		"engaged": engaged,
		"orbiting": orbiting,
		"day": int(floor(GameState.day)),
		"color_a": colors.a,
		"color_b": colors.b,
		"accent": tip,
		"ordered": bool(f.get("ordered", false)),
		"dest_x": float(f.get("dest_x", 0.0)),
		"dest_z": float(f.get("dest_z", 0.0)),
		"pursue_fleet_id": String(f.get("pursue_fleet_id", "")),
	}
	# Hostiles are pickable for inspect; movement is blocked separately.
	var pick_i := _pickables.size()
	_pickables.append({
		"kind": "fleet",
		"center": pos,
		"radius": 0.12,
		"meta": meta,
	})
	var flag_i := _flags.size()
	_spawn_flag(meta, pos, tip, colors.a, colors.b)
	_fleet_orbiters.append({
		"root": root,
		"fleet_id": fleet_id,
		"a": a,
		"phase0": phase0,
		"inc": inc,
		"period": period,
		"host": host,
		"pick_i": pick_i,
		"flag_i": flag_i,
		"meta": meta,
		"hostile": hostile,
		"stationary": stationary,
		"engaged": engaged,
		"orbiting": orbiting,
		"ordered": bool(f.get("ordered", false)),
		"pursue_fleet_id": String(f.get("pursue_fleet_id", "")),
		"destination": Vector3(float(f.get("dest_x", 0.0)), 0.0, float(f.get("dest_z", 0.0))),
		"dest_marker": null,
	})

func _disk_point_from_screen(screen_pos: Vector2) -> Variant:
	## Ray ∩ solar disk plane (Y = 0). Returns Vector3 or null.
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return null
	var from := cam.project_ray_origin(screen_pos)
	var dir := cam.project_ray_normal(screen_pos)
	if absf(dir.y) < 1e-8:
		return null
	var t := -from.y / dir.y
	if t < 0.0:
		return null
	var p := from + dir * t
	p.y = 0.0
	return p


func _try_rmb_fleet_order(screen_pos: Vector2) -> bool:
	## Portal path > pursue another fleet > fixed disk dest. No orders for hostiles.
	if _selected_fleet_i < 0 or _selected_fleet_i >= _fleet_orbiters.size():
		return false
	var orb0: Dictionary = _fleet_orbiters[_selected_fleet_i]
	if bool(orb0.get("hostile", false)):
		return false
	var fid0 := String(orb0.get("fleet_id", ""))
	if GameState.is_fleet_engaged(fid0) or bool(orb0.get("engaged", false)):
		return false
	# Portal / linked-star marker takes pathing priority over pursue / disk dest.
	var portal := _hyperlane_at_screen(screen_pos)
	if not portal.is_empty():
		var dest_star := int(portal.get("target_star", -1))
		if dest_star >= 0 and GameState.order_fleet_path_to_star(fid0, dest_star):
			_apply_game_state_order_to_orb(_selected_fleet_i)
			if _panel_mode == "fleet" and not _panel_meta.is_empty():
				_refresh_fleet_stats(_panel_meta)
			return true
		return false
	var target_i := _fleet_index_at_screen(screen_pos)
	if target_i >= 0:
		# Hit a fleet marker: pursue (not self) and never also set disk dest.
		if target_i != _selected_fleet_i:
			_try_issue_pursue(_selected_fleet_i, target_i)
			if _panel_mode == "fleet" and not _panel_meta.is_empty():
				_refresh_fleet_stats(_panel_meta)
		return true
	return _set_selected_fleet_destination(screen_pos)


func _hyperlane_at_screen(screen_pos: Vector2) -> Dictionary:
	## Nearest hyperlane pickable under the ray (portal oval).
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return {}
	var from := cam.project_ray_origin(screen_pos)
	var dir := cam.project_ray_normal(screen_pos)
	var best: Dictionary = {}
	var best_score := 1e9
	for item in _pickables:
		if String(item.get("kind", "")) != "hyperlane":
			continue
		var center: Vector3 = item.center
		var radius: float = float(item.radius)
		var w := center - from
		var proj := w.dot(dir)
		if proj < 0.0:
			continue
		var closest := from + dir * proj
		var dist := closest.distance_to(center)
		if dist > radius:
			continue
		if dist < best_score:
			best_score = dist
			best = item.get("meta", {})
	return best


func _apply_game_state_order_to_orb(fleet_i: int) -> void:
	## Mirror GameState ordered dest / route onto a live orbiter + dest ring.
	if fleet_i < 0 or fleet_i >= _fleet_orbiters.size():
		return
	var orb: Dictionary = _fleet_orbiters[fleet_i]
	var fid := String(orb.get("fleet_id", ""))
	if fid.is_empty() or not GameState.has_fleet(fid):
		return
	var f: Dictionary = GameState.fleets[fid]
	var dest := Vector3(float(f.get("dest_x", 0.0)), 0.0, float(f.get("dest_z", 0.0)))
	orb["ordered"] = bool(f.get("ordered", false))
	orb["orbiting"] = bool(f.get("orbiting", false))
	orb["pursue_fleet_id"] = String(f.get("pursue_fleet_id", ""))
	orb["destination"] = dest
	var meta: Dictionary = orb.get("meta", {})
	meta["ordered"] = orb["ordered"]
	meta["orbiting"] = orb["orbiting"]
	meta["pursue_fleet_id"] = orb["pursue_fleet_id"]
	meta["dest_x"] = dest.x
	meta["dest_z"] = dest.z
	orb["meta"] = meta
	if bool(orb["ordered"]):
		_ensure_dest_marker(orb, dest)
	else:
		var marker: MeshInstance3D = orb.get("dest_marker") as MeshInstance3D
		if is_instance_valid(marker):
			marker.visible = false
	_fleet_orbiters[fleet_i] = orb


func _fleet_index_at_screen(screen_pos: Vector2) -> int:
	## Prefer PlanetFlag frame under cursor, else nearest fleet pickable along the ray.
	for i in _fleet_orbiters.size():
		var orb: Dictionary = _fleet_orbiters[i]
		var flag_i: int = int(orb.get("flag_i", -1))
		if flag_i < 0 or flag_i >= _flags.size():
			continue
		var flag: PlanetFlag = _flags[flag_i] as PlanetFlag
		if flag != null and is_instance_valid(flag) and flag.hit_test_global(screen_pos):
			return i
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return -1
	var from := cam.project_ray_origin(screen_pos)
	var dir := cam.project_ray_normal(screen_pos)
	var best_i := -1
	var best_score := 1e9
	for i in _pickables.size():
		var item: Dictionary = _pickables[i]
		if String(item.get("kind", "")) != "fleet":
			continue
		var center: Vector3 = item.center
		var radius: float = float(item.radius)
		var w := center - from
		var proj := w.dot(dir)
		if proj < 0.0:
			continue
		var closest := from + dir * proj
		var dist := closest.distance_to(center)
		if dist > radius:
			continue
		if dist < best_score:
			best_score = dist
			var meta: Dictionary = item.get("meta", {})
			best_i = int(meta.get("fleet_i", -1))
	return best_i


func _set_selected_fleet_destination(screen_pos: Vector2) -> bool:
	if _selected_fleet_i < 0 or _selected_fleet_i >= _fleet_orbiters.size():
		return false
	var orb0: Dictionary = _fleet_orbiters[_selected_fleet_i]
	if bool(orb0.get("hostile", false)):
		return false
	var fid0 := String(orb0.get("fleet_id", ""))
	if GameState.is_fleet_engaged(fid0) or bool(orb0.get("engaged", false)):
		return false
	var hit = _disk_point_from_screen(screen_pos)
	if hit == null:
		return false
	var dest: Vector3 = hit
	dest.y = 0.0
	if not fid0.is_empty():
		if not GameState.set_fleet_disk_destination(fid0, dest):
			return false
	var orb: Dictionary = _fleet_orbiters[_selected_fleet_i]
	orb["ordered"] = true
	orb["orbiting"] = false
	orb["pursue_fleet_id"] = ""  # fixed RMB dest replaces chase
	orb["destination"] = dest
	var meta: Dictionary = orb.meta
	meta["ordered"] = true
	meta["orbiting"] = false
	meta["pursue_fleet_id"] = ""
	meta["dest_x"] = dest.x
	meta["dest_z"] = dest.z
	_ensure_dest_marker(orb, dest)
	_fleet_orbiters[_selected_fleet_i] = orb
	if _panel_mode == "fleet":
		_refresh_fleet_stats(meta)
	return true


func _fleet_index_by_id(fleet_id: String) -> int:
	if fleet_id.is_empty():
		return -1
	for i in _fleet_orbiters.size():
		if String(_fleet_orbiters[i].get("fleet_id", "")) == fleet_id:
			return i
	return -1


func _try_issue_pursue(pursuer_i: int, target_i: int) -> void:
	## Friendly movable pursuer → chase target fleet (RMB on marker; selection stays).
	if pursuer_i < 0 or pursuer_i >= _fleet_orbiters.size():
		return
	if target_i < 0 or target_i >= _fleet_orbiters.size():
		return
	if pursuer_i == target_i:
		return
	var pursuer: Dictionary = _fleet_orbiters[pursuer_i]
	var target: Dictionary = _fleet_orbiters[target_i]
	if bool(pursuer.get("hostile", false)) or bool(pursuer.get("stationary", false)):
		return
	var pid := String(pursuer.get("fleet_id", ""))
	var tid := String(target.get("fleet_id", ""))
	if pid.is_empty() or tid.is_empty():
		return
	if GameState.is_fleet_engaged(pid) or bool(pursuer.get("engaged", false)):
		return
	if not GameState.set_fleet_pursuit(pid, tid):
		return
	var target_pos := Vector3.ZERO
	var troot: Node3D = target.get("root") as Node3D
	if is_instance_valid(troot):
		target_pos = Vector3(troot.position.x, 0.0, troot.position.z)
	else:
		target_pos = Vector3(
			float(GameState.fleets[tid].get("pos_x", 0.0)),
			0.0,
			float(GameState.fleets[tid].get("pos_z", 0.0)),
		)
	var pursuer_pos := Vector3.ZERO
	var proot: Node3D = pursuer.get("root") as Node3D
	if is_instance_valid(proot):
		pursuer_pos = Vector3(proot.position.x, 0.0, proot.position.z)
	elif GameState.has_fleet(pid):
		pursuer_pos = Vector3(
			float(GameState.fleets[pid].get("pos_x", 0.0)),
			0.0,
			float(GameState.fleets[pid].get("pos_z", 0.0)),
		)
	var dest := _pursue_standoff_dest(pursuer_pos, target_pos)
	pursuer["ordered"] = true
	pursuer["orbiting"] = false
	pursuer["pursue_fleet_id"] = tid
	pursuer["destination"] = dest
	var meta: Dictionary = pursuer.get("meta", {})
	meta["ordered"] = true
	meta["orbiting"] = false
	meta["pursue_fleet_id"] = tid
	meta["dest_x"] = dest.x
	meta["dest_z"] = dest.z
	pursuer["meta"] = meta
	_ensure_dest_marker(pursuer, dest)
	_fleet_orbiters[pursuer_i] = pursuer


func _pursue_standoff_dest(pursuer_pos: Vector3, target_pos: Vector3) -> Vector3:
	## Cruise dest on the segment toward target, FOLLOW_STANDOFF_AU short of T.
	## Already within standoff → hold at pursuer (no jitter toward exact overlap).
	var p := Vector3(pursuer_pos.x, 0.0, pursuer_pos.z)
	var t := Vector3(target_pos.x, 0.0, target_pos.z)
	var to_t := t - p
	var dist := to_t.length()
	if dist <= FOLLOW_STANDOFF_AU:
		return p
	return t - (to_t / dist) * FOLLOW_STANDOFF_AU


func _clear_orb_pursuit(orb: Dictionary) -> void:
	## Stop chase / ordered travel; leave at current pose (orbiting=false).
	orb["pursue_fleet_id"] = ""
	orb["ordered"] = false
	orb["orbiting"] = false
	var meta: Dictionary = orb.get("meta", {})
	meta["pursue_fleet_id"] = ""
	meta["ordered"] = false
	meta["orbiting"] = false
	orb["meta"] = meta
	var marker: MeshInstance3D = orb.get("dest_marker") as MeshInstance3D
	if is_instance_valid(marker):
		marker.visible = false
	var fid := String(orb.get("fleet_id", ""))
	if not fid.is_empty() and GameState.has_fleet(fid):
		GameState.fleets[fid]["pursue_fleet_id"] = ""
		GameState.fleets[fid]["ordered"] = false
		GameState.fleets[fid]["orbiting"] = false
		GameState.fleets[fid]["route"] = []


func _ensure_dest_marker(orb: Dictionary, dest: Vector3) -> void:
	var marker: MeshInstance3D = orb.get("dest_marker") as MeshInstance3D
	if marker == null or not is_instance_valid(marker):
		marker = MeshInstance3D.new()
		marker.name = "FleetDestination"
		var torus := TorusMesh.new()
		torus.inner_radius = 0.035
		torus.outer_radius = 0.055
		torus.rings = 12
		torus.ring_segments = 24
		var mat := StandardMaterial3D.new()
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.albedo_color = Color(0.55, 0.85, 0.95, 0.85)
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		mat.emission_enabled = true
		mat.emission = Color(0.35, 0.75, 0.95)
		mat.emission_energy_multiplier = 1.2
		marker.mesh = torus
		marker.material_override = mat
		# Torus lies in XY by default; rotate flat onto XZ disk.
		marker.rotation_degrees = Vector3(90, 0, 0)
		_bodies.add_child(marker)
		orb["dest_marker"] = marker
	marker.position = dest
	marker.visible = true


func _sync_fleet_world(orb: Dictionary, pos: Vector3, face_dir: Vector3, write_state: bool = true) -> void:
	pos.y = 0.0
	var root: Node3D = orb.root
	if is_instance_valid(root):
		root.position = pos
		if face_dir.length_squared() > 1e-12:
			var flat := Vector3(face_dir.x, 0.0, face_dir.z)
			if flat.length_squared() > 1e-12:
				root.look_at(pos + flat.normalized(), Vector3.UP)
	var pick_i: int = int(orb.pick_i)
	if pick_i >= 0 and pick_i < _pickables.size():
		_pickables[pick_i].center = pos
		_pickables[pick_i].meta.day = int(floor(GameState.day))
	var flag_i: int = int(orb.flag_i)
	if flag_i >= 0 and flag_i < _flags.size() and is_instance_valid(_flags[flag_i]):
		_flags[flag_i].world_pos = pos
	if write_state:
		var fid := String(orb.get("fleet_id", ""))
		if not fid.is_empty():
			GameState.update_fleet_system_pose(fid, _star_id, pos)


func _nearest_hyperlane_portal(pos: Vector3) -> Dictionary:
	var best: Dictionary = {}
	var best_d := 1e9
	for p in _hyperlane_portals:
		var c: Vector3 = p.center
		var r := float(p.get("radius", 0.5))
		var d := Vector3(pos.x, 0.0, pos.z).distance_to(Vector3(c.x, 0.0, c.z))
		if d <= r and d < best_d:
			best_d = d
			best = p
	return best


func _despawn_fleet_at(index: int, keep_selection: bool = false) -> void:
	if index < 0 or index >= _fleet_orbiters.size():
		return
	var orb: Dictionary = _fleet_orbiters[index]
	var root: Node3D = orb.get("root") as Node3D
	if is_instance_valid(root):
		root.queue_free()
	var marker: MeshInstance3D = orb.get("dest_marker") as MeshInstance3D
	if is_instance_valid(marker):
		marker.queue_free()
	var flag_i: int = int(orb.get("flag_i", -1))
	if flag_i >= 0 and flag_i < _flags.size() and is_instance_valid(_flags[flag_i]):
		_flags[flag_i].queue_free()
		_flags[flag_i] = null
	var pick_i: int = int(orb.get("pick_i", -1))
	if pick_i >= 0 and pick_i < _pickables.size():
		_pickables[pick_i] = {
			"kind": "gone",
			"center": Vector3(1e9, 1e9, 1e9),
			"radius": 0.0,
			"meta": {},
		}
	if _selected_fleet_i == index:
		_selected_fleet_i = -1
		if _panel_mode == "fleet":
			if keep_selection:
				_hide_panel_keep_selection()
			else:
				close_panel()
	elif _selected_fleet_i > index:
		_selected_fleet_i -= 1
	_fleet_orbiters.remove_at(index)
	# Refresh fleet_i indices on remaining metas.
	for i in _fleet_orbiters.size():
		var o: Dictionary = _fleet_orbiters[i]
		var m: Dictionary = o.get("meta", {})
		m["fleet_i"] = i


func _sync_fleets_from_state() -> void:
	## Mirror GameState poses / orders onto visuals. No local integration —
	## GameState owns in-system cruise + portal entry for all systems.
	var i := _fleet_orbiters.size() - 1
	while i >= 0:
		var orb: Dictionary = _fleet_orbiters[i]
		var fid := String(orb.get("fleet_id", ""))
		if fid.is_empty() or not GameState.has_fleet(fid):
			_despawn_fleet_at(i, true)
			i -= 1
			continue
		var f: Dictionary = GameState.fleets[fid]
		if String(f.get("status", "")) != "in_system" or int(f.get("system_id", -1)) != _star_id:
			_despawn_fleet_at(i, true)
			i -= 1
			continue
		orb["ordered"] = bool(f.get("ordered", false))
		orb["orbiting"] = bool(f.get("orbiting", orb.get("orbiting", true)))
		orb["pursue_fleet_id"] = String(f.get("pursue_fleet_id", ""))
		orb["engaged"] = bool(f.get("engaged", false))
		orb["destination"] = Vector3(
			float(f.get("dest_x", 0.0)), 0.0, float(f.get("dest_z", 0.0))
		)
		var meta: Dictionary = orb.get("meta", {})
		meta["ordered"] = orb["ordered"]
		meta["orbiting"] = orb["orbiting"]
		meta["pursue_fleet_id"] = orb["pursue_fleet_id"]
		meta["engaged"] = orb["engaged"]
		meta["dest_x"] = orb["destination"].x
		meta["dest_z"] = orb["destination"].z
		orb["meta"] = meta
		var marker: MeshInstance3D = orb.get("dest_marker") as MeshInstance3D
		if bool(orb["ordered"]) and not bool(orb["engaged"]):
			_ensure_dest_marker(orb, orb["destination"])
		elif is_instance_valid(marker):
			marker.visible = false
		# Ordered / pursue / engaged / non-orbiting: pose from GameState.
		# Kepler orbiters are positioned in _apply_orbits.
		var still_orbiting := bool(orb["orbiting"]) and not bool(orb["ordered"])
		if (
			bool(orb["ordered"])
			or bool(orb.get("stationary", false))
			or bool(orb.get("hostile", false))
			or bool(orb["engaged"])
			or not still_orbiting
		):
			var pos := Vector3(float(f.get("pos_x", 0.0)), 0.0, float(f.get("pos_z", 0.0)))
			var face := Vector3.ZERO
			if bool(orb["ordered"]):
				var dest: Vector3 = orb["destination"]
				face = Vector3(dest.x - pos.x, 0.0, dest.z - pos.z)
			_sync_fleet_world(orb, pos, face, false)
		_fleet_orbiters[i] = orb
		i -= 1


func _enter_hyperlane(fleet_index: int, portal: Dictionary) -> void:
	## Legacy helper — portal entry is authoritative in GameState; keep for
	## explicit UI jumps if needed. Prefer begin_hyperlane_transit via sim.
	var orb: Dictionary = _fleet_orbiters[fleet_index]
	var fid := String(orb.get("fleet_id", ""))
	var dest := int(portal.get("target_star", -1))
	if fid.is_empty() or dest < 0:
		return
	var route_dest := GameState.route_next_hyperlane_dest(fid)
	if route_dest >= 0 and route_dest != dest:
		return
	if not GameState.begin_hyperlane_transit(fid, _star_id, dest):
		return
	_despawn_fleet_at(fleet_index, true)

func _update_flag_positions() -> void:
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return
	var shown := 0
	var vp := get_viewport().get_visible_rect().size
	## Separate stacks by marker kind (fleets / planets / fields).
	var fleet_items: Array = []
	var planet_items: Array = []
	var field_items: Array = []
	for flag in _flags:
		if flag == null or not is_instance_valid(flag):
			continue
		var wp: Vector3 = flag.world_pos
		if cam.is_position_behind(wp):
			flag.visible = false
			continue
		var tip := cam.unproject_position(wp)
		if tip.x < -80.0 or tip.y < -80.0 or tip.x > vp.x + 80.0 or tip.y > vp.y + 80.0:
			flag.visible = false
			continue
		var item := {"flag": flag, "tip": tip}
		var marker := String(flag.meta.get("marker", "planet"))
		match marker:
			"fleet":
				fleet_items.append(item)
			"field", "asteroid":
				field_items.append(item)
			_:
				planet_items.append(item)
	PlanetFlag.apply_fleet_flag_layout(fleet_items, vp)
	PlanetFlag.apply_flag_layout(planet_items, vp)
	PlanetFlag.apply_flag_layout(field_items, vp)
	shown = fleet_items.size() + planet_items.size() + field_items.size()
	if _flag_hud:
		var total := 0
		for f2 in _flags:
			if f2 != null and is_instance_valid(f2):
				total += 1
		_flag_hud.text = "overlay: %d/%d flags" % [shown, total]


func _add_asteroid_field(af: Dictionary, mu: float, host: Vector3) -> void:
	var a := float(af.get("orbital_radius", 3.0))
	var half_w := 0.5 * float(af.get("radial_width", 0.5))
	var shape := String(af.get("shape", "ring"))
	var ang_w := float(af.get("angular_width", TAU))
	var phase0 := float(af.get("phase0", 0.0))
	var inc := float(af.get("inclination", 0.04))
	var field_seed := int(af.get("seed", 1))
	var n_dots := int(af.get("n_dots", 900))
	n_dots = clampi(n_dots, 80, 1800)
	var field_name := String(af.get("name", "Asteroids"))

	var rng := RandomNumberGenerator.new()
	rng.seed = field_seed
	var positions: PackedVector3Array = PackedVector3Array()
	positions.resize(n_dots)

	var ci := cos(inc)
	var si := sin(inc)
	var filled := 0
	var guard := 0
	while filled < n_dots and guard < n_dots * 40:
		guard += 1
		var r: float
		var th: float
		if shape == "ring":
			var u := rng.randf()
			var r_in := maxf(0.05, a - half_w)
			var r_out := a + half_w
			r = sqrt(u * (r_out * r_out - r_in * r_in) + r_in * r_in)
			th = rng.randf() * TAU
		else:
			var half_ang := 0.5 * ang_w
			var dth := rng.randfn(0.0, half_ang / 2.2)
			var dr := rng.randfn(0.0, half_w / 2.4)
			var gate := (dth / maxf(half_ang, 1e-6)) ** 2 + (dr / maxf(half_w, 1e-6)) ** 2
			if gate >= rng.randf_range(0.35, 1.15):
				continue
			th = phase0 + dth
			r = a + dr
		var zflat := rng.randfn(0.0, maxf(0.002 * a, 0.004))
		var x := r * cos(th)
		var y_plane := r * sin(th)
		positions[filled] = Vector3(x, zflat + y_plane * si, y_plane * ci)
		filled += 1

	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	var dot := SphereMesh.new()
	dot.radius = 0.012
	dot.height = 0.024
	dot.radial_segments = 4
	dot.rings = 2
	var dmat := StandardMaterial3D.new()
	dmat.vertex_color_use_as_albedo = true
	dmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	dot.material = dmat
	mm.mesh = dot
	mm.instance_count = filled
	var palette := [
		Color(0.59, 0.60, 0.62, 0.85),
		Color(0.51, 0.52, 0.54, 0.8),
		Color(0.67, 0.65, 0.61, 0.82),
		Color(0.57, 0.52, 0.46, 0.78),
		Color(0.47, 0.55, 0.61, 0.8),
	]
	var center_acc := Vector3.ZERO
	for i in filled:
		var p := host + positions[i]
		center_acc += p
		mm.set_instance_transform(i, Transform3D(Basis.IDENTITY, p))
		mm.set_instance_color(i, palette[rng.randi() % palette.size()])
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = mm
	mmi.name = field_name
	_bodies.add_child(mmi)

	var template := PackedVector3Array()
	template.resize(filled)
	for i in filled:
		template[i] = positions[i]

	var period := (TAU * sqrt((a * a * a) / mu)) if mu > 0.0 else 0.0
	var center := center_acc / float(maxi(filled, 1))
	var pick_i := _pickables.size()
	_pickables.append({
		"kind": "asteroid",
		"center": center,
		"radius": maxf(half_w + 0.4, 0.5),
		"meta": {
			"name": field_name,
			"shape": shape,
			"a": a,
			"radial_width": half_w * 2.0,
			"n_dots": filled,
			"period": period,
			"phase0": phase0,
			"host_star": int(af.get("host_star", 0)),
		},
	})
	_field_orbiters.append({
		"mmi": mmi,
		"template": template,
		"period": period,
		"inc": inc,
		"host": host,
		"phase0": phase0,
		"pick_i": pick_i,
	})


func _apply_orbits() -> void:
	## Positions at whole-day samples; linear blend for the fractional day.
	var day := GameState.day
	var d0 := floorf(day)
	var t := day - d0
	var d1 := d0 + 1.0

	for orb in _planet_orbiters:
		var a: float = float(orb.a)
		var phase0: float = float(orb.phase0)
		var inc: float = float(orb.inc)
		var period: float = float(orb.period)
		var orbit_mode := String(orb.get("orbit_mode", "kepler"))
		var half_period := float(orb.get("horseshoe_half_period_days", 30.0))
		var arc_frac := float(orb.get("horseshoe_arc_frac", (360.0 - 50.0) / 360.0))
		var host: Vector3 = orb.host
		var p0 := host + _planet_pos_at_day_ex(
			a, phase0, inc, period, d0, orbit_mode, half_period, arc_frac
		)
		var p1 := host + _planet_pos_at_day_ex(
			a, phase0, inc, period, d1, orbit_mode, half_period, arc_frac
		)
		var pos := p0.lerp(p1, t)
		var mi: MeshInstance3D = orb.mi
		if is_instance_valid(mi):
			mi.position = pos
		var pick_i: int = int(orb.pick_i)
		if pick_i >= 0 and pick_i < _pickables.size():
			_pickables[pick_i].center = pos
			_pickables[pick_i].meta.day = int(d0)
		var flag_i: int = int(orb.flag_i)
		if flag_i >= 0 and flag_i < _flags.size() and is_instance_valid(_flags[flag_i]):
			_flags[flag_i].world_pos = pos

	for orb in _fleet_orbiters:
		# Under orders / free-disk: GameState owns pose (_sync_fleets_from_state).
		# Stationary / hostile / engaged / left-orbit: hold world pose
		# (post-battle survivors must not snap back to phase0 spawn).
		var fid_hold := String(orb.get("fleet_id", ""))
		var still_orbiting := bool(orb.get("orbiting", true))
		if GameState.has_fleet(fid_hold):
			still_orbiting = bool(GameState.fleets[fid_hold].get("orbiting", still_orbiting))
		var ordered_hold := bool(orb.get("ordered", false))
		if GameState.has_fleet(fid_hold):
			ordered_hold = bool(GameState.fleets[fid_hold].get("ordered", ordered_hold))
		if (
			ordered_hold
			or bool(orb.get("stationary", false))
			or bool(orb.get("hostile", false))
			or bool(orb.get("engaged", false))
			or GameState.is_fleet_engaged(fid_hold)
			or not still_orbiting
		):
			# Do not write GameState — ordered poses come from sim; hold visuals
			# until _sync_fleets_from_state refreshes them.
			continue
		var a: float = float(orb.a)
		var phase0: float = float(orb.phase0)
		var inc: float = float(orb.inc)
		var period: float = float(orb.period)
		var host: Vector3 = orb.host
		var p0 := host + _planet_pos_at_day(a, phase0, inc, period, d0)
		var p1 := host + _planet_pos_at_day(a, phase0, inc, period, d1)
		p0.y = 0.0
		p1.y = 0.0
		var pos := p0.lerp(p1, t)
		pos.y = 0.0
		var tang := p1 - p0
		_sync_fleet_world(orb, pos, tang)

	for orb in _field_orbiters:
		var mmi: MultiMeshInstance3D = orb.mmi
		if not is_instance_valid(mmi) or mmi.multimesh == null:
			continue
		var template: PackedVector3Array = orb.template
		var period: float = float(orb.period)
		var inc: float = float(orb.inc)
		var host: Vector3 = orb.host
		var mm := mmi.multimesh
		var n := mini(mm.instance_count, template.size())
		var center_acc := Vector3.ZERO
		for i in n:
			var a0 := host + _rotate_field_point(template[i], d0, period, inc)
			var a1 := host + _rotate_field_point(template[i], d1, period, inc)
			var p := a0.lerp(a1, t)
			mm.set_instance_transform(i, Transform3D(Basis.IDENTITY, p))
			center_acc += p
		var pick_i: int = int(orb.pick_i)
		if pick_i >= 0 and pick_i < _pickables.size() and n > 0:
			_pickables[pick_i].center = center_acc / float(n)


func _horseshoe_phase(day: float, phase0: float, half_period: float, arc_frac: float) -> float:
	## Travel arc_frac of a circle one way over half_period days, then reverse.
	var half := maxf(half_period, 0.001)
	var arc := TAU * arc_frac
	var cycle := 2.0 * half
	var t := fposmod(day, cycle)
	if t < half:
		var u := t / half
		return phase0 + u * arc
	var u2 := (t - half) / half
	return phase0 + (1.0 - u2) * arc


func _planet_pos_at_day(a: float, phase0: float, inc: float, period: float, day: float) -> Vector3:
	return _planet_pos_at_day_ex(a, phase0, inc, period, day, "kepler", 30.0, 0.9)


func _planet_pos_at_day_ex(
	a: float,
	phase0: float,
	inc: float,
	period: float,
	day: float,
	orbit_mode: String,
	half_period: float,
	arc_frac: float,
) -> Vector3:
	var phase := phase0
	if orbit_mode == "horseshoe":
		phase = _horseshoe_phase(day, phase0, half_period, arc_frac)
	elif period > 1e-9:
		phase += TAU * (day / period)
	return _orbit_point(a, phase, inc)


func _rotate_field_point(p0: Vector3, day: float, period: float, inc: float) -> Vector3:
	## Rigid mean-motion advance (Godot XZ disk; Y = Python Z).
	if period <= 1e-9:
		return p0
	var dtheta := TAU * (day / period)
	var c := cos(dtheta)
	var s := sin(dtheta)
	var ci := cos(inc)
	var si := sin(inc)
	var gx0 := p0.x
	var gy0 := p0.y
	var gz0 := p0.z
	if absf(ci) < 1e-6:
		return Vector3(c * gx0 - s * gz0, gy0, s * gx0 + c * gz0)
	var y_plane := gz0 / ci
	var z_flat := gy0 - y_plane * si
	var gx := c * gx0 - s * y_plane
	var y_p := s * gx0 + c * y_plane
	return Vector3(gx, z_flat + y_p * si, y_p * ci)


func _add_hyperlane(hl: Dictionary) -> void:
	var portal_name := String(hl.get("name", "Hyperlane Entry"))
	var target_label := String(hl.get("target_label", "System"))
	var target_star := int(hl.get("target_star", -1))
	var cx := float(hl.get("x", 0.0))
	var cy := float(hl.get("y", 0.0))
	var ox := float(hl.get("out_x", 1.0))
	var oy := float(hl.get("out_y", 0.0))
	var ah := float(hl.get("along_half", 0.35))
	var ch := float(hl.get("across_half", 0.55))
	var center := Vector3(cx, 0.0, cy)
	var along := Vector3(ox, 0.0, oy)
	if along.length_squared() < 1e-8:
		along = Vector3.RIGHT
	else:
		along = along.normalized()
	var across := Vector3(-along.z, 0.0, along.x)

	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var fill := Color(0.27, 0.75, 0.82, 0.28)
	var n := 48
	for i in n:
		var t0 := TAU * float(i) / float(n)
		var t1 := TAU * float(i + 1) / float(n)
		var p0 := center + along * (ah * cos(t0)) + across * (ch * sin(t0))
		var p1 := center + along * (ah * cos(t1)) + across * (ch * sin(t1))
		st.set_color(fill)
		st.add_vertex(center)
		st.set_color(fill)
		st.add_vertex(p0)
		st.set_color(fill)
		st.add_vertex(p1)
	var fill_mi := MeshInstance3D.new()
	fill_mi.mesh = st.commit()
	var fmat := StandardMaterial3D.new()
	fmat.vertex_color_use_as_albedo = true
	fmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	fmat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	fmat.cull_mode = BaseMaterial3D.CULL_DISABLED
	fill_mi.material_override = fmat
	fill_mi.name = portal_name
	_bodies.add_child(fill_mi)

	var ost := SurfaceTool.new()
	ost.begin(Mesh.PRIMITIVE_LINE_STRIP)
	var ocol := Color(0.43, 0.88, 0.94, 0.95)
	for i in n + 1:
		var t := TAU * float(i) / float(n)
		var p := center + along * (ah * cos(t)) + across * (ch * sin(t))
		ost.set_color(ocol)
		ost.add_vertex(p)
	var outline := MeshInstance3D.new()
	outline.mesh = ost.commit()
	var omat := StandardMaterial3D.new()
	omat.vertex_color_use_as_albedo = true
	omat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	outline.material_override = omat
	_bodies.add_child(outline)

	var shaft0 := center + along * (ah * 1.05)
	var tip := center + along * (ah * 2.35)
	var wing := maxf(0.12, 0.55 * ch)
	var left := tip - along * (0.85 * wing) + across * wing
	var right := tip - along * (0.85 * wing) - across * wing
	var ast := SurfaceTool.new()
	ast.begin(Mesh.PRIMITIVE_LINES)
	var acol := Color(0.47, 0.90, 0.96, 0.95)
	ast.set_color(acol)
	ast.add_vertex(shaft0)
	ast.set_color(acol)
	ast.add_vertex(tip)
	ast.set_color(acol)
	ast.add_vertex(tip)
	ast.set_color(acol)
	ast.add_vertex(left)
	ast.set_color(acol)
	ast.add_vertex(tip)
	ast.set_color(acol)
	ast.add_vertex(right)
	var arrow := MeshInstance3D.new()
	arrow.mesh = ast.commit()
	var amat := StandardMaterial3D.new()
	amat.vertex_color_use_as_albedo = true
	amat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	arrow.material_override = amat
	_bodies.add_child(arrow)

	_pickables.append({
		"kind": "hyperlane",
		"center": center,
		"radius": maxf(ah, ch) + 0.15,
		"meta": {
			"name": portal_name,
			"target_label": target_label,
			"target_star": target_star,
			"radius_au": sqrt(cx * cx + cy * cy),
		},
	})
	_hyperlane_portals.append({
		"center": center,
		"radius": maxf(ah, ch) + 0.25,
		"target_star": target_star,
		"target_label": target_label,
		"name": portal_name,
	})


func _try_pick(screen_pos: Vector2) -> void:
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return
	var from := cam.project_ray_origin(screen_pos)
	var dir := cam.project_ray_normal(screen_pos)
	var best_i := -1
	var best_score := 1e9
	for i in _pickables.size():
		var item: Dictionary = _pickables[i]
		if String(item.get("kind", "")) == "gone":
			continue
		var center: Vector3 = item.center
		var radius: float = float(item.radius)
		var w := center - from
		var proj := w.dot(dir)
		if proj < 0.0:
			continue
		var closest := from + dir * proj
		var dist := closest.distance_to(center)
		if dist > radius:
			continue
		if dist < best_score:
			best_score = dist
			best_i = i
	if best_i < 0:
		# Empty space: clear selection / close info panel.
		if _panel_open:
			close_panel()
		return
	_show_info(_pickables[best_i])


func _show_info(item: Dictionary) -> void:
	var meta: Dictionary = item.meta
	match String(item.kind):
		"planet":
			_open_planet_panel(meta)
		"fleet":
			_open_fleet_panel(meta)
		"asteroid":
			_open_asteroid_panel(meta)
		"hyperlane":
			if _info:
				_info.text = "[b]%s[/b]\nHyperlane entry\n→ %s (#%d)\nr = %.2f AU\n(jumping…)" % [
					meta.name, meta.target_label, meta.target_star, meta.radius_au
				]
			var dest := int(meta.get("target_star", -1))
			if dest >= 0:
				GameState.enter_system(dest)
		_:
			if _info:
				_info.text = str(meta)


func _kind_label(kind: String) -> String:
	match kind:
		"goldilocks":
			return "Goldilocks world"
		"rocky":
			return "Rocky world"
		"gas_giant":
			return "Gas giant"
		"neverdark":
			return "Neverdark homeworld (Brightstep)"
		_:
			return kind.capitalize()


func _true_anomaly_rad(phase0: float, period: float, day: float) -> float:
	## Circular orbits: true anomaly ν equals mean anomaly (phase from periapsis/epoch).
	var nu := phase0
	if period > 1e-9:
		nu += TAU * (day / period)
	return fposmod(nu, TAU)


func _format_true_anomaly(meta: Dictionary) -> String:
	var mode := String(meta.get("orbit_mode", ""))
	var nu: float
	if mode == "horseshoe":
		nu = _horseshoe_phase(
			GameState.day,
			float(meta.get("phase0", 0.0)),
			float(meta.get("horseshoe_half_period_days", 30.0)),
			float(meta.get("horseshoe_arc_frac", (360.0 - 50.0) / 360.0)),
		)
	else:
		nu = _true_anomaly_rad(
			float(meta.get("phase0", 0.0)),
			float(meta.get("period", 0.0)),
			GameState.day,
		)
	return "%.2f°  (%.4f rad)" % [rad_to_deg(fposmod(nu, TAU)), fposmod(nu, TAU)]


func _open_planet_panel(meta: Dictionary) -> void:
	if _panel == null:
		return
	_panel_open = true
	_panel_mode = "planet"
	_panel_meta = meta
	_panel.visible = true
	if _panel_title:
		_panel_title.text = String(meta.get("name", "Planet"))
	if _panel_kind:
		_panel_kind.text = _kind_label(String(meta.get("kind", "")))
	var ca: Color = meta.get("color_a", Color(0.56, 0.83, 0.66))
	var cb: Color = meta.get("color_b", Color(0.12, 0.24, 0.16))
	if _panel_preview:
		_panel_preview.texture = PlanetFlag.make_checkered_texture(128, ca, cb)
	_refresh_planet_stats(meta)
	if _info:
		_info.visible = false


func _refresh_planet_stats(meta: Dictionary) -> void:
	if _panel_stats == null:
		return
	var orbit_line := "Kepler (host star)"
	if String(meta.get("orbit_mode", "")) == "horseshoe":
		var half := float(meta.get("horseshoe_half_period_days", 30.0))
		var frac := float(meta.get("horseshoe_arc_frac", (360.0 - 50.0) / 360.0))
		var gap := float(meta.get("horseshoe_gap_deg", (1.0 - frac) * 360.0))
		orbit_line = (
			"Horseshoe about 3-star barycenter — %.0f° gap toward tertiary, reverse every %.0f days"
			% [gap, half]
		)
	elif int(meta.get("host_star", 0)) < 0:
		orbit_line = "Barycentric"
	var text := (
		"[color=#9eb6d8]Semi-major axis[/color]  %.2f AU\n"
		+ "[color=#9eb6d8]Orbit[/color]  %s\n"
		+ "[color=#9eb6d8]Size radius[/color]  %.1f\n"
		+ "[color=#9eb6d8]Orbital period[/color]  %.1f days\n"
		+ "[color=#9eb6d8]True anomaly ν[/color]  %s\n"
		+ "[color=#9eb6d8]Sample day[/color]  %s"
	) % [
		float(meta.get("a", 0.0)),
		orbit_line,
		float(meta.get("size", 1.0)),
		float(meta.get("period", 0.0)),
		_format_true_anomaly(meta),
		GameState.day_label_text(),
	]
	var climate = meta.get("climate", {})
	if typeof(climate) == TYPE_DICTIONARY and not climate.is_empty():
		text += "\n\n[b]Climate (Neverdark)[/b]"
		text += "\n[color=#9eb6d8]Equator[/color]  %s" % String(climate.get("equator", "—"))
		text += "\n[color=#9eb6d8]Poles[/color]  %s" % String(climate.get("poles", "—"))
		text += "\n[color=#9eb6d8]Mid-bands[/color]  %s" % String(climate.get("mid_bands", "—"))
		text += "\n[color=#9eb6d8]Binary-facing pole[/color]  %s" % String(climate.get("binary_facing_pole", "—"))
		text += "\n[color=#9eb6d8]Far pole[/color]  %s" % String(climate.get("far_pole", "—"))
		text += "\n[color=#9eb6d8]Pole flip[/color]  %s" % String(climate.get("pole_flip", "—"))
	var notes := String(meta.get("notes", ""))
	if notes != "":
		text += "\n\n%s" % notes
	_panel_stats.text = text
	if _panel_empty:
		if String(meta.get("kind", "")) == "neverdark":
			_panel_empty.text = "Long-day horseshoe world — poles not yet flipped."
		else:
			_panel_empty.text = "Further planetary data will appear here."


func _open_asteroid_panel(meta: Dictionary) -> void:
	if _panel == null:
		return
	_panel_open = true
	_panel_mode = "asteroid"
	_panel_meta = meta
	_panel.visible = true
	if _panel_title:
		_panel_title.text = String(meta.get("name", "Asteroids"))
	if _panel_kind:
		var shape := String(meta.get("shape", "ring"))
		_panel_kind.text = "Asteroid ring" if shape == "ring" else "Asteroid camp"
	if _panel_preview:
		_panel_preview.texture = null
	_refresh_asteroid_stats(meta)
	if _panel_empty:
		_panel_empty.text = "Field stipple — no flag marker."
	if _info:
		_info.visible = false


func _refresh_asteroid_stats(meta: Dictionary) -> void:
	if _panel_stats == null:
		return
	_panel_stats.text = (
		"[color=#9eb6d8]Semi-major axis[/color]  %.2f AU\n"
		+ "[color=#9eb6d8]Radial width[/color]  %.2f AU\n"
		+ "[color=#9eb6d8]Dots[/color]  %d\n"
		+ "[color=#9eb6d8]Orbital period[/color]  %.1f days\n"
		+ "[color=#9eb6d8]True anomaly ν[/color]  %s\n"
		+ "[color=#9eb6d8]Sample day[/color]  %s"
	) % [
		float(meta.get("a", 0.0)),
		float(meta.get("radial_width", 0.0)),
		int(meta.get("n_dots", 0)),
		float(meta.get("period", 0.0)),
		_format_true_anomaly(meta),
		GameState.day_label_text(),
	]


func _open_fleet_panel(meta: Dictionary) -> void:
	if _panel == null:
		return
	var target_i := int(meta.get("fleet_i", -1))
	_panel_open = true
	_panel_mode = "fleet"
	_panel_meta = meta
	_selected_fleet_i = target_i
	GameState.select_fleet(String(meta.get("fleet_id", "")))
	_panel.visible = true
	if _panel_title:
		_panel_title.text = String(meta.get("name", "Fleet"))
	if _panel_kind:
		var faction := String(meta.get("faction", ""))
		var hostile := bool(meta.get("hostile", false))
		var head := faction if not faction.is_empty() else "Fleet"
		if hostile:
			_panel_kind.text = "%s · hostile · %d ships" % [head, int(meta.get("ship_count", 0))]
		else:
			_panel_kind.text = "%s · %d ships" % [head, int(meta.get("ship_count", 0))]
	var ca: Color = meta.get("color_a", Color(0.72, 0.82, 0.92))
	var cb: Color = meta.get("color_b", Color(0.12, 0.18, 0.28))
	if _panel_preview:
		_panel_preview.texture = PlanetFlag.make_fleet_texture(128, ca, cb)
	_refresh_fleet_stats(meta)
	if _panel_empty:
		if bool(meta.get("hostile", false)):
			_panel_empty.text = "Inspect only — contents viewable; this fleet cannot be ordered or moved."
		elif bool(meta.get("engaged", false)):
			_panel_empty.text = "Engaged in battle — destinations locked until resolved."
		else:
			_panel_empty.text = (
				"RMB disk destination · RMB portal to path to that star · RMB fleet to pursue"
				+ " · Reach exit portal to jump (28-day transit; 28-day entry cooldown)"
				+ " · LMB empty deselects."
			)
	if _info:
		_info.visible = false


func _refresh_fleet_stats(meta: Dictionary) -> void:
	if _panel_stats == null:
		return
	var ship_lines := ""
	var templates = meta.get("ship_templates", [])
	if typeof(templates) == TYPE_ARRAY and not templates.is_empty():
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
	else:
		var ships = meta.get("ships", [])
		if typeof(ships) == TYPE_ARRAY:
			for s in ships:
				ship_lines += "\n  · %s" % String(s)
	var dest_line := "—  (RMB to set)"
	var eta_line := "—"
	var cooldown_line := ""
	var fleet_i := int(meta.get("fleet_i", -1))
	var engaged := bool(meta.get("engaged", false))
	var hostile := bool(meta.get("hostile", false))
	var pursue_id := String(meta.get("pursue_fleet_id", ""))
	var fid_stats := String(meta.get("fleet_id", ""))
	if GameState.has_fleet(fid_stats):
		pursue_id = String(GameState.fleets[fid_stats].get("pursue_fleet_id", pursue_id))
		engaged = bool(GameState.fleets[fid_stats].get("engaged", engaged))
		var cd_left := GameState.hyperlane_entry_cooldown_left(fid_stats)
		if cd_left > 0.0:
			cooldown_line = (
				"[color=#9eb6d8]Hyperlane ready[/color]  in %.0f days\n" % ceilf(cd_left)
			)
	if hostile:
		dest_line = "stationary (hostile)"
		eta_line = "—"
	elif engaged:
		dest_line = "locked (battle)"
		eta_line = "—"
		var bid := ""
		if not fid_stats.is_empty():
			bid = GameState.fleet_battle_id(fid_stats)
		if not bid.is_empty() and GameState.battles.has(bid):
			var b: Dictionary = GameState.battles[bid]
			eta_line = "round %d" % int(b.get("round", 0))
	elif not pursue_id.is_empty():
		var tname := pursue_id
		if GameState.has_fleet(pursue_id):
			tname = String(GameState.fleets[pursue_id].get("name", pursue_id))
		dest_line = "Pursuing %s" % tname
		if fleet_i >= 0 and fleet_i < _fleet_orbiters.size():
			var root_p: Node3D = _fleet_orbiters[fleet_i].root
			var dest_p: Vector3 = _fleet_orbiters[fleet_i].get(
				"destination", Vector3(float(meta.get("dest_x", 0.0)), 0.0, float(meta.get("dest_z", 0.0)))
			)
			if is_instance_valid(root_p):
				var dist_p := Vector3(root_p.position.x, 0.0, root_p.position.z).distance_to(
					Vector3(dest_p.x, 0.0, dest_p.z)
				)
				if dist_p <= FLEET_ARRIVE_EPS_AU:
					eta_line = "at target"
				elif _fleet_speed_au_per_day > 1e-9:
					eta_line = "%.1f days (closing)" % (dist_p / _fleet_speed_au_per_day)
	elif bool(meta.get("ordered", false)):
		var route_n := 0
		if GameState.has_fleet(fid_stats):
			route_n = GameState.fleet_route(fid_stats).size()
		if route_n > 0:
			dest_line = "Route · (%.2f, %.2f) AU · %d hops left" % [
				float(meta.get("dest_x", 0.0)), float(meta.get("dest_z", 0.0)), route_n
			]
		else:
			dest_line = "(%.2f, %.2f) AU" % [float(meta.get("dest_x", 0.0)), float(meta.get("dest_z", 0.0))]
		if fleet_i >= 0 and fleet_i < _fleet_orbiters.size():
			var root: Node3D = _fleet_orbiters[fleet_i].root
			if is_instance_valid(root):
				var dest := Vector3(float(meta.get("dest_x", 0.0)), 0.0, float(meta.get("dest_z", 0.0)))
				var dist := Vector3(root.position.x, 0.0, root.position.z).distance_to(dest)
				if dist <= FLEET_ARRIVE_EPS_AU:
					eta_line = "arrived"
				elif _fleet_speed_au_per_day > 1e-9:
					eta_line = "%.1f days" % (dist / _fleet_speed_au_per_day)
	_panel_stats.text = (
		"[color=#9eb6d8]Ships[/color]  %d%s\n"
		+ "[color=#9eb6d8]Cruise speed[/color]  %.3f AU/day\n"
		+ "  (diameter %.1f AU ÷ %d days)\n"
		+ "[color=#9eb6d8]Destination[/color]  %s\n"
		+ "%s"
		+ "[color=#9eb6d8]ETA[/color]  %s\n"
		+ "[color=#9eb6d8]Sample day[/color]  %s"
	) % [
		int(meta.get("ship_count", 0)),
		ship_lines,
		_fleet_speed_au_per_day,
		2.0 * _system_edge_au,
		int(FLEET_CROSSING_DAYS),
		dest_line,
		cooldown_line,
		eta_line,
		GameState.day_label_text(),
	]


func _refresh_battle_hud() -> void:
	if _info == null or _star_id < 0:
		return
	var line := GameState.battle_hud_line(_star_id)
	if line.is_empty():
		return
	# Keep battle status visible on the system HUD tip line.
	if not _panel_open:
		_info.visible = true
		_info.text = line


func close_panel() -> void:
	## Explicit deselect (Esc / LMB empty / X): clear GameState selection.
	var was_fleet := _panel_mode == "fleet"
	var was_fid := String(_panel_meta.get("fleet_id", ""))
	_panel_open = false
	_panel_meta = {}
	_panel_mode = ""
	_selected_fleet_i = -1
	_close_panel_ui()
	if was_fleet and not was_fid.is_empty() and GameState.selected_fleet_id == was_fid:
		GameState.clear_fleet_selection()
	if _info:
		_info.visible = true
	_refresh_battle_hud()


func _hide_panel_keep_selection() -> void:
	## Close panel UI without clearing GameState.selected_fleet_id.
	_panel_open = false
	_panel_meta = {}
	_panel_mode = ""
	_selected_fleet_i = -1
	_close_panel_ui()
	if _info:
		_info.visible = true
	_refresh_battle_hud()


func _close_panel_ui() -> void:
	if _panel:
		_panel.visible = false
