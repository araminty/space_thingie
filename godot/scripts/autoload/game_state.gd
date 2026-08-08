extends Node
## Global navigation + shared simulation clock.

signal entered_system(star_id: int)
signal returned_to_galaxy
signal day_changed(day: float)
signal playing_changed(playing: bool)

## 48 half-hours per day; play advances at prior rate / 48.
const HALF_HOURS_PER_DAY := 48.0
const DAYS_PER_SECOND := 24.0 / HALF_HOURS_PER_DAY  # 0.5 days/sec

var current_star_id: int = -1
var in_system: bool = false
var day: float = 0.0
var playing: bool = false


func _process(delta: float) -> void:
	if not playing:
		return
	day += DAYS_PER_SECOND * delta
	day_changed.emit(day)


func toggle_play() -> void:
	playing = not playing
	playing_changed.emit(playing)


func set_playing(value: bool) -> void:
	if playing == value:
		return
	playing = value
	playing_changed.emit(playing)


func enter_system(star_id: int) -> void:
	current_star_id = star_id
	in_system = true
	entered_system.emit(star_id)


func return_to_galaxy() -> void:
	in_system = false
	current_star_id = -1
	returned_to_galaxy.emit()


func day_label_text() -> String:
	## Whole days + half-hour step within the day (0..47 → 0h..23.5h).
	var whole := int(floor(day))
	var frac := day - float(whole)
	var half := int(floor(frac * HALF_HOURS_PER_DAY + 1e-6))
	half = clampi(half, 0, int(HALF_HOURS_PER_DAY) - 1)
	var hours := half / 2
	var mins := 0 if (half % 2) == 0 else 30
	return "day %d  %02d:%02d" % [whole, hours, mins]
