extends Node3D
## Camera-locked star sphere (equirectangular texture, uniform-on-sphere sampling).

const TEX_W := 4096
const TEX_H := 2048

@export var star_count: int = 8000
@export var space_color: Color = Color(0.012, 0.018, 0.045)
@export var radius_far_frac: float = 0.82

var _sphere: MeshInstance3D


func _ready() -> void:
	var tex := _make_star_texture()
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_texture = tex
	mat.albedo_color = Color.WHITE
	# Nearest keeps tiny stars as pinpoints (linear blurs/stretches them).
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	mat.texture_repeat = false
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	mat.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
	mat.disable_receive_shadows = true
	mat.render_priority = -128

	var mesh := SphereMesh.new()
	mesh.radius = 1.0
	mesh.height = 2.0
	mesh.radial_segments = 64
	mesh.rings = 32

	_sphere = MeshInstance3D.new()
	_sphere.name = "StarSphere"
	_sphere.mesh = mesh
	_sphere.material_override = mat
	_sphere.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_sphere)


func _process(_delta: float) -> void:
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		visible = false
		return
	visible = true
	global_position = cam.global_position
	global_basis = Basis.IDENTITY
	var r := maxf(cam.far * radius_far_frac, 20.0)
	scale = Vector3.ONE * r


func _make_star_texture() -> ImageTexture:
	## Equirectangular map. Stars placed by uniform solid-angle sampling so poles
	## are not over-/under-dense relative to the equator.
	var img := Image.create(TEX_W, TEX_H, false, Image.FORMAT_RGBA8)
	img.fill(space_color)
	var rng := RandomNumberGenerator.new()
	rng.seed = 42_4242
	for _i in star_count:
		# Uniform direction on the sphere.
		var z := rng.randf_range(-1.0, 1.0)
		var a := rng.randf() * TAU
		var r_xy := sqrt(maxf(0.0, 1.0 - z * z))
		var x := r_xy * cos(a)
		var y := z
		var zz := r_xy * sin(a)
		# Equirect UV: u = atan2(x,z), v = asin(y)
		var u := atan2(x, zz) / TAU + 0.5
		var v := 0.5 - asin(clampf(y, -1.0, 1.0)) / PI
		var px := int(floor(u * float(TEX_W))) % TEX_W
		var py := clampi(int(floor(v * float(TEX_H))), 0, TEX_H - 1)
		if px < 0:
			px += TEX_W
		var bright := rng.randf_range(0.65, 1.0)
		# Single-pixel stars only (smaller / sharper).
		img.set_pixel(px, py, Color(bright, bright * 0.97, bright * 0.92, 1.0))
	return ImageTexture.create_from_image(img)
