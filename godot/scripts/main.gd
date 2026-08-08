extends Node3D
## Root: galaxy + system layers, shared time HUD.

@onready var _galaxy_root: Node3D = $GalaxyRoot
@onready var _system_root: Node3D = $SystemRoot
@onready var _galaxy_cam: Camera3D = $GalaxyRoot/OrbitCamera/Camera3D
@onready var _system_cam: Camera3D = $SystemRoot/OrbitCamera/Camera3D
@onready var _galaxy_hud: Control = $UI/GalaxyHud
@onready var _galaxy_transit_flags: Control = $UI/GalaxyTransitFlags
@onready var _galaxy_fleet_panel: Control = $UI/GalaxyFleetPanel
@onready var _system_hud: Control = $UI/SystemHud
@onready var _play_btn: Button = $UI/TimeHud/PlayButton
@onready var _speed_strip: HBoxContainer = $UI/TimeHud/SpeedStrip
@onready var _day_lbl: Label = $UI/TimeHud/DayLabel

var _speed_btns: Array[Button] = []

# Digits 1…5 → PLAY_SPEEDS indices (skip 2× and 8×).
const SPEED_KEY_INDICES: Array[int] = [0, 1, 2, 4, 6]


func _ready() -> void:
	_show_galaxy()
	if _play_btn:
		# Mouse-only focus so Space always hits _unhandled_input → toggle_play
		# (not Button ui_accept). LineEdit/TextEdit still consume Space via GUI.
		_play_btn.focus_mode = Control.FOCUS_NONE
		_play_btn.pressed.connect(GameState.toggle_play)
	_wire_speed_buttons()
	GameState.entered_system.connect(_on_entered_system)
	GameState.returned_to_galaxy.connect(_on_returned)
	GameState.day_changed.connect(_on_day_changed)
	GameState.playing_changed.connect(_on_playing_changed)
	GameState.play_speed_changed.connect(_on_play_speed_changed)
	_sync_time_ui()


func _wire_speed_buttons() -> void:
	if _speed_strip == null:
		return
	_speed_btns.clear()
	var speeds: Array = GameState.PLAY_SPEEDS
	for i in range(speeds.size()):
		var btn := _speed_strip.get_node_or_null("Speed%d" % i) as Button
		if btn == null:
			continue
		btn.focus_mode = Control.FOCUS_NONE
		btn.toggle_mode = false
		var speed: float = speeds[i]
		btn.pressed.connect(_on_speed_pressed.bind(speed))
		_speed_btns.append(btn)


func _on_speed_pressed(speed: float) -> void:
	GameState.set_play_speed(speed)
	_sync_speed_ui()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_SPACE:
				GameState.toggle_play()
				get_viewport().set_input_as_handled()
			KEY_BRACKETLEFT:
				GameState.cycle_play_speed(-1)
				get_viewport().set_input_as_handled()
			KEY_BRACKETRIGHT:
				GameState.cycle_play_speed(1)
				get_viewport().set_input_as_handled()
			KEY_1, KEY_2, KEY_3, KEY_4, KEY_5:
				# Digits 1…5 → PLAY_SPEEDS via SPEED_KEY_INDICES; does not toggle pause.
				var key_i := int(event.keycode) - int(KEY_1)
				var speeds: Array = GameState.PLAY_SPEEDS
				if key_i >= 0 and key_i < SPEED_KEY_INDICES.size():
					var idx: int = SPEED_KEY_INDICES[key_i]
					if idx < speeds.size():
						GameState.set_play_speed(float(speeds[idx]))
						get_viewport().set_input_as_handled()


func _on_entered_system(_star_id: int) -> void:
	if _galaxy_root:
		_galaxy_root.visible = false
	if _system_root:
		_system_root.visible = true
	if _galaxy_hud:
		_galaxy_hud.visible = false
	if _galaxy_transit_flags:
		_galaxy_transit_flags.visible = false
	if _galaxy_fleet_panel:
		_galaxy_fleet_panel.visible = false
	if _system_hud:
		_system_hud.visible = true
	if _galaxy_cam:
		_galaxy_cam.current = false
	if _system_cam:
		_system_cam.current = true


func _on_returned() -> void:
	_show_galaxy()


func _show_galaxy() -> void:
	if _galaxy_root:
		_galaxy_root.visible = true
	if _system_root:
		_system_root.visible = false
	if _galaxy_hud:
		_galaxy_hud.visible = true
	if _galaxy_transit_flags:
		_galaxy_transit_flags.visible = true
	# Fleet panel visibility is owned by galaxy_map (selection).
	if _system_hud:
		_system_hud.visible = false
	if _system_cam:
		_system_cam.current = false
	if _galaxy_cam:
		_galaxy_cam.current = true


func _on_day_changed(_day: float) -> void:
	_sync_time_ui()


func _on_playing_changed(_playing: bool) -> void:
	_sync_time_ui()


func _on_play_speed_changed(_speed: float) -> void:
	_sync_speed_ui()


func _sync_time_ui() -> void:
	if _play_btn:
		_play_btn.text = "⏸ Pause" if GameState.playing else "▶ Play"
	if _day_lbl:
		_day_lbl.text = GameState.day_label_text()
	_sync_speed_ui()


func _sync_speed_ui() -> void:
	var speeds: Array = GameState.PLAY_SPEEDS
	for i in range(_speed_btns.size()):
		var btn := _speed_btns[i]
		var active := i < speeds.size() and is_equal_approx(GameState.play_speed, float(speeds[i]))
		btn.modulate = Color(1.15, 1.25, 1.4, 1.0) if active else Color(0.85, 0.9, 0.95, 0.85)
