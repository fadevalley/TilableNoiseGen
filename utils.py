import bpy


def update_display_aspect(self, context):
    img = context.space_data.image
    if img:
        # Update the image's display aspect immediately
        if self.noise_correct_aspect:
            img.display_aspect = (1, img.size[0]/img.size[1]) if img.size[0] > img.size[1] else (img.size[1]/img.size[0], 1)
        else:
            img.display_aspect = (1.0, 1.0)
        
        # Also update the stored parameter if it exists
        if "noise_params" in img:
            img["noise_params"]["correct_aspect"] = self.noise_correct_aspect
            

class NoiseParamsUpdater:
    print("NoiseParamsUpdater run")
    _timer = None
    _current_image = ""
    _last_area = None

    @classmethod
    def start_polling(cls):
        if cls._timer is None:
            cls._timer = bpy.app.timers.register(cls.poll, persistent=True)
            print("NoiseParamsUpdater initiated")

    @classmethod
    def stop_polling(cls):
        if cls._timer is not None:
            try:
                bpy.app.timers.unregister(cls._timer)
            except ValueError:
                # Timer was already removed
                pass
            cls._timer = None
        cls._current_image = ""
        cls._last_area = None

    @classmethod
    def poll(cls):
        # Get all image editor spaces in the current window
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    space = area.spaces.active
                    
                    if space and space.image:
                        img = space.image
                        if img.name != cls._current_image:
                            cls._current_image = img.name
                            if "noise_params" in img:
                                params = img["noise_params"]
                                scene = bpy.context.scene
                                
                                # Update all properties at once
                                scene.noise_image_name = img.name
                                scene.noise_width = params["width"]
                                scene.noise_height = params["height"]
                                scene.noise_seed = params["seed"]
                                scene.noise_use_color = params["use_color"]
                                scene.noise_use_alpha = params["use_alpha"]
                                scene.noise_correct_aspect = params["correct_aspect"]
                                
                                # Set noise type based on params
                                if "turbulence" in params:
                                    scene.noise_type = 'PERLIN'
                                    scene.noise_period = params["period"]
                                    scene.noise_absolute = params["absolute"]
                                    scene.noise_turbulence = params["turbulence"]
                                    
                                    if params["turbulence"]:
                                        scene.noise_depth = params["depth"]
                                        scene.noise_lacunarity = params["lacunarity"]
                                        scene.noise_atten = params["atten"]
                                else:
                                    scene.noise_type = 'VORONOI'
                                    scene.noise_frequency = params["frequency"]
                                    # Only set fbm_iterations if it exists in params (for backward compatibility)
                                    if "fbm_iterations" in params:
                                        scene.noise_fbm_iterations = params["fbm_iterations"]
                                    scene.noise_return_type = params["return_type"]
                                
                                # Update aspect ratio from params
                                if "correct_aspect" in img["noise_params"]:
                                    bpy.context.scene.noise_correct_aspect = img["noise_params"]["correct_aspect"]

                                # Force UI update
                                area.tag_redraw()
                                print(f"Updated UI for image: {img.name}")
                    
        return 0.1  # Run every 0.1 seconds