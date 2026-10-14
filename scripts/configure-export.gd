extends SceneTree


func _initialize() -> void:
	var preset := ConfigFile.new()
	var load_error := preset.load("res://export_presets.cfg")
	if load_error != OK and load_error != ERR_FILE_NOT_FOUND:
		push_error("Cannot load Web export presets: %s" % error_string(load_error))
		quit(1)
		return

	var preset_index := 0
	while preset.has_section("preset.%d" % preset_index):
		if preset.get_value("preset.%d" % preset_index, "name", "") == "Web":
			break
		preset_index += 1

	var preset_section := "preset.%d" % preset_index
	var options_section := "%s.options" % preset_section
	preset.set_value(preset_section, "name", "Web")
	preset.set_value(preset_section, "platform", "Web")
	preset.set_value(preset_section, "runnable", true)
	preset.set_value(preset_section, "export_filter", "all_resources")
	preset.set_value(preset_section, "include_filter", "")
	preset.set_value(preset_section, "exclude_filter", "")
	preset.set_value(options_section, "custom_template/debug", "/workspace/build/templates/web_debug.zip")
	preset.set_value(options_section, "custom_template/release", "/workspace/build/templates/web_release.zip")
	preset.set_value(options_section, "variant/thread_support", true)
	preset.set_value(options_section, "threads/emscripten_pool_size", 24)
	preset.set_value(options_section, "threads/godot_pool_size", 4)
	preset.set_value(options_section, "variant/extensions_support", false)
	preset.set_value(options_section, "html/canvas_resize_policy", 2)
	var error := preset.save("res://export_presets.cfg")
	if error != OK:
		push_error("Cannot save Web export preset: %s" % error_string(error))
		quit(1)
		return

	quit()
