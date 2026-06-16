"""User Interface Module.

This module handles the Blender UI,
as well as the prompt execution.
"""

import bpy
from . import api_client
from . import material_logic


class VIEW3D_PT_ai_texture_generator(bpy.types.Panel):
    """Initialize the 'N-Panel' window in Blender."""

    bl_label = "AI Texture Generator"
    bl_idname = "VIEW3D_PT_ai_texture_generator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AI Texture"
    
    def draw(self, context):
        """Initialize prompt and save path input."""
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "ai_texture_prompt")
        layout.prop(scene, "ai_texture_save_path")
        layout.operator("texture.generate_ai_material", text="Generate Material")


class TEXTURE_OT_generate_ai_material(bpy.types.Operator):
    """Blender operator manages the AI generation and PBR material construction pipeline."""

    bl_idname = "texture.generate_ai_material"
    bl_label = "Generate AI Material"
    
    def execute(self, context):
        """Triggers the AI generation and initialize material construction.

        Args:
            self: The operator instance.
            context (bpy.types.Context): Blender context providing access to the current scene.
        """
        prompt = context.scene.ai_texture_prompt
        save_dir = context.scene.ai_texture_save_path
        if not save_dir:
            self.report({'ERROR'}, "Please select a save path in the panel!")
            return {'CANCELLED'}
        try:
            # Manages the data flow: API Client -> Material Logic
            image_path = api_client.download_comfy_image(prompt, save_dir)
            if image_path is None:
                self.report({'ERROR'}, "API returned None!")
                return {'CANCELLED'}
            
            material_logic.create_ai_material(prompt, image_path)
            self.report({'INFO'}, "Material successfully created!")
        except Exception as e:
            self.report({'ERROR'}, f"API Error: {str(e)}")
            return {'FINISHED'}
        
        return {'FINISHED'}
classes = [
    VIEW3D_PT_ai_texture_generator,
    TEXTURE_OT_generate_ai_material
]

def register():
    """Register classes in Blender."""
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    """Unregister classes in Blender."""
    for cls in classes:
        bpy.utils.unregister_class(cls)