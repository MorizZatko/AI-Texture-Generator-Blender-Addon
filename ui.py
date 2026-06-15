import bpy
from . import api_client
from . import material_logic


class VIEW3D_PT_ai_texture_generator(bpy.types.Panel):
    bl_label = "AI Texture Generator"
    bl_idname = "VIEW3D_PT_ai_texture_generator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AI Texture"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "ai_texture_prompt")
        layout.operator("texture.generate_ai_material", text="Generate Material")


class TEXTURE_OT_generate_ai_material(bpy.types.Operator):
    bl_idname = "texture.generate_ai_material"
    bl_label = "Generate AI Material"
    
    def execute(self, context):
        prompt = context.scene.ai_texture_prompt
        prefs = context.preferences.addons[__package__].preferences
        save_dir = prefs.save_path
        self.report({'INFO'}, "AI is thinking... Blender my freeze!")
        
        try:
            paths = api_client.download_comfy_image(prompt, save_dir)
            material_logic.create_ai_material(prompt, paths)
            self.report({'INFO'}, "Material successfully created!")
        except Exception as e:
            self.report({'ERROR'}, f"AI failed to deliver image. Check Console!")
        return {'FINISHED'}