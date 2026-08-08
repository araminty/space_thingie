extends Node3D
## Builds the galaxy star MultiMesh + lane line mesh from exported JSON.

@onready var _stars_mmi: MultiMeshInstance3D = $Stars
@onready var _lanes_mi: MeshInstance3D = $Lanes
@onready var _camera_rig: Node3D = $"../OrbitCamera"
@onready var _hud: Label = $"../../UI/GalaxyHud"

var _data := GalaxyData.new()
var _star_positions: PackedVector3Array = PackedVector3Array()
var _pick_enabled := true
var _labels_root: Node3D
## Galaxy camera pose captured when entering a system (restored on return).
var _saved_camera: Dictionary = {}


func _ready() -> void:
	var err := _data.load_all()
	if err != OK:
		if _hud:
			_hud.text = "Missing galaxy export.\nRun: .venv/bin/python export_godot.py"
		return
	_labels_root = Node3D.new()
	_labels_root.name = "HomeworldLabels"
	add_child(_labels_root)
	_build_lanes()
	_build_stars()
	if _camera_rig and _camera_rig.has_method("set_focus"):
		_camera_rig.call_deferred("set_focus", _data.map_center(), _data.region_size())
	if _hud:
		var named := 0
		for s in _data.stars:
			if bool(s.get("homeworld", false)):
				named += 1
		_hud.text = (
			"Stars %d · Lanes %d · Homeworlds %d · LMB open · ▶/Space time · WASD/RMB/Wheel"
			% [_data.stars.size(), _data.lanes.size(), named]
		)
	GameState.entered_system.connect(_on_enter_system)
	GameState.returned_to_galaxy.connect(_on_return_galaxy)


func _on_enter_system(_star_id: int) -> void:
	_pick_enabled = false
	if _camera_rig and _camera_rig.has_method("snapshot"):
		_saved_camera = _camera_rig.snapshot()
	visible = false
	if _camera_rig:
		_camera_rig.visible = false


func _on_return_galaxy() -> void:
	_pick_enabled = true
	visible = true
	if _camera_rig:
		_camera_rig.visible = true
		# Keep last galaxy pan/zoom/orbit — do not recenter on the map.
		if not _saved_camera.is_empty() and _camera_rig.has_method("restore"):
			_camera_rig.restore(_saved_camera)


func _unhandled_input(event: InputEvent) -> void:
	if not _pick_enabled or not visible:
		return
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
			var id := _pick_star(mb.position)
			if id >= 0:
				GameState.enter_system(id)
				get_viewport().set_input_as_handled()


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
	sphere.radius = 0.0045
	sphere.height = 0.009
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
	for s in _data.stars:
		instance_count += clampi(int(s.get("multiplicity", 1)), 1, 3)

	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	mm.mesh = sphere
	mm.instance_count = instance_count
	_star_positions.resize(n)

	var inst := 0
	for i in n:
		var s: Dictionary = _data.stars[i]
		var pos := Vector3(float(s.x), float(s.z), float(s.y))
		_star_positions[i] = pos
		var scale := 1.0
		var label := String(s.get("label", ""))
		var special := String(s.get("special", ""))
		var is_homeworld := bool(s.get("homeworld", false))
		var mult := clampi(int(s.get("multiplicity", 1)), 1, 3)
		if label.begins_with("ancient") and label.contains("core"):
			scale = 1.55
		elif special == "sol":
			scale = 1.9
		elif special == "neverdark" or label.begins_with("Neverdark"):
			scale = 1.85
		elif is_homeworld:
			scale = 1.55
		elif label == "treasure":
			scale = 1.7
		elif label == "ring network":
			scale = 1.2
		elif label.begins_with("locked frontier"):
			scale = 0.75
		elif label == "galactic core":
			scale = 0.7
		elif label == "locked wall" or label == "outer rim":
			scale = 0.75
		var col := _color_from_entry(s)
		var sep := 0.0038 * scale
		var offsets := _multiplicity_offsets(mult, sep, int(s.get("id", i)))
		var comp_scale := scale if mult == 1 else scale * 0.78
		for oi in offsets.size():
			var o: Vector3 = offsets[oi]
			# Primary component slightly larger in multi-star glyphs.
			var s_i := comp_scale * (1.12 if oi == 0 and mult > 1 else 1.0)
			var xf := Transform3D(Basis.IDENTITY.scaled(Vector3.ONE * s_i), pos + o)
			mm.set_instance_transform(inst, xf)
			mm.set_instance_color(inst, col)
			inst += 1

		if is_homeworld:
			var text := String(s.get("map_label", label))
			if text.is_empty():
				text = label
			var lbl := Label3D.new()
			lbl.text = text
			lbl.billboard = BaseMaterial3D.BILLBOARD_ENABLED
			lbl.font_size = 36
			lbl.pixel_size = 0.00055
			lbl.outline_size = 8
			lbl.modulate = Color(0.95, 0.97, 1.0, 0.95)
			lbl.position = pos + Vector3(0.0, 0.011, 0.0)
			lbl.no_depth_test = true
			_labels_root.add_child(lbl)

	_stars_mmi.multimesh = mm


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
		var col := _color_from_entry(lane)
		if String(lane.get("paint", "")) == "black":
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
