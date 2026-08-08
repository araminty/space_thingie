extends Node3D
## Solar-system view: stars, orbits, planets, asteroid fields, hyperlane ovals,
## and planet zoom-inset flags (hockey-stick leaders).

const MU_SOLAR := 0.00029591220828559115  # AU^3 / day^2

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
var _panel_is_planet := false
## Planet orbiters: {mi, a, phase0, inc, period, pick_i, flag_i, meta}
var _planet_orbiters: Array = []
## Field orbiters: {mmi, template, period, inc, host, pick_i}
var _field_orbiters: Array = []
## Host star positions in Godot space (XZ disk).
var _host_positions: Array = []
var _host_mus: Array = []


func _ready() -> void:
	visible = false
	if _back:
		_back.pressed.connect(_on_back)
	if _panel_close:
		_panel_close.pressed.connect(close_panel)
	_close_panel_ui()
	GameState.entered_system.connect(_on_enter)
	GameState.returned_to_galaxy.connect(_on_leave)
	GameState.day_changed.connect(_on_day_changed)
	_data.load_all()


func _on_enter(star_id: int) -> void:
	_star_id = star_id
	visible = true
	_build(star_id)


func _on_leave() -> void:
	visible = false
	close_panel()
	_clear_bodies()
	_star_id = -1


func _on_back() -> void:
	GameState.return_to_galaxy()


func _on_day_changed(_day: float) -> void:
	if visible and is_visible_in_tree():
		_apply_orbits()
		if _panel_open and not _panel_meta.is_empty():
			if _panel_is_planet:
				_refresh_planet_stats(_panel_meta)
			else:
				_refresh_asteroid_stats(_panel_meta)


func _process(_delta: float) -> void:
	if not visible or not is_visible_in_tree():
		return
	_update_flag_positions()


func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		if _panel_open:
			close_panel()
		else:
			GameState.return_to_galaxy()
		get_viewport().set_input_as_handled()
		return
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
			_try_pick(mb.position)
			get_viewport().set_input_as_handled()


func _clear_bodies() -> void:
	for c in _bodies.get_children():
		c.queue_free()
	_pickables.clear()
	_planet_orbiters.clear()
	_field_orbiters.clear()
	_host_positions.clear()
	_host_mus.clear()
	for f in _flags:
		if is_instance_valid(f):
			f.queue_free()
	_flags.clear()
	if _flag_hud:
		_flag_hud.text = ""


func _build(star_id: int) -> void:
	_clear_bodies()
	close_panel()
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

	_apply_orbits()
	if _camera_rig and _camera_rig.has_method("set_focus"):
		_camera_rig.call_deferred("set_focus", Vector3.ZERO, extent * 2.2)


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
	var name := String(p.get("name", "World"))
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
	orbit_mi.name = "%s_orbit" % name
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
	pmi.name = name
	_bodies.add_child(pmi)

	var meta := {
		"name": name,
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
	flag.opened.connect(func() -> void: _open_planet_panel(meta))
	_flags.append(flag)


func _update_flag_positions() -> void:
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return
	var shown := 0
	var vp := get_viewport().get_visible_rect().size
	for flag in _flags:
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
		flag.place_at_screen(tip)
		shown += 1
	if _flag_hud:
		_flag_hud.text = "overlay: %d/%d flags" % [shown, _flags.size()]


func _add_asteroid_field(af: Dictionary, mu: float, host: Vector3) -> void:
	var a := float(af.get("orbital_radius", 3.0))
	var half_w := 0.5 * float(af.get("radial_width", 0.5))
	var shape := String(af.get("shape", "ring"))
	var ang_w := float(af.get("angular_width", TAU))
	var phase0 := float(af.get("phase0", 0.0))
	var inc := float(af.get("inclination", 0.04))
	var seed := int(af.get("seed", 1))
	var n_dots := int(af.get("n_dots", 900))
	n_dots = clampi(n_dots, 80, 1800)
	var name := String(af.get("name", "Asteroids"))

	var rng := RandomNumberGenerator.new()
	rng.seed = seed
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
	mmi.name = name
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
			"name": name,
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
	var name := String(hl.get("name", "Hyperlane Entry"))
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
	fill_mi.name = name
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
			"name": name,
			"target_label": target_label,
			"target_star": target_star,
			"radius_au": sqrt(cx * cx + cy * cy),
		},
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
		return
	_show_info(_pickables[best_i])


func _show_info(item: Dictionary) -> void:
	var meta: Dictionary = item.meta
	match String(item.kind):
		"planet":
			_open_planet_panel(meta)
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
	_panel_is_planet = true
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
	_panel_is_planet = false
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


func close_panel() -> void:
	_panel_open = false
	_panel_meta = {}
	_close_panel_ui()
	if _info:
		_info.visible = true


func _close_panel_ui() -> void:
	if _panel:
		_panel.visible = false
