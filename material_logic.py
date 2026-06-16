"""Material Logic Module.

This module handles the PBR material node construction.
"""

import bpy


def create_ai_material(prompt, paths):
    """Construct a complete PBR material node tree.

    For: Diffuse, Roughness and Normal/Bump.
    
    Args:
        prompt (str): Text description of the texture.
        paths (dict): Dictionary containing file paths for the received maps.

    Returns:
        material (bpy.types.material): The newly created material object. 
    """
    mat_name = f"AI_{prompt[:10]}"
    material = bpy.data.materials.get(mat_name) or bpy.data.materials.new(name=mat_name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    links = material.node_tree.links
    
    # Base Node
    output_node = nodes.new(type="ShaderNodeOutputMaterial")
    principled_node = nodes.new(type="ShaderNodeBsdfPrincipled")
    principled_node.location, output_node.location = (0, 0), (300, 0)
    links.new(principled_node.outputs["BSDF"], output_node.inputs["Surface"])
    
    # Diffuse
    if "diffuse" in paths:
        diff_node = nodes.new(type="ShaderNodeTexImage")
        diff_node.location = (principled_node.location.x -400, principled_node.location.y +200)
        diff_node.image = bpy.data.images.load(paths["diffuse"])
        links.new(diff_node.outputs["Color"], principled_node.inputs["Base Color"])
    
    # Roughness:
        # Set to 'Non-Color' to ensure grayscale values are interpreted correctly
    if "roughness" in paths:
        rough_node = nodes.new(type="ShaderNodeTexImage")
        rough_node.location = (principled_node.location.x -400, principled_node.location.y -200)
        rough_node.image = bpy.data.images.load(paths["roughness"])
        rough_node.image.colorspace_settings.name = 'Non-Color'
        links.new(rough_node.outputs["Color"], principled_node.inputs["Roughness"])
    
    # Normal:
        # Using a Bump node to convert grayscale height data into surface normals.
        # Set to grayscale ('Non-Color') for linear data interpretation.
    if "normal" in paths:
        nor_img_node = nodes.new(type="ShaderNodeTexImage")
        nor_img_node.location = (principled_node.location.x -400, principled_node.location.y -500)   
        nor_img_node.image = bpy.data.images.load(paths["normal"])
        nor_img_node.image.colorspace_settings.name = 'Non-Color'
    
        bump = nodes.new(type="ShaderNodeBump")
        bump.location = (principled_node.location.x -200, principled_node.location.y -200)
        links.new(nor_img_node.outputs["Color"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], principled_node.inputs["Normal"])
    
    return material