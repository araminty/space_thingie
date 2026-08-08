extends Node3D
## Orbit / pan / zoom camera for galaxy and system maps.
## Default (system): RMB orbit · MMB / WASD pan · Wheel zoom
## Galaxy mode: set pan_on_rmb + rotate_on_mmb → RMB pan · MMB orbit · Wheel zoom
## Uses _unhandled_input so fleet/star RMB orders (handled in _input) win first.

@export var target: Vector3 = Vector3(0.86, 0.0, 0.86)
@export var distance: float = 2.4
@export var min_distance: float = 0.35
@export var max_distance: float = 6.0
@export var yaw_deg: float = -90.0
@export var pitch_deg: float = 72.0
@export var orbit_sensitivity: float = 0.25
@export var pan_sensitivity: float = 0.0025
@export var zoom_sensitivity: float = 0.12
## World units per second at distance≈1; scales with current zoom.
@export var wasd_speed: float = 0.85
## If true, WASD stays on the XZ plane (galaxy/system disk). If false, uses camera up.
@export var pan_on_disk_plane: bool = true
## Galaxy: RMB drag pans. System keeps false (RMB turntable).
@export var pan_on_rmb: bool = false
## Galaxy: MMB drag turntables. System keeps false (MMB pan).
@export var rotate_on_mmb: bool = false

var _camera: Camera3D
var _orbiting := false
var _panning := false


func _ready() -> void:
	_camera = get_node_or_null("Camera3D") as Camera3D
	_apply()


func set_focus(center: Vector3, region: float) -> void:
	target = center
	distance = clampf(region * 1.35, min_distance, max_distance)
	if _camera == null:
		call_deferred("_apply")
	else:
		_apply()


func set_view(center: Vector3, region: float, yaw: float, pitch: float) -> void:
	yaw_deg = yaw
	pitch_deg = clampf(pitch, 8.0, 89.0)
	set_focus(center, region)


func snapshot() -> Dictionary:
	return {
		"target": target,
		"distance": distance,
		"yaw_deg": yaw_deg,
		"pitch_deg": pitch_deg,
	}


func restore(state: Dictionary) -> void:
	if state.is_empty():
		return
	if state.has("target"):
		target = state["target"] as Vector3
	if state.has("distance"):
		distance = float(state["distance"])
	if state.has("yaw_deg"):
		yaw_deg = float(state["yaw_deg"])
	if state.has("pitch_deg"):
		pitch_deg = float(state["pitch_deg"])
	_apply()


func _is_active() -> bool:
	return is_visible_in_tree() and _camera != null and _camera.current


func _process(delta: float) -> void:
	if not _is_active():
		return
	var move := Vector2(
		float(Input.is_key_pressed(KEY_D)) - float(Input.is_key_pressed(KEY_A)),
		float(Input.is_key_pressed(KEY_S)) - float(Input.is_key_pressed(KEY_W))
	)
	if move == Vector2.ZERO:
		return
	# Scale pan with zoom so near/far feels consistent.
	var speed := wasd_speed * maxf(distance, 0.2)
	var right: Vector3
	var forward: Vector3
	if pan_on_disk_plane:
		# Flatten camera axes onto the disk (XZ / Y-up).
		right = _camera.global_transform.basis.x
		right.y = 0.0
		right = right.normalized() if right.length_squared() > 1e-8 else Vector3.RIGHT
		forward = -_camera.global_transform.basis.z
		forward.y = 0.0
		forward = forward.normalized() if forward.length_squared() > 1e-8 else Vector3(right.z, 0.0, -right.x)
	else:
		right = _camera.global_transform.basis.x
		forward = -_camera.global_transform.basis.z
	target += (right * move.x + forward * (-move.y)) * speed * delta
	_apply()


func _unhandled_input(event: InputEvent) -> void:
	if not _is_active():
		return
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.button_index == MOUSE_BUTTON_RIGHT:
			if pan_on_rmb:
				_panning = mb.pressed
			else:
				_orbiting = mb.pressed
		elif mb.button_index == MOUSE_BUTTON_MIDDLE:
			if rotate_on_mmb:
				_orbiting = mb.pressed
			else:
				_panning = mb.pressed
		elif mb.button_index == MOUSE_BUTTON_WHEEL_UP and mb.pressed:
			distance = clampf(distance * (1.0 - zoom_sensitivity), min_distance, max_distance)
			_apply()
		elif mb.button_index == MOUSE_BUTTON_WHEEL_DOWN and mb.pressed:
			distance = clampf(distance * (1.0 + zoom_sensitivity), min_distance, max_distance)
			_apply()
	elif event is InputEventMouseMotion:
		var mm := event as InputEventMouseMotion
		if _orbiting:
			yaw_deg -= mm.relative.x * orbit_sensitivity
			pitch_deg = clampf(pitch_deg - mm.relative.y * orbit_sensitivity, 8.0, 89.0)
			_apply()
		elif _panning:
			var right := _camera.global_transform.basis.x
			var up := _camera.global_transform.basis.y
			var pan_scale := distance * pan_sensitivity
			target -= right * mm.relative.x * pan_scale
			target += up * mm.relative.y * pan_scale
			_apply()


func _apply() -> void:
	if _camera == null:
		_camera = get_node_or_null("Camera3D") as Camera3D
	if _camera == null:
		return
	var yaw := deg_to_rad(yaw_deg)
	var pitch := deg_to_rad(pitch_deg)
	var offset := Vector3(
		cos(pitch) * cos(yaw),
		sin(pitch),
		cos(pitch) * sin(yaw)
	) * distance
	_camera.global_position = target + offset
	_camera.look_at(target, Vector3.UP)
