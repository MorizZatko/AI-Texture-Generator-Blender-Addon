print("!!! Blender läd die neue Version !!!")

import bpy
import importlib
from . import ui, api_client, material_logic

bl_info = {
    "name": "AI Texture Generator",
    "category": "Material",
    "blender": (4, 0, 0)
}

def register():
    importlib.reload(ui)
    importlib.reload(api_client)
    importlib.reload(material_logic)
    bpy.types.Scene.ai_texture_prompt = bpy.props.StringProperty(
        name="Prompt",
        default="rusty metal"
    )
    bpy.types.Scene.ai_texture_save_path = bpy.props.StringProperty(
        name="Save Path",
        subtype='DIR_PATH',
        default="C:\\Blender\Assets"
    )
    ui.register()

def unregister():
    ui.unregister()
    del bpy.types.Scene.ai_texture_prompt