extends Control
class_name PlanetFlag
## One planet/fleet flag: hockey-stick leader + circle zoom inset.
## Tip of the stick tracks the body/fleet screen position. Nearby flags of the
## same marker kind stack into a vertical lens column with slant leaders.
## Side is locked by kind: fleets badge-left of tip (−1); planets/fields badge-right (+1).
## Fixed-width rectangular badge chrome sits behind the content cluster
## (lens | dial? | name, or mirrored name | lens | dial); stick + dial `_draw`
## on top. Names wrap up to NAME_MAX_LINES with ellipsis overrun.
## Optional SystemPosDial (right of lens): top-down in-system pose for galaxy flags.

signal opened

const INSET_PX := 36
const STEM_X := 32
const DROP_BELOW := 20
const TIP_X := 2.0
const FLAG_W := 68  # STEM_X + INSET_PX (badge extends further for name/dial)
const FLAG_H := 56  # INSET_PX + DROP_BELOW
const TIP_Y := 54.0
const HORIZ_Y := 18.0
const ELBOW_X := 22.0
const LEG_LEN := 10.0  # STEM_X - ELBOW_X

const NAME_GAP := 4.0
## Fixed outer badge width (lens + optional dial + name column ~12–16 chars).
const BADGE_W := 168.0
const NAME_MAX_LINES := 3
const NAME_FONT_SIZE := 10
## Fallback line height when theme font is unavailable.
const NAME_LINE_H := 12.0

## Round top-down solar-system pose dial (right of lens on galaxy system flags).
const DIAL_PX := 28
const DIAL_GAP := 3.0
const DIAL_NEAR_AU := 0.5
const DIAL_FALLBACK_MAX_AU := 36.0
const DIAL_PAD := 2.5
const DIAL_DOT_R := 2.0
const DIAL_BLINK_HZ := 0.008

## Screen-space cluster radius for overlapping/near lenses (~lens + gap).
const CLUSTER_RADIUS_PX := 64.0
## Vertical pitch between stacked lens tops (room for multi-line badge height).
const STACK_SPACING := 48.0
## Horizontal gap from outermost tip to the lens column.
const STACK_OFFSET_X := 52.0
const STACK_PAD := 8.0

var world_pos: Vector3 = Vector3.ZERO
var meta: Dictionary = {}
var accent: Color = Color(0.43, 0.78, 1.0)
var color_a: Color = Color(0.56, 0.83, 0.66)
var color_b: Color = Color(0.12, 0.24, 0.16)

var _badge: Panel
## Horizontal content host inside the badge (lens | dial? | name); laid out manually
## so place_stacked / draw see correct geometry the same frame.
var _row: Control
var _frame: Button
var _lens: TextureRect
var _label: Label
## Layout slot for system-pose dial (drawn in `_draw`; always right of lens).
var _sys_dial: Control

## Leader polyline in local coords (updated by place_at_screen / place_stacked).
var _tip_l: Vector2 = Vector2(TIP_X, TIP_Y)
var _elbow_l: Vector2 = Vector2(ELBOW_X, HORIZ_Y)
var _stem_l: Vector2 = Vector2(float(STEM_X), HORIZ_Y)
var _side: int = 1  # +1 badge right of tip; -1 badge left of tip (mirrored)

var _sys_dial_on := false
var _sys_px := 0.0
var _sys_pz := 0.0
var _sys_max_au := DIAL_FALLBACK_MAX_AU
var _blink_alpha := 1.0
var _badge_hover := false


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
	var is_fleet := String(meta.get("marker", "planet")) == "fleet"
	var hostile := bool(meta.get("hostile", false))
	# Hostiles are inspectable (panel/roster) but not orderable; planets stay as before.
	var interactive := is_fleet or not hostile
	if is_fleet:
		_lens.texture = make_fleet_texture(64, color_a, color_b)
		if hostile:
			_frame.tooltip_text = "Inspect hostile fleet (cannot move)"
		else:
			_frame.tooltip_text = "Open fleet info"
	else:
		_lens.texture = make_checkered_texture(64, color_a, color_b)
		_frame.tooltip_text = "Open planet info"
	set_name_text(String(meta.get("name", "World")))
	_frame.add_theme_stylebox_override("normal", _frame_style())
	_frame.add_theme_stylebox_override("hover", _frame_style())
	_frame.add_theme_stylebox_override("pressed", _frame_style())
	_apply_badge_style()
	set_interactive(interactive)
	queue_redraw()


func set_name_text(text: String) -> void:
	if _label == null:
		_build_children()
	_label.text = text
	_relayout_badge_keep_lens()


func set_system_position_indicator(pos_x: float, pos_z: float, max_au: float, enabled: bool) -> void:
	## Galaxy in-system fleet flags: round dial right of the lens.
	## Maps AU (pos_x/pos_z) onto the dial with rim = max_au (fallback 36).
	## Dial pixels (Control Y-down): +pos_x → left, +pos_z → up (matches
	## OrbitCamera yaw ≈ −90: world +X appears left when looking +Z).
	## Within DIAL_NEAR_AU of origin: blinking center dot only (no arrow).
	if _frame == null:
		_build_children()
	_sys_dial_on = enabled
	_sys_px = pos_x
	_sys_pz = pos_z
	_sys_max_au = max_au if max_au > 1e-6 else DIAL_FALLBACK_MAX_AU
	set_process(_sys_dial_on)
	_relayout_badge_keep_lens()
	queue_redraw()


func set_interactive(on: bool) -> void:
	if _frame == null:
		return
	_frame.disabled = not on
	_frame.mouse_filter = Control.MOUSE_FILTER_STOP if on else Control.MOUSE_FILTER_IGNORE
	if _badge:
		_badge.mouse_filter = (
			Control.MOUSE_FILTER_STOP if on else Control.MOUSE_FILTER_IGNORE
		)
	if not on and bool(meta.get("hostile", false)):
		_frame.tooltip_text = String(meta.get("name", "Hostile")) + " (hostile)"


func place_at_screen(tip: Vector2, side: int = 1) -> void:
	## Solo hockey-stick: tip tracks world projection.
	## side +1 = badge/stack to the right of tip; -1 = to the left of tip.
	_reset_default_layout(side)
	position = tip - _tip_l
	visible = true
	queue_redraw()


func place_stacked(tip_screen: Vector2, lens_tl_screen: Vector2, side: int) -> void:
	## Stacked flag: lens at lens_tl_screen; tip still on tip_screen.
	## side +1 = badge to the right of tip (leg on left of lens);
	## side -1 = badge to the left of tip (leg on right of lens).
	## Badge (lens | dial? | name) sits with name opposite the leg.
	## System dial stays to the right of the lens (lens | dial | name when name right).
	if _frame == null:
		_build_children()
	_side = 1 if side >= 0 else -1

	var inset := float(INSET_PX)
	var stem_screen: Vector2
	var elbow_screen: Vector2
	if _side > 0:
		stem_screen = lens_tl_screen + Vector2(0.0, HORIZ_Y)
		elbow_screen = stem_screen + Vector2(-LEG_LEN, 0.0)
	else:
		stem_screen = lens_tl_screen + Vector2(inset, HORIZ_Y)
		elbow_screen = stem_screen + Vector2(LEG_LEN, 0.0)

	_refresh_badge_layout()
	var lens_off := _lens_offset_in_badge()
	var badge_sz := _badge.size
	var badge_tl_screen := lens_tl_screen - lens_off

	var min_x := minf(tip_screen.x, minf(elbow_screen.x, minf(lens_tl_screen.x, badge_tl_screen.x))) - STACK_PAD
	var max_x := maxf(
		tip_screen.x,
		maxf(elbow_screen.x, maxf(lens_tl_screen.x + inset, badge_tl_screen.x + badge_sz.x))
	) + STACK_PAD
	var min_y := minf(
		tip_screen.y,
		minf(elbow_screen.y, minf(lens_tl_screen.y, badge_tl_screen.y))
	) - STACK_PAD
	var max_y := maxf(
		tip_screen.y,
		maxf(elbow_screen.y, maxf(lens_tl_screen.y + inset, badge_tl_screen.y + badge_sz.y))
	) + STACK_PAD

	position = Vector2(min_x, min_y)
	size = Vector2(maxf(4.0, max_x - min_x), maxf(4.0, max_y - min_y))
	custom_minimum_size = size

	_tip_l = tip_screen - position
	_elbow_l = elbow_screen - position
	_stem_l = stem_screen - position

	_badge.position = badge_tl_screen - position
	_sync_frame_transform()
	visible = true
	queue_redraw()


func hit_test_global(global_pos: Vector2) -> bool:
	## True if point is over the badge cluster (lens / dial / name).
	if not visible or _badge == null:
		return false
	return _badge.get_global_rect().has_point(global_pos)


static func apply_fleet_flag_layout(items: Array, viewport_size: Vector2) -> void:
	## Place fleet PlanetFlags with proximity stacking.
	## items: Array of { "flag": PlanetFlag, "tip": Vector2 }
	## Friendly and hostile fleets cluster separately so mixed stacks stay readable.
	## Badge / hockey-stick always to the left of the tip (side = −1).
	if items.is_empty():
		return
	var friendlies: Array = []
	var hostiles: Array = []
	for it in items:
		var flag: PlanetFlag = it.get("flag") as PlanetFlag
		if flag == null or not is_instance_valid(flag):
			continue
		if bool(flag.meta.get("hostile", false)):
			hostiles.append(it)
		else:
			friendlies.append(it)
	_layout_proximity_group(friendlies, viewport_size, -1)
	_layout_proximity_group(hostiles, viewport_size, -1)


static func apply_flag_layout(items: Array, viewport_size: Vector2) -> void:
	## Place PlanetFlags with proximity stacking (no friend/hostile split).
	## Use for planets, asteroid-field markers, etc.
	## Badge / hockey-stick always to the right of the tip (side = +1).
	_layout_proximity_group(items, viewport_size, 1)


static func _layout_proximity_group(items: Array, viewport_size: Vector2, forced_side: int) -> void:
	var n := items.size()
	if n == 0:
		return
	var side := 1 if forced_side >= 0 else -1
	if n == 1:
		var only: Dictionary = items[0]
		(only["flag"] as PlanetFlag).place_at_screen(only["tip"] as Vector2, side)
		return

	# Transitive screen-proximity clusters (BFS).
	var r2 := CLUSTER_RADIUS_PX * CLUSTER_RADIUS_PX
	var seen := PackedByteArray()
	seen.resize(n)
	for i in n:
		seen[i] = 0

	for seed_i in n:
		if seen[seed_i]:
			continue
		var idxs: Array = []
		var queue: Array = [seed_i]
		seen[seed_i] = 1
		while not queue.is_empty():
			var i: int = queue.pop_front()
			idxs.append(i)
			var ti: Vector2 = items[i]["tip"]
			for j in n:
				if seen[j]:
					continue
				var tj: Vector2 = items[j]["tip"]
				if ti.distance_squared_to(tj) <= r2:
					seen[j] = 1
					queue.append(j)
		if idxs.size() < 2:
			var solo_i: int = idxs[0]
			(items[solo_i]["flag"] as PlanetFlag).place_at_screen(
				items[solo_i]["tip"] as Vector2, side
			)
		else:
			_place_stack(items, idxs, viewport_size, side)


static func _place_stack(
	items: Array, idxs: Array, _viewport_size: Vector2, forced_side: int
) -> void:
	## Sort top→bottom by tip Y, then place lenses in a vertical column.
	## Side is locked by marker kind (no free-space picking).
	idxs.sort_custom(func(a: int, b: int) -> bool:
		var ya: float = (items[a]["tip"] as Vector2).y
		var yb: float = (items[b]["tip"] as Vector2).y
		if absf(ya - yb) > 0.5:
			return ya < yb
		return (items[a]["tip"] as Vector2).x < (items[b]["tip"] as Vector2).x
	)

	var sum := Vector2.ZERO
	var min_tip_x := INF
	var max_tip_x := -INF
	for i in idxs:
		var t: Vector2 = items[i]["tip"]
		sum += t
		min_tip_x = minf(min_tip_x, t.x)
		max_tip_x = maxf(max_tip_x, t.x)
	var centroid := sum / float(idxs.size())

	var side := 1 if forced_side >= 0 else -1
	var lens_x: float
	if side > 0:
		lens_x = max_tip_x + STACK_OFFSET_X
	else:
		lens_x = min_tip_x - STACK_OFFSET_X - float(INSET_PX)

	var count := idxs.size()
	var total_h := float(INSET_PX) + float(count - 1) * STACK_SPACING
	var lens_y0 := centroid.y - total_h * 0.5

	for slot in count:
		var ii: int = idxs[slot]
		var tip: Vector2 = items[ii]["tip"]
		var lens_tl := Vector2(lens_x, lens_y0 + float(slot) * STACK_SPACING)
		(items[ii]["flag"] as PlanetFlag).place_stacked(tip, lens_tl, side)


func _process(_delta: float) -> void:
	if not _sys_dial_on:
		return
	# Soft blink on the pose dot (visible while dial is shown).
	_blink_alpha = 0.30 + 0.70 * (0.5 + 0.5 * sin(Time.get_ticks_msec() * DIAL_BLINK_HZ))
	queue_redraw()


func _reset_default_layout(side: int = 1) -> void:
	_side = 1 if side >= 0 else -1
	if _side > 0:
		_tip_l = Vector2(TIP_X, TIP_Y)
		_elbow_l = Vector2(ELBOW_X, HORIZ_Y)
		_stem_l = Vector2(float(STEM_X), HORIZ_Y)
		custom_minimum_size = Vector2(FLAG_W, FLAG_H)
		size = custom_minimum_size
		if _frame == null:
			return
		_relayout_default_badge()
		return
	# Mirrored solo: badge left of tip (stem/elbow on right of lens).
	var tip_dx := float(STEM_X) - TIP_X
	var tip_dy := TIP_Y - HORIZ_Y
	if _frame == null:
		_stem_l = Vector2(float(INSET_PX), HORIZ_Y)
		_elbow_l = _stem_l + Vector2(LEG_LEN, 0.0)
		_tip_l = _stem_l + Vector2(tip_dx, tip_dy)
		custom_minimum_size = Vector2(FLAG_W, FLAG_H)
		size = custom_minimum_size
		return
	_refresh_badge_layout()
	var lens_off := _lens_offset_in_badge()
	var badge_sz := _badge.size
	# Lens top-left at (lens_off.x + pad, 0) so name column can sit further left.
	var lens_tl := Vector2(STACK_PAD + lens_off.x, 0.0)
	_badge.position = lens_tl - lens_off
	_stem_l = lens_tl + Vector2(float(INSET_PX), HORIZ_Y)
	_elbow_l = _stem_l + Vector2(LEG_LEN, 0.0)
	_tip_l = _stem_l + Vector2(tip_dx, tip_dy)
	var max_x := maxf(_badge.position.x + badge_sz.x, _tip_l.x) + STACK_PAD
	var max_y := maxf(_badge.position.y + badge_sz.y, _tip_l.y) + STACK_PAD
	size = Vector2(maxf(4.0, max_x), maxf(4.0, max_y))
	custom_minimum_size = size
	_sync_frame_transform()


func _relayout_default_badge() -> void:
	## Solo layout: badge placed so the lens TL stays at (STEM_X, 0).
	if _badge == null or _frame == null:
		return
	_refresh_badge_layout()
	var lens_off := _lens_offset_in_badge()
	_badge.position = Vector2(float(STEM_X), 0.0) - lens_off
	_expand_bounds_for_badge()
	_sync_frame_transform()
	_stem_l = Vector2(float(STEM_X), HORIZ_Y)


func _relayout_badge_keep_lens() -> void:
	## Rebuild badge size/order but keep the current lens top-left fixed (stacked-safe).
	if _badge == null or _frame == null:
		return
	var lens_tl := _frame_tl_local()
	_refresh_badge_layout()
	_badge.position = lens_tl - _lens_offset_in_badge()
	_sync_frame_transform()
	# Grow only — never shrink stack/solo bounds that include the leader.
	var need_r := _badge.position.x + _badge.size.x + 4.0
	var need_b := _badge.position.y + _badge.size.y + 4.0
	if need_r > size.x or need_b > size.y:
		size = Vector2(maxf(size.x, need_r), maxf(size.y, need_b))
		custom_minimum_size = size


func _name_column_width() -> float:
	## Remaining width inside fixed badge after lens (+ dial when shown) and gaps.
	var margins := _badge_margins()
	var content_w := BADGE_W - margins.x - margins.z
	var used := float(INSET_PX) + NAME_GAP
	if _sys_dial_on:
		used += float(DIAL_PX) + DIAL_GAP
	return maxf(40.0, content_w - used)


func _name_line_height() -> float:
	if _label == null:
		return NAME_LINE_H
	var font := _label.get_theme_font("font")
	var fs := _label.get_theme_font_size("font_size")
	if font:
		return maxf(NAME_LINE_H, font.get_height(fs))
	return maxf(NAME_LINE_H, float(fs) + 2.0)


func _measure_label_size() -> Vector2:
	## Fixed name column width; height grows with wrapped lines up to NAME_MAX_LINES.
	var name_w := _name_column_width()
	var line_h := _name_line_height()
	var max_h := line_h * float(NAME_MAX_LINES)
	if _label == null or _label.text.is_empty():
		return Vector2(name_w, line_h)
	var font := _label.get_theme_font("font")
	var fs := _label.get_theme_font_size("font_size")
	var text_h := line_h
	if font:
		text_h = font.get_multiline_string_size(
			_label.text,
			HORIZONTAL_ALIGNMENT_LEFT,
			name_w,
			fs,
			NAME_MAX_LINES,
			TextServer.AUTOWRAP_WORD_SMART,
		).y
	else:
		# Rough wrap estimate without a font.
		var chars_per_line := maxi(1, int(name_w / maxf(1.0, float(fs) * 0.55)))
		var lines := mini(
			NAME_MAX_LINES,
			maxi(1, int(ceil(float(_label.text.length()) / float(chars_per_line)))),
		)
		text_h = line_h * float(lines)
	return Vector2(name_w, clampf(text_h, line_h, max_h))


func _badge_margins() -> Vector4:
	## left, top, right, bottom content margins from the badge stylebox.
	var s := _badge.get_theme_stylebox("panel") if _badge else null
	if s == null:
		return Vector4(4, 4, 4, 4)
	return Vector4(s.content_margin_left, s.content_margin_top, s.content_margin_right, s.content_margin_bottom)


func _apply_row_order() -> void:
	if _row == null or _frame == null or _label == null or _sys_dial == null:
		return
	if _side > 0:
		# lens | dial | name
		_row.move_child(_frame, 0)
		_row.move_child(_sys_dial, 1)
		_row.move_child(_label, 2)
	else:
		# name | lens | dial (dial stays right of lens)
		_row.move_child(_label, 0)
		_row.move_child(_frame, 1)
		_row.move_child(_sys_dial, 2)


func _refresh_badge_layout() -> void:
	## Size badge + row from lens / optional dial / name; order follows `_side`.
	if _badge == null or _row == null:
		return
	clip_contents = false
	_apply_row_order()
	_apply_badge_style()

	_frame.custom_minimum_size = Vector2(INSET_PX, INSET_PX)
	_frame.size = Vector2(INSET_PX, INSET_PX)

	_sys_dial.visible = _sys_dial_on
	if _sys_dial_on:
		_sys_dial.custom_minimum_size = Vector2(DIAL_PX, DIAL_PX)
		_sys_dial.size = Vector2(DIAL_PX, DIAL_PX)
	else:
		_sys_dial.custom_minimum_size = Vector2.ZERO
		_sys_dial.size = Vector2.ZERO

	var label_sz := _measure_label_size()
	_label.custom_minimum_size = label_sz
	_label.size = label_sz
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_label.max_lines_visible = NAME_MAX_LINES
	_label.clip_text = true
	_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS

	var margins := _badge_margins()
	var content_w := _content_width()
	var content_h := _content_height()

	_row.custom_minimum_size = Vector2(content_w, content_h)
	_row.size = _row.custom_minimum_size
	_row.position = Vector2(margins.x, margins.y)

	# Fixed width; height follows content (capped by name line limit).
	var badge_sz := Vector2(BADGE_W, margins.y + content_h + margins.w)
	_badge.custom_minimum_size = badge_sz
	_badge.size = badge_sz

	# Place row children explicitly so same-frame draw/hit use correct geometry.
	# Positions are relative to `_row` (badge content margins applied to `_row`).
	var x := 0.0
	var ordered: Array[Control] = []
	if _side > 0:
		ordered.assign([_frame, _sys_dial, _label] if _sys_dial_on else [_frame, _label])
	else:
		ordered.assign([_label, _frame, _sys_dial] if _sys_dial_on else [_label, _frame])
	for i in ordered.size():
		var c: Control = ordered[i]
		var cs := Vector2.ZERO
		if c == _frame:
			cs = Vector2(INSET_PX, INSET_PX)
		elif c == _sys_dial:
			cs = Vector2(DIAL_PX, DIAL_PX)
		elif c == _label:
			cs = label_sz
		c.size = cs
		c.position = Vector2(x, (content_h - cs.y) * 0.5)
		x += cs.x
		if i >= ordered.size() - 1:
			continue
		var nxt: Control = ordered[i + 1]
		# lens→dial uses DIAL_GAP; every other neighbor uses NAME_GAP.
		if (c == _frame and nxt == _sys_dial) or (c == _sys_dial and nxt == _frame):
			x += DIAL_GAP
		else:
			x += NAME_GAP


func _content_width() -> float:
	## Fixed badge content width (name column absorbs leftover after lens/dial).
	var margins := _badge_margins()
	return BADGE_W - margins.x - margins.z


func _content_height() -> float:
	var label_sz := _measure_label_size()
	var dial_h := float(DIAL_PX) if _sys_dial_on else 0.0
	return maxf(float(INSET_PX), maxf(dial_h, label_sz.y))


func _lens_offset_in_badge() -> Vector2:
	## Lens frame top-left relative to badge top-left (formula; same-frame safe).
	var margins := _badge_margins()
	var name_w := _name_column_width()
	var content_h := _content_height()
	var y := margins.y + (content_h - float(INSET_PX)) * 0.5
	var x := margins.x
	if _side < 0:
		x = margins.x + name_w + NAME_GAP
	return Vector2(x, y)


func _dial_offset_in_badge() -> Vector2:
	## Dial top-left relative to badge (always immediately right of lens).
	var margins := _badge_margins()
	var name_w := _name_column_width()
	var content_h := _content_height()
	var y := margins.y + (content_h - float(DIAL_PX)) * 0.5
	var x := margins.x + float(INSET_PX) + DIAL_GAP
	if _side < 0:
		x = margins.x + name_w + NAME_GAP + float(INSET_PX) + DIAL_GAP
	return Vector2(x, y)


func _sync_frame_transform() -> void:
	if _badge == null:
		return
	_badge.force_update_transform()
	if _row:
		_row.force_update_transform()
	if _frame:
		_frame.force_update_transform()
	if _sys_dial:
		_sys_dial.force_update_transform()


func _expand_bounds_for_badge() -> void:
	## Solo layout: grow control rect to cover the badge (+ leader room).
	if _badge == null:
		return
	var right := maxf(float(FLAG_W), _badge.position.x + _badge.size.x + 4.0)
	var bottom := maxf(float(FLAG_H), _badge.position.y + _badge.size.y + 4.0)
	size = Vector2(right, bottom)
	custom_minimum_size = size


func _build_children() -> void:
	if _frame != null:
		return
	clip_contents = false

	_badge = Panel.new()
	_badge.name = "Badge"
	_badge.mouse_filter = Control.MOUSE_FILTER_STOP
	_badge.clip_contents = false
	# Panel (+ lens/name) behind PlanetFlag `_draw` so stick + dial sit on top of chrome.
	_badge.show_behind_parent = true
	_badge.add_theme_stylebox_override("panel", _badge_style(false))
	add_child(_badge)
	move_child(_badge, 0)

	_row = Control.new()
	_row.name = "ContentRow"
	_row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_badge.add_child(_row)

	_frame = Button.new()
	_frame.name = "Frame"
	_frame.focus_mode = Control.FOCUS_NONE
	_frame.mouse_filter = Control.MOUSE_FILTER_STOP
	_frame.custom_minimum_size = Vector2(INSET_PX, INSET_PX)
	_frame.size = Vector2(INSET_PX, INSET_PX)
	_frame.flat = true
	_frame.add_theme_stylebox_override("normal", _frame_style())
	_frame.add_theme_stylebox_override("hover", _frame_style())
	_frame.add_theme_stylebox_override("pressed", _frame_style())
	_row.add_child(_frame)

	_lens = TextureRect.new()
	_lens.name = "Lens"
	_lens.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_lens.stretch_mode = TextureRect.STRETCH_SCALE
	_lens.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Circular lens centered in the square frame.
	_lens.position = Vector2(7, 7)
	_lens.size = Vector2(22, 22)
	_frame.add_child(_lens)

	_sys_dial = Control.new()
	_sys_dial.name = "SystemPosDial"
	_sys_dial.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_sys_dial.visible = false
	_sys_dial.custom_minimum_size = Vector2(DIAL_PX, DIAL_PX)
	_sys_dial.size = Vector2(DIAL_PX, DIAL_PX)
	_row.add_child(_sys_dial)

	_label = Label.new()
	_label.name = "Label"
	_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_label.add_theme_font_size_override("font_size", NAME_FONT_SIZE)
	_label.add_theme_color_override("font_color", Color(0.91, 0.93, 0.97))
	_label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.85))
	_label.add_theme_constant_override("shadow_offset_x", 1)
	_label.add_theme_constant_override("shadow_offset_y", 1)
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_label.max_lines_visible = NAME_MAX_LINES
	_label.clip_text = true
	_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	_row.add_child(_label)

	_frame.pressed.connect(func() -> void: opened.emit())
	_badge.mouse_entered.connect(_on_badge_hover.bind(true))
	_badge.mouse_exited.connect(_on_badge_hover.bind(false))
	_badge.gui_input.connect(_on_badge_gui_input)

	_refresh_badge_layout()
	_badge.position = Vector2(float(STEM_X), 0.0) - _lens_offset_in_badge()


func _on_badge_hover(on: bool) -> void:
	_badge_hover = on
	_apply_badge_style()


func _apply_badge_style() -> void:
	if _badge == null:
		return
	_badge.add_theme_stylebox_override("panel", _badge_style(_badge_hover))


func _on_badge_gui_input(event: InputEvent) -> void:
	if _frame != null and _frame.disabled:
		return
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
			opened.emit()
			accept_event()


func _frame_tl_local() -> Vector2:
	if _badge == null:
		return Vector2(float(STEM_X), 0.0)
	return _badge.position + _lens_offset_in_badge()


func _dial_tl_local() -> Vector2:
	if _badge == null or _sys_dial == null:
		return Vector2.ZERO
	return _badge.position + _dial_offset_in_badge()


func _draw() -> void:
	# Hockey-stick: tip → elbow → stem (into mid of inset stem-side).
	var tip := _tip_l
	var elbow := _elbow_l
	var stem := _stem_l
	# Soft outline under the stroke for readability.
	draw_polyline(PackedVector2Array([tip, elbow, stem]), Color(0.02, 0.03, 0.08, 0.55), 3.2, true)
	draw_polyline(PackedVector2Array([tip, elbow, stem]), accent, 1.6, true)
	# Circular border on the lens area (drawn on parent for crisp edge).
	var fl := _frame_tl_local()
	var lens_c := fl + Vector2(INSET_PX * 0.5, INSET_PX * 0.5)
	draw_arc(lens_c, 11.5, 0.0, TAU, 32, Color(0.91, 0.93, 0.97, 0.95), 1.5, true)
	_draw_system_pos_dial()


func _draw_system_pos_dial() -> void:
	if not _sys_dial_on or _sys_dial == null or not _sys_dial.visible:
		return
	var c := _dial_tl_local() + Vector2(float(DIAL_PX), float(DIAL_PX)) * 0.5
	var R := float(DIAL_PX) * 0.5 - DIAL_PAD
	# Dark disk + thin rim (top-down system).
	draw_circle(c, R + 1.0, Color(0.04, 0.06, 0.10, 0.90))
	draw_arc(c, R, 0.0, TAU, 40, Color(0.78, 0.88, 0.98, 0.70), 1.15, true)
	# Faint center crosshair.
	var tick := R * 0.18
	var tick_col := Color(0.55, 0.68, 0.82, 0.35)
	draw_line(c + Vector2(-tick, 0), c + Vector2(tick, 0), tick_col, 1.0, true)
	draw_line(c + Vector2(0, -tick), c + Vector2(0, tick), tick_col, 1.0, true)

	var max_au := maxf(_sys_max_au, 1e-3)
	# Control +Y is down; negate both so +X is left and +Z is up on the dial
	# (OrbitCamera yaw ≈ −90: world +X appears left when looking +Z).
	var offset := Vector2(-_sys_px, -_sys_pz)
	var len_au := offset.length()
	var dir := offset / len_au if len_au > 1e-8 else Vector2.ZERO
	var dist_px := minf(len_au / max_au, 1.0) * R
	var dot_pos := c + dir * dist_px

	# Arrow from center toward fleet; omit when near system origin.
	if len_au >= DIAL_NEAR_AU:
		var arrow_col := Color(0.82, 0.94, 1.0, 0.88)
		draw_line(c, dot_pos, Color(0.02, 0.04, 0.08, 0.45), 2.2, true)
		draw_line(c, dot_pos, arrow_col, 1.05, true)

	var blink := Color(0.88, 0.97, 1.0, _blink_alpha)
	draw_circle(dot_pos, DIAL_DOT_R + 0.6, Color(0.02, 0.04, 0.08, 0.55 * _blink_alpha))
	draw_circle(dot_pos, DIAL_DOT_R, blink)


func _frame_style() -> StyleBoxFlat:
	## Transparent — chrome lives on the outer badge panel.
	var s := StyleBoxFlat.new()
	s.bg_color = Color(0, 0, 0, 0)
	s.border_color = Color(0, 0, 0, 0)
	s.set_border_width_all(0)
	s.set_corner_radius_all(4)
	s.content_margin_left = 0
	s.content_margin_right = 0
	s.content_margin_top = 0
	s.content_margin_bottom = 0
	return s


func _badge_style(hover: bool) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = Color(0.04, 0.06, 0.10, 0.88)
	s.border_color = (
		Color(1, 1, 1, 0.85) if hover else Color(accent.r, accent.g, accent.b, 0.55)
	)
	s.set_border_width_all(1)
	s.set_corner_radius_all(3)
	s.content_margin_left = 4
	s.content_margin_right = 4
	s.content_margin_top = 4
	s.content_margin_bottom = 4
	if hover:
		s.shadow_color = Color(accent.r, accent.g, accent.b, 0.40)
		s.shadow_size = 5
	else:
		s.shadow_color = Color(0, 0, 0, 0.4)
		s.shadow_size = 3
	return s


static func make_fleet_texture(size_px: int, a: Color, b: Color) -> ImageTexture:
	## Circular lens with three tiny chevron “ships” in a V formation.
	var img := Image.create(size_px, size_px, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	var cx := (size_px - 1) * 0.5
	var cy := (size_px - 1) * 0.5
	var R := minf(cx, cy) * 0.92
	var bg := Color(b.r * 0.35, b.g * 0.35, b.b * 0.4, 1.0)
	for y in size_px:
		for x in size_px:
			var dx := (float(x) - cx) / R
			var dy := (cy - float(y)) / R
			if dx * dx + dy * dy > 1.0:
				continue
			img.set_pixel(x, y, bg)
	# Local lens coords: +y up. Lead ship forward (+y), wingmen aft-left/right.
	var ships := [
		Vector2(0.0, 0.28),
		Vector2(-0.32, -0.18),
		Vector2(0.32, -0.18),
	]
	for s in ships:
		_blit_chevron(img, cx + s.x * R, cy - s.y * R, R * 0.16, a)
	return ImageTexture.create_from_image(img)


static func _blit_chevron(img: Image, cx: float, cy: float, half: float, col: Color) -> void:
	## Simple filled chevron pointing “up” (nose toward -image-y / +world-up in lens).
	var x0 := int(floor(cx - half))
	var x1 := int(ceil(cx + half))
	var y0 := int(floor(cy - half * 0.85))
	var y1 := int(ceil(cy + half * 0.85))
	var w := img.get_width()
	var h := img.get_height()
	for y in range(maxi(0, y0), mini(h, y1 + 1)):
		for x in range(maxi(0, x0), mini(w, x1 + 1)):
			var lx := (float(x) - cx) / half
			var ly := (cy - float(y)) / half  # +up
			# Diamond / arrowhead: |x| + 0.55*|y_aft| < 1 near nose.
			if ly < -0.95 or ly > 1.05:
				continue
			var width_at := 0.15 + 0.85 * clampf(1.0 - ly, 0.0, 1.0)
			if absf(lx) <= width_at * 0.55 and ly > -0.7:
				img.set_pixel(x, y, col)
			elif absf(lx) <= width_at and ly <= 0.35 and ly >= -0.55:
				# hollow-ish trailing wings
				if absf(lx) >= width_at * 0.35:
					img.set_pixel(x, y, col)


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
