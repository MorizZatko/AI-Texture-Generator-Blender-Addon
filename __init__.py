import bpy
from . import ui, api_client, material_logic

bl_info = {
    "name": "AI Texture Generator",
    "category": "Material",
    "blender": (4, 0, 0)
}


comfy_url = "http://127.0.0.1:8188"

class AI_Texture_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    save_path = bpy.props.StringProperty(
        name="Save Directory",
        subtype='DIR_PATH'
    )


def register():
    ui.register()
    api_client.register()
    material_logic.register()