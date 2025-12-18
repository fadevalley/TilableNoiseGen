import bpy
from bpy.types import Panel


class NOISE_PT_main_panel(Panel):
    bl_label = "Tilable NoiseGen"
    bl_idname = "NOISE_PT_main_panel"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Noise Tools"


    @classmethod
    def poll(cls, context):
        return context.space_data and context.space_data.type == 'IMAGE_EDITOR'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        img = context.space_data.image
        
        # Image Name, Overwrite and Generate Button
        box = layout.box()
        box.prop(scene, "noise_image_name", text="Name", expand=True)
        box.prop(scene, "noise_overwrite", text="Overwrite")
        
        # Generate Button based on noise type
        if scene.noise_type == 'PERLIN':
            op = box.operator("noise.generate_perlin", text="Generate Noise")
            op.image_name = scene.noise_image_name
            op.overwrite = scene.noise_overwrite
            op.correct_aspect = scene.noise_correct_aspect
            op.width = scene.noise_width
            op.height = scene.noise_height
            op.seed = scene.noise_seed
            op.period = scene.noise_period
            op.turbulence = scene.noise_turbulence
            op.depth = scene.noise_depth
            op.lacunarity = scene.noise_lacunarity
            op.atten = scene.noise_atten
            op.use_color = scene.noise_use_color
            op.use_alpha = scene.noise_use_alpha
            op.absolute = scene.noise_absolute
        else:  # VORONOII
            op = box.operator("noise.generate_voronoii", text="Generate Noise")
            op.image_name = scene.noise_image_name
            op.overwrite = scene.noise_overwrite
            op.correct_aspect = scene.noise_correct_aspect
            op.width = scene.noise_width
            op.height = scene.noise_height
            op.seed = scene.noise_seed
            op.frequency = scene.noise_frequency
            op.return_type = scene.noise_return_type
            op.minkowski_exponent = scene.noise_minkowski_exponent
            op.smoothness = scene.noise_smoothness
            op.randomness = scene.noise_randomness
            op.use_color = scene.noise_use_color
            op.use_alpha = scene.noise_use_alpha
        
        #Image settings
        box = layout.box()
        box.label(text="Image settings")
        col = box.column(align=True)
        col.prop(scene, "noise_correct_aspect", text="display as 1x1")
        col.prop(scene, "noise_width", text="Width")
        col.prop(scene, "noise_height", text="Height")

        # Noise Type
        box = layout.box()
        box.label(text="Noise Settings")
        col = box.column(align=True)
        col.prop(scene, "noise_type", text="Noise Type")
        col.prop(scene, "noise_seed", text = "Seed")

        # Noise-specific settings
        if scene.noise_type == 'PERLIN':
            col.prop(scene, "noise_period", text = "Scale")
            col.prop(scene, "noise_turbulence", text = "Use depth")
            col.prop(scene, "noise_depth", text = "Depth details")
            col.prop(scene, "noise_lacunarity", text = "lacunarity")
            col.prop(scene, "noise_atten", text = "Mix details")
        else:  # VORONOII
            col.prop(scene, "noise_frequency", text="Frequency")
            col.prop(scene, "noise_return_type", text="Return Type")
            # Only show Minkowski exponent when using Minkowski distance
            if scene.noise_return_type == '1' or scene.noise_return_type == '3':
                col.prop(scene, "noise_minkowski_exponent", text="Minkowski p")
            col.prop(scene, "noise_smoothness", text="Smoothness")
            col.prop(scene, "noise_randomness", text="Randomness")

        box = layout.box()
        box.label(text="Other")
        col = box.column(align=True)
        col.prop(scene, "noise_use_color", text = "RGB")
        col.prop(scene, "noise_use_alpha", text = "Alpha")
        
        if scene.noise_type == 'PERLIN':
            col.prop(scene, "noise_absolute", text = "Groovy")
        

        
        # Add to Shader Button
        layout.operator("noise.add_to_shader")