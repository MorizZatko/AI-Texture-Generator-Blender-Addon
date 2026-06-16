"""AI Texture Generator - Main Entry.

This module coordinates the registration and initialisation of the addon.
It handles the setup of scene properties, module reloading for development,
and registration of the user interface.
"""

import bpy
import importlib
from . import ui, api_client, material_logic


# Blender addon metadata
bl_info = {
    "name": "AI Texture Generator",
    "author": "Moriz Zatko",
    "version": (1, 0),
    "blender": (5, 1, 0),
    "location": "VIEW3D > N-Panel > AI Texture",
    "description": "Generates PBR textures via ComfyUI API and sets up material node tree automatically.",
    "category": "Material"
}

def register():
    """
    Register the addon and its components.

    This function forces a reload of all sub-modules to ensure
    that the latest changes are applied without needing a Blender restart.
    Initializes the necessary scene properties.
    """
    # Force reload of modules
    importlib.reload(ui)
    importlib.reload(api_client)
    importlib.reload(material_logic)

    # Initialize scene properties for user input and configuration
    bpy.types.Scene.ai_texture_prompt = bpy.props.StringProperty(
        name="Prompt",
        default="rusty metal"
    )
    bpy.types.Scene.ai_texture_save_path = bpy.props.StringProperty(
        name="Save Path",
        subtype='DIR_PATH',
        default="C:\\Blender\Assets"
    )

    # Register UI panels and operators
    ui.register()

def unregister():
    """
    Unregister the addon and cleans up the Blender environment.

    Remove UI elements and deletes texture prompt amd save path properties to keep Blender data clean.
    """
    ui.unregister()
    del bpy.types.Scene.ai_texture_prompt
    del bpy.types.Scene.ai_texture_save_path