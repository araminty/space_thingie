extends Control
class_name UnlockProgressMarker
## Lane midpoint marker: progress ring while a scientist works, or a queue
## number in a circle while waiting for a free scientist (dimmer if unseen).

const SIZE_PX := 28.0
const RING_WIDTH := 3.5

enum Mode { ACTIVE, QUEUED }

var lane_id: int = -1
var mode: int = Mode.ACTIVE
var progress: float = 0.0  # 0..1 complete when ACTIVE
var queue_number: int = 0  # 1-based when QUEUED
var _queued_unseen: bool = false
var world_pos: Vector3 = Vector3.ZERO

var _bg := Color(0.08, 0.1, 0.14, 0.82)
var _track := Color(0.35, 0.4, 0.48, 0.85)
var _fill := Color(0.45, 0.82, 0.95, 1.0)
var _hub := Color(0.75, 0.9, 1.0, 0.95)
var _queue_fill := Color(0.55, 0.62, 0.72, 0.95)
var _queue_fill_unseen := Color(0.32, 0.34, 0.38, 0.9)
var _queue_text := Color(0.92, 0.96, 1.0, 1.0)
var _queue_text_unseen := Color(0.7, 0.72, 0.75, 0.95)


func _ready() -> void:
	# Ignore so LMB reaches galaxy lane pick (double-click promote / assign).
	# RMB pause/cancel is hit-tested from galaxy_map._input.
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2(SIZE_PX, SIZE_PX)
	size = Vector2(SIZE_PX, SIZE_PX)
	tooltip_text = "Unlocking · RMB to pause"


func set_active_progress(p: float) -> void:
	mode = Mode.ACTIVE
	progress = clampf(p, 0.0, 1.0)
	queue_number = 0
	_queued_unseen = false
	queue_redraw()


func set_queue_number(n: int, unseen: bool = false) -> void:
	mode = Mode.QUEUED
	queue_number = maxi(n, 1)
	progress = 0.0
	_queued_unseen = unseen
	queue_redraw()


func place_at_screen(tip: Vector2) -> void:
	## Center the ring on the lane midpoint tip.
	position = tip - size * 0.5
	visible = true
	queue_redraw()


func hit_test_global(global_pos: Vector2) -> bool:
	if not visible:
		return false
	return get_global_rect().has_point(global_pos)


func _draw() -> void:
	var c := size * 0.5
	var r := minf(size.x, size.y) * 0.5 - 1.0
	draw_circle(c, r, _bg)
	if mode == Mode.QUEUED:
		var fill := _queue_fill_unseen if _queued_unseen else _queue_fill
		var tcol := _queue_text_unseen if _queued_unseen else _queue_text
		draw_circle(c, r - 1.5, fill)
		var font := ThemeDB.fallback_font
		var fs := 14 if queue_number < 10 else 11
		var label := str(queue_number)
		var text_size := font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs)
		var baseline := c + Vector2(-text_size.x * 0.5, text_size.y * 0.35)
		draw_string(font, baseline, label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, tcol)
		return
	draw_arc(c, r - RING_WIDTH * 0.5, 0.0, TAU, 48, _track, RING_WIDTH, true)
	var p := clampf(progress, 0.0, 1.0)
	if p > 0.001:
		# Start at top (−PI/2), sweep clockwise for “loading” feel.
		var from := -PI * 0.5
		var to := from + TAU * p
		draw_arc(c, r - RING_WIDTH * 0.5, from, to, 48, _fill, RING_WIDTH, true)
	draw_circle(c, r * 0.28, _hub)
