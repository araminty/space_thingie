extends Control
class_name PlanetFlag
## One planet flag: hockey-stick leader + circle-in-square zoom inset.
## Tip of the stick tracks the planet's screen position.

signal opened

const INSET_PX := 36
const STEM_X := 32
const LABEL_H := 14
const DROP_BELOW := 20
const TIP_X := 2.0
const FLAG_W := 68  # STEM_X + INSET_PX
const FLAG_H := 56  # INSET_PX + max(LABEL_H, DROP_BELOW)
const TIP_Y := 54.0
const HORIZ_Y := 18.0
const ELBOW_X := 22.0

var world_pos: Vector3 = Vector3.ZERO
var meta: Dictionary = {}
var accent: Color = Color(0.43, 0.78, 1.0)
var color_a: Color = Color(0.56, 0.83, 0.66)
var color_b: Color = Color(0.12, 0.24, 0.16)

var _frame: Button
var _lens: TextureRect
var _label: Label


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2(FLAG_W, FLAG_H)
	size = custom_minimum_size
	_build_children()


func setup(
	p_meta: Dictionary,
	p_world: Vector3,
	p_accent: Color,
	p_a: Color,
	p_b: Color,
) -> void:
	meta = p_meta
	world_pos = p_world
	accent = p_accent
	color_a = p_a
	color_b = p_b
	if _lens == null:
		_build_children()
	_lens.texture = make_checkered_texture(64, color_a, color_b)
	_label.text = String(meta.get("name", "World"))
	_fit_label()
	_frame.tooltip_text = "Open planet info"
	_frame.add_theme_stylebox_override("normal", _frame_style(false))
	_frame.add_theme_stylebox_override("hover", _frame_style(true))
	_frame.add_theme_stylebox_override("pressed", _frame_style(true))
	queue_redraw()


func place_at_screen(tip: Vector2) -> void:
	position = tip - Vector2(TIP_X, TIP_Y)
	visible = true


func _fit_label() -> void:
	# Don't clip to the 36px inset — full names sit centered under the frame.
	clip_contents = false
	_label.clip_text = false
	_label.autowrap_mode = TextServer.AUTOWRAP_OFF
	var font := _label.get_theme_font("font")
	var fs := _label.get_theme_font_size("font_size")
	var tw := 0.0
	if font:
		tw = font.get_string_size(_label.text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	else:
		tw = float(_label.text.length()) * float(fs) * 0.55
	var w := maxf(float(INSET_PX), tw + 8.0)
	_label.size = Vector2(w, float(LABEL_H + 2))
	# Center under the zoom frame; may overhang left/right of the flag rect.
	_label.position = Vector2(float(STEM_X) + float(INSET_PX) * 0.5 - w * 0.5, float(INSET_PX + 1))


func _build_children() -> void:
	if _frame != null:
		return
	clip_contents = false
	_frame = Button.new()
	_frame.name = "Frame"
	_frame.focus_mode = Control.FOCUS_NONE
	_frame.mouse_filter = Control.MOUSE_FILTER_STOP
	_frame.position = Vector2(STEM_X, 0)
	_frame.size = Vector2(INSET_PX, INSET_PX)
	_frame.flat = true
	add_child(_frame)

	_lens = TextureRect.new()
	_lens.name = "Lens"
	_lens.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_lens.stretch_mode = TextureRect.STRETCH_SCALE
	_lens.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Circular lens centered in the square frame.
	_lens.position = Vector2(7, 7)
	_lens.size = Vector2(22, 22)
	_frame.add_child(_lens)

	_label = Label.new()
	_label.name = "Label"
	_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_label.position = Vector2(STEM_X, INSET_PX + 1)
	_label.size = Vector2(INSET_PX, LABEL_H)
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_label.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_label.add_theme_font_size_override("font_size", 10)
	_label.add_theme_color_override("font_color", Color(0.91, 0.93, 0.97))
	_label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.85))
	_label.add_theme_constant_override("shadow_offset_x", 1)
	_label.add_theme_constant_override("shadow_offset_y", 1)
	_label.clip_text = false
	_label.text_overrun_behavior = TextServer.OVERRUN_NO_TRIMMING
	add_child(_label)

	_frame.pressed.connect(func() -> void: opened.emit())


func _draw() -> void:
	# Hockey-stick: tip → elbow → stem (into mid-left of inset).
	var tip := Vector2(TIP_X, TIP_Y)
	var elbow := Vector2(ELBOW_X, HORIZ_Y)
	var stem := Vector2(float(STEM_X), HORIZ_Y)
	draw_polyline(PackedVector2Array([tip, elbow, stem]), accent, 1.6, true)
	# Soft outline under the stroke for readability.
	draw_polyline(PackedVector2Array([tip, elbow, stem]), Color(0.02, 0.03, 0.08, 0.55), 3.2, true)
	draw_polyline(PackedVector2Array([tip, elbow, stem]), accent, 1.6, true)
	# Circular border on the lens area (drawn on parent for crisp edge).
	var lens_c := Vector2(STEM_X + INSET_PX * 0.5, INSET_PX * 0.5)
	draw_arc(lens_c, 11.5, 0.0, TAU, 32, Color(0.91, 0.93, 0.97, 0.95), 1.5, true)


func _frame_style(hover: bool) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = Color(0.05, 0.07, 0.12, 0.92)
	s.border_color = accent if not hover else Color(1, 1, 1)
	s.set_border_width_all(2)
	s.set_corner_radius_all(4)
	if hover:
		s.shadow_color = Color(accent.r, accent.g, accent.b, 0.45)
		s.shadow_size = 6
	else:
		s.shadow_color = Color(0, 0, 0, 0.55)
		s.shadow_size = 4
	return s


static func make_checkered_texture(size_px: int, a: Color, b: Color) -> ImageTexture:
	var img := Image.create(size_px, size_px, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	var cx := (size_px - 1) * 0.5
	var cy := (size_px - 1) * 0.5
	var R := minf(cx, cy) * 0.92
	var n_lat := 10.0
	var n_lon := 14.0
	for y in size_px:
		for x in size_px:
			var dx := (float(x) - cx) / R
			var dy := (cy - float(y)) / R  # +up
			var rr := dx * dx + dy * dy
			if rr > 1.0:
				continue
			var sin_lat := clampf(dy, -1.0, 1.0)
			var cos_lat := sqrt(maxf(0.0, 1.0 - sin_lat * sin_lat))
			if cos_lat < 1e-6:
				img.set_pixel(x, y, a if int(floor((sin_lat + 1.0) * 0.5 * n_lat)) % 2 == 0 else b)
				continue
			var sin_lon := clampf(dx / cos_lat, -1.0, 1.0)
			# Face the lit hemisphere (lon near π/2); use asin for longitude band.
			var lon := asin(sin_lon)
			var lat := asin(sin_lat)
			var la := int(floor((lat + PI * 0.5) / PI * n_lat))
			var lo := int(floor((lon + PI * 0.5) / PI * n_lon))
			la = clampi(la, 0, int(n_lat) - 1)
			lo = clampi(lo, 0, int(n_lon) - 1)
			img.set_pixel(x, y, a if ((la + lo) % 2 == 0) else b)
	return ImageTexture.create_from_image(img)
