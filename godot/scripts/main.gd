extends Node3D
## Root: galaxy + system layers, shared time HUD.

@onready var _galaxy_root: Node3D = $GalaxyRoot
@onready var _system_root: Node3D = $SystemRoot
@onready var _galaxy_cam: Camera3D = $GalaxyRoot/OrbitCamera/Camera3D
@onready var _system_cam: Camera3D = $SystemRoot/OrbitCamera/Camera3D
@onready var _galaxy_hud: Control = $UI/GalaxyHud
@onready var _system_hud: Control = $UI/SystemHud
@onready var _play_btn: Button = $UI/TimeHud/PlayButton
@onready var _day_lbl: Label = $UI/TimeHud/DayLabel


func _ready() -> void:
	_show_galaxy()
	if _play_btn:
		_play_btn.pressed.connect(GameState.toggle_play)
	GameState.entered_system.connect(_on_entered_system)
	GameState.returned_to_galaxy.connect(_on_returned)
	GameState.day_changed.connect(_on_day_changed)
	GameState.playing_changed.connect(_on_playing_changed)
	_sync_time_ui()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_SPACE:
		GameState.toggle_play()
		get_viewport().set_input_as_handled()


func _on_entered_system(_star_id: int) -> void:
	if _galaxy_root:
		_galaxy_root.visible = false
	if _system_root:
		_system_root.visible = true
	if _galaxy_hud:
		_galaxy_hud.visible = false
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


func _sync_time_ui() -> void:
	if _play_btn:
		_play_btn.text = "⏸ Pause" if GameState.playing else "▶ Play"
	if _day_lbl:
		_day_lbl.text = GameState.day_label_text()
