import bpy
from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, EnumProperty
from .noise_generators import create_perlin_noise_image, create_turbulence_image, create_worley_noise_image

class NOISE_OT_generate_perlin(Operator):
    bl_idname = "noise.generate_perlin"
    bl_label = "Generate Perlin Noise"
    bl_options = {'REGISTER', 'UNDO'}

    # Operator properties
    image_name: StringProperty(
        name="Image Name",
        default="NoiseTexture",
    )
    overwrite: BoolProperty(
        name="Overwrite Existing",
        default=True,
        description="Replace existing image with the same name"
    )
    depth: IntProperty(
        name="Depth",
        default=4,
        min=1,
        max=8,
        description="Number of noise layers"
    )
    lacunarity: FloatProperty(
        name="lacunarity",
        default=2.0,
        min=1.0,
        max=64.0,
        description="Step of each octave"
    )
    atten: FloatProperty(
        name="Attenuation",
        default=0.5,
        min=0.01,
        max=1.0,
        description="Amplitude reduction per layer"
    )
    use_color: BoolProperty(
        name="RGB",
        default=False,
        description="Generate separate noise for each color channel"
    )
    use_alpha: BoolProperty(
        name="Alpha",
        default=False,
        description="Generate alpha channel noise"
    )
    absolute: BoolProperty(
        name="Absolute",
        default=False,
        description="Use absolute values for contrast"
    )
    turbulence: BoolProperty(
        name="Turbulence",
        default=False,
        description="Enable multi-layer turbulence"
    )
    correct_aspect: BoolProperty(
        name="Correct Aspect Ratio",
        default=True,
        description="Adjust display aspect ratio based on image dimensions"
    )

    width: IntProperty(default=512, min=64, max=8192)
    height: IntProperty(default=512, min=64, max=8192)
    period: FloatProperty(default=64.0, min=1.0, max=1000.0)
    seed: IntProperty(default=1, min=0)

    def execute(self, context):
        if not self.overwrite and self.image_name in bpy.data.images:
            self.report({'ERROR'}, "Image exists! Check Overwrite")
            return {'CANCELLED'}
        if self.turbulence:
            image = create_turbulence_image(
                self.image_name,
                self.width,
                self.height,
                self.period,
                self.seed,
                self.depth,
                self.lacunarity,
                self.atten,
                self.use_color,
                self.use_alpha,
                self.absolute,
                self.overwrite,
                self.correct_aspect
            )
        else:
            image = create_perlin_noise_image(
                self.image_name,
                self.width,
                self.height,
                self.period,
                self.seed,
                self.overwrite,
                self.correct_aspect,
                self.use_color,
                self.use_alpha,
                self.absolute
            )
        
        # Set the active image in the Image Editor
        if context.space_data and context.space_data.type == 'IMAGE_EDITOR':
            context.space_data.image = image
        
        self.report({'INFO'}, f"Image updated: {image.name}")
        context.scene.noise_generator_last_image = image.name
        context.scene.noise_image_name = image.name
        context.scene.noise_overwrite = True
        image.pack()
        image.colorspace_settings.name = 'Non-Color'
        return {'FINISHED'}

# Operator to Generate Worley Noise
class NOISE_OT_generate_worley(Operator):
    bl_idname = "noise.generate_worley"
    bl_label = "Generate Worley Noise"
    bl_options = {'REGISTER', 'UNDO'}

    # Operator properties
    image_name: StringProperty(
        name="Image Name",
        default="WorleyNoise",
    )
    overwrite: BoolProperty(
        name="Overwrite Existing",
        default=True,
        description="Replace existing image with the same name"
    )
    frequency: FloatProperty(
        name="Frequency",
        default=4.0,
        min=0.1,
        max=100.0,
        description="Number of cells per unit"
    )
    return_type: EnumProperty(
        name="Return Type",
        items=[
            ('0', "Euclidean Distance", "Distance to the closest point using Euclidean distance"),
            ('1', "Minkowski Distance", "Distance to the closest point using Minkowski distance"),
            ('2', "Cell Pattern (Euclidean)", "Difference between closest and second closest point using Euclidean distance"),
            ('3', "Cell Pattern (Minkowski)", "Difference between closest and second closest point using Minkowski distance"),
        ],
        default='0',
        description="Type of distance calculation for Worley noise"
    )
    minkowski_exponent: FloatProperty(
        name="Minkowski Exponent (p)",
        default=3.0,
        min=0.1,
        max=10.0,
        description="Exponent for Minkowski distance calculation"
    )
    use_color: BoolProperty(
        name="RGB",
        default=False,
        description="Generate separate noise for each color channel"
    )
    use_alpha: BoolProperty(
        name="Alpha",
        default=False,
        description="Generate alpha channel noise"
    )
    correct_aspect: BoolProperty(
        name="Correct Aspect Ratio",
        default=True,
        description="Adjust display aspect ratio based on image dimensions"
    )
    smoothness: FloatProperty(
        name="Smoothness",
        default=0.0,
        min=0.0,
        max=1.0,
        description="Smoothing applied to the noise (higher = more blur)"
    )
    randomness: FloatProperty(
        name="Randomness",
        default=1.0,
        min=0.0,
        max=1.0,
        description="Randomness of cell center positions (0 = grid, 1 = fully random)"
    )

    width: IntProperty(default=512, min=64, max=8192)
    height: IntProperty(default=512, min=64, max=8192)
    seed: IntProperty(default=1, min=0)

    def execute(self, context):
        if not self.overwrite and self.image_name in bpy.data.images:
            self.report({'ERROR'}, "Image exists! Check Overwrite")
            return {'CANCELLED'}
        
        image = create_worley_noise_image(
            self.image_name,
            self.width,
            self.height,
            self.frequency,
            self.seed,
            self.return_type,
            self.use_color,
            self.use_alpha,
            self.overwrite,
            self.correct_aspect,
            smoothness=self.smoothness,
            randomness=self.randomness,
            minkowski_exponent=self.minkowski_exponent
        )
        
        # Set the active image in the Image Editor
        if context.space_data and context.space_data.type == 'IMAGE_EDITOR':
            context.space_data.image = image
        
        self.report({'INFO'}, f"Image updated: {image.name}")
        context.scene.noise_generator_last_image = image.name
        context.scene.noise_image_name = image.name
        context.scene.noise_overwrite = True
        image.pack()
        image.colorspace_settings.name = 'Non-Color'
        return {'FINISHED'}

# Operator to Add Noise to Shader
class NOISE_OT_add_to_shader(Operator):
    bl_idname = "noise.add_to_shader"
    bl_label = "Add to Active Shader"
    bl_description = "Connect generated image to active material"
    bl_options = {'REGISTER', 'UNDO'}

    def get_absolute_location(self, node):
        """Calculate absolute location considering all parent frames/groups"""
        abs_location = (node.location)
        parent = node.parent
        while parent:
            abs_location += (parent.location)
            parent = parent.parent
        return abs_location

    def find_parent_tree(self, node):
        """Find the root node tree through parent groups"""
        if node.id_data.users == 1:  # Check if it's a node group
            for mat in bpy.data.materials:
                if mat.node_tree:
                    for n in mat.node_tree.nodes:
                        if n.type == 'GROUP' and n.node_tree == node.id_data:
                            return self.find_parent_tree(n)
        return node.id_data

    def get_active_node(self, context):
        """Safely get the active node from context"""
        # Try to get from node editor first
        for area in context.screen.areas:
            if area.type == 'NODE_EDITOR':
                if area.spaces.active and area.spaces.active.node_tree:
                    return area.spaces.active.node_tree.nodes.active
        
        # Fallback to material's active node
        if context.object and context.object.active_material:
            return context.object.active_material.node_tree.nodes.active
        
        return None

    def execute(self, context):
        if not hasattr(context.scene, 'noise_generator_last_image'):
            self.report({'ERROR'}, "No generated image exists")
            return {'CANCELLED'}
        
        image = bpy.data.images.get(context.scene.noise_generator_last_image)
        if not image:
            self.report({'ERROR'}, "Image not found")
            return {'CANCELLED'}

        obj = context.object
        if not obj or not obj.active_material:
            self.report({'ERROR'}, "No active object or material")
            return {'CANCELLED'}

        mat = obj.active_material
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Get the active node safely
        active_node = self.get_active_node(context)
        node_tree = mat.node_tree

        # If inside a node group, find the parent tree
        if active_node and active_node.id_data != mat.node_tree:
            node_tree = self.find_parent_tree(active_node)

        # Create texture node in the correct tree
        tex_node = node_tree.nodes.new('ShaderNodeTexImage')
        tex_node.image = image

        # Positioning logic
        if active_node:
            # Direct relative positioning
            if active_node.parent and active_node.parent.type == 'FRAME':
                frame = active_node.parent
                tex_node.parent = frame  # Parent first
                # Use frame-relative coordinates directly
                tex_node.location = (active_node.location.x - 300, 
                                    active_node.location.y)
            else:
                # Standard positioning
                tex_node.location = (active_node.location.x - 300,
                                    active_node.location.y)
        else:
            # Fallback positioning
            output_node = next((n for n in node_tree.nodes 
                              if isinstance(n, bpy.types.ShaderNodeOutputMaterial)), None)
            if output_node:
                tex_node.location = (output_node.location.x - 300, 
                                   output_node.location.y)

        # Ensure frame expansion
        if tex_node.parent and tex_node.parent.type == 'FRAME':
            tex_node.parent.update()

        # Force UI update
        context.area.tag_redraw()
        
        return {'FINISHED'}