# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "TilableNoiseGen",
    "author": "BykovSer and FadeValley",
    "version": (1, 9, 0),
    "blender": (4, 3, 0),
    "location": "Image Editor > N Panel > Noise Tools",
    "description": "Generates procedural noise patterns and connects to shaders",
    "category": "Material",
}

# Import necessary modules
import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty
from .utils import NoiseParamsUpdater, update_display_aspect
from .operators import NOISE_OT_generate_perlin, NOISE_OT_generate_voronoii, NOISE_OT_add_to_shader
from .panels import NOISE_PT_main_panel


classes = (
    NOISE_OT_generate_perlin,
    NOISE_OT_generate_voronoii,
    NOISE_OT_add_to_shader,
    NOISE_PT_main_panel,
)


def register():
    NoiseParamsUpdater.stop_polling()
    
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Scene properties for UI
    bpy.types.Scene.noise_image_name = StringProperty(
        name="Image Name",
        default="NoiseTexture",
        update=lambda s,c: setattr(c.scene, 'noise_name_exists', s.image_name in bpy.data.images)
    )
    bpy.types.Scene.noise_overwrite = BoolProperty(
        name="Overwrite",
        default=True
    )
    bpy.types.Scene.noise_width = IntProperty(default=512, min=64, max=8192)
    bpy.types.Scene.noise_height = IntProperty(default=512, min=64, max=8192)
    bpy.types.Scene.noise_period = FloatProperty(default=64.0, min=1.0, max=1000.0)
    bpy.types.Scene.noise_seed = IntProperty(default=1, min=0)
    bpy.types.Scene.noise_generator_last_image = StringProperty()
    bpy.types.Scene.noise_depth = IntProperty(default=4, min=1, max=8)
    bpy.types.Scene.noise_lacunarity = FloatProperty(default=2.0, min=1.0, max=64.0)
    bpy.types.Scene.noise_atten = FloatProperty(default=0.5, min=0.01, max=1.0)
    bpy.types.Scene.noise_use_color = BoolProperty(default=False)
    bpy.types.Scene.noise_use_alpha = BoolProperty(default=False)
    bpy.types.Scene.noise_absolute = BoolProperty(default=False)
    bpy.types.Scene.noise_turbulence = BoolProperty(default=False)
    bpy.types.Scene.noise_correct_aspect = BoolProperty(
        default=True,
        update=update_display_aspect,
        description="Adjust display aspect ratio based on image dimensions"
    )
    bpy.types.Scene.noise_type = EnumProperty(
        name="Noise Type",
        items=[
            ('PERLIN', "Perlin", "Generate Perlin noise"),
            ('VORONOII', Voronoioi", "GeneratVoronoinoi noise"),
        ],
        default='PERLIN'
    )
    bpy.types.Scene.noise_frequency = FloatProperty(default=4.0, min=0.1, max=100.0)
    bpy.types.Scene.noise_fbm_iterations = IntProperty(default=0, min=0, max=8)
    bpy.types.Scene.noise_return_type = EnumProperty(
        name="Return Type",
        items=[
            ('0', "Euclidean Distance", "Distance to the closest point using Euclidean distance"),
            ('1', "Minkowski Distance", "Distance to the closest point using Minkowski distance"),
            ('2', "Cell Pattern (Euclidean)", "Difference between closest and second closest point using Euclidean distance"),
            ('3', "Cell Pattern (Minkowski)", "Difference between closest and second closest point using Minkowski distance"),
        ],
        default='0'
    )
    bpy.types.Scene.noise_minkowski_exponent = FloatProperty(
        name="Minkowski Exponent (p)",
        default=3.0,
        min=0.1,
        max=10.0,
        description="Exponent for Minkowski distance calculation"
    )
    bpy.types.Scene.noise_smoothness = FloatProperty(default=0.0, min=0.0, max=1.0)
    bpy.types.Scene.noise_randomness = FloatProperty(default=1.0, min=0.0, max=1.0)
    bpy.types.Scene.noise_active_image = StringProperty()
    bpy.types.Scene.noise_name_exists = BoolProperty(default=False)
    NoiseParamsUpdater.start_polling()


def unregister():
    NoiseParamsUpdater.stop_polling()
    
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Remove scene properties
    del bpy.types.Scene.noise_image_name
    del bpy.types.Scene.noise_overwrite
    del bpy.types.Scene.noise_width
    del bpy.types.Scene.noise_height
    del bpy.types.Scene.noise_period
    del bpy.types.Scene.noise_seed
    del bpy.types.Scene.noise_generator_last_image
    del bpy.types.Scene.noise_depth    
    del bpy.types.Scene.noise_lacunarity
    del bpy.types.Scene.noise_atten
    del bpy.types.Scene.noise_use_color
    del bpy.types.Scene.noise_use_alpha
    del bpy.types.Scene.noise_absolute
    del bpy.types.Scene.noise_turbulence
    del bpy.types.Scene.noise_correct_aspect
    
    del bpy.types.Scene.noise_type
    del bpy.types.Scene.noise_frequency
    del bpy.types.Scene.noise_fbm_iterations
    del bpy.types.Scene.noise_return_type
    del bpy.types.Scene.noise_minkowski_exponent
    del bpy.types.Scene.noise_smoothness
    del bpy.types.Scene.noise_randomness
    del bpy.types.Scene.noise_active_image
    del bpy.types.Scene.noise_name_exists