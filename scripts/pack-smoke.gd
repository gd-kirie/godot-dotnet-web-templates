extends SceneTree


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 2:
		push_error("Usage: --script pack-smoke.gd -- PUBLISH_DIR OUTPUT_PCK")
		quit(1)
		return

	var packer := PCKPacker.new()
	assert(packer.pck_start(args[1]) == OK)
	var project := ConfigFile.new()
	assert(project.load("res://project.godot") == OK)
	project.set_value("", "_custom_features", "dotnet")
	assert(project.save("user://smoke-project.godot") == OK)
	assert(packer.add_file("res://project.godot", "user://smoke-project.godot") == OK)
	for name in ["Main.tscn", "Main.cs", "ThreadProbe.cs"]:
		assert(packer.add_file("res://" + name, "res://" + name) == OK)
	var cache := ConfigFile.new()
	cache.set_value("", "list", Array([], TYPE_DICTIONARY, "", null))
	assert(cache.save("user://smoke-script-cache.cfg") == OK)
	assert(packer.add_file("res://.godot/global_script_class_cache.cfg", "user://smoke-script-cache.cfg") == OK)
	add_directory(packer, args[0], "res://.godot/mono/publish/wasm32")
	assert(packer.flush() == OK)
	quit()


func add_directory(packer: PCKPacker, source: String, destination: String) -> void:
	var directory := DirAccess.open(source)
	assert(directory != null)
	for name in directory.get_files():
		if name.ends_with(".dll") or name.ends_with(".json") or name.ends_with(".pdb"):
			assert(packer.add_file(destination.path_join(name), source.path_join(name)) == OK)
	for name in directory.get_directories():
		add_directory(packer, source.path_join(name), destination.path_join(name))
