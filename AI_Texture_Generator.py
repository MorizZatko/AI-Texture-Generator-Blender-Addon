import bpy
import urllib.request
import urllib.parse
import os
import json
import base64
import time
import traceback


comfy_url = "http://127.0.0.1:8188"
base_save_dir = os.path.expanduser(r"E:\Blender\Assets\Download_API")

workflow_json = {
  "3": {
    "inputs": {
      "seed": 532752441413155,
      "steps": 20,
      "cfg": 4.5,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1,
      "model": [
        "4",
        0
      ],
      "positive": [
        "6",
        0
      ],
      "negative": [
        "7",
        0
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "4": {
    "inputs": {
      "ckpt_name": "sd3.5_medium_incl_clips_t5xxlfp8scaled.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "5": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "6": {
    "inputs": {
      "text": "A seamless texture of a fine sandblasted anodized aluminum surface, matte dark charcoal gray with a subtle metallic zinc sheen, matching the rugged chassis of an electronic music hardware sampler. Top-down flat macro photography, orthogonal view, perfectly even studio lighting, zero shadows, high detail metallic micro-texture, tileable material pattern.",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "7": {
    "inputs": {
      "text": "blurry, low quality",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "9": {
    "inputs": {
      "texture_name": "MyTexture",
      "seamless_mode": "seamless",
      "normal_strength": 1,
      "normal_invert_y": True,
      "roughness_min": 0,
      "roughness_max": 1,
      "metallic_min": 0,
      "metallic_max": 1,
      "metallic_threshold": 0.15,
      "ao_blur": 2,
      "ao_strength": 1,
      "save_textures": True,
      "image": [
        "8",
        0
      ]
    },
    "class_type": "QFXPBRGenerator",
    "_meta": {
      "title": "PBR Generator"
    }
  },
  "10": {
    "inputs": {
      "filename_prefix": "Nor",
      "images": [
        "9",
        1
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "11": {
    "inputs": {
      "filename_prefix": "Rough",
      "images": [
        "9",
        2
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "//": {
    "inputs": {
      "filename_prefix": "Diff",
      "images": [
        "9",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  }
}            

def download_comfy_image(prompt):
    folder_name = "".join([c if c.isalnum() else "_" for c in prompt[:20]])
    current_save_dir = os.path.join(base_save_dir, folder_name)
    os.makedirs(current_save_dir, exist_ok=True)
    
    map_nodes = {
        "diffuse": "//", 
        "roughness": "11", 
        "normal": "10"
    }
    
    try:
        print(f"---DEBUG START---")
        
        url = "http://127.0.0.1:8188/prompt"
        workflow_json["6"]["inputs"]["text"] = prompt
        payload = json.dumps({"prompt": workflow_json}).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode())
            prompt_id = res_json['prompt_id']
        
            print(f"1. Prompt ID erhalten: {prompt_id}")
        
        downloaded_files = {}
        
        while len(downloaded_files) < len(map_nodes):
            try:
                with urllib.request.urlopen(f"{comfy_url}/history/{prompt_id}") as r:
                    history = json.loads(r.read().decode())
                    if prompt_id in history:
                        node_id = "//"
                        outputs = history[prompt_id]['outputs']
                        for map_type, node_id in map_nodes.items():
                            if node_id in outputs and map_type not in downloaded_files:
                                filename = outputs[node_id]['images'][0]['filename']
                                
                                
                                full_img_url = f"{comfy_url}/view?filename={filename}"
                                save_path = os.path.join(current_save_dir, f"{map_type}_{filename}")
                                
                                with urllib.request.urlopen(full_img_url) as img_r:
                                    with open(save_path, "wb") as f:
                                        f.write(img_r.read())
                                
                                downloaded_files[map_type] = save_path
                                print(f"Download erfolgreich: {map_type} -> {save_path}")
                                
            except Exception as e:
                print(f"Warte auf Bilder... ({e})")
            time.sleep(1)
            
        return downloaded_files
    
    
    except Exception as e:
        print("--- ECHTER FEHLER START ---")
        print(traceback.format_exc())
        print("--- ECHTER FEHLER ENDE ---")   
        return None
    
    
def create_ai_material(prompt, paths):
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
    
    # Roughness
    if "roughness" in paths:
        rough_node = nodes.new(type="ShaderNodeTexImage")
        rough_node.location = (principled_node.location.x -400, principled_node.location.y -200)
        rough_node.image = bpy.data.images.load(paths["roughness"])
        rough_node.image.colorspace_settings.name = 'Non-Color'
        links.new(rough_node.outputs["Color"], principled_node.inputs["Roughness"])
    
    # Normal (Bump)
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
        self.report({'INFO'}, "AI is thinking... Blender my freeze!")
        
        try:
            image_path = download_comfy_image(prompt)
            create_ai_material(prompt, image_path)
            self.report({'INFO'}, "Material successfully created!")
        except Exception as e:
            self.report({'ERROR'}, f"AI failed to deliver image. Check Console!")
        return {'FINISHED'}
        

bpy.types.Scene.ai_texture_prompt = bpy.props.StringProperty(name='Prompt', default='rusty metal')
classes = [VIEW3D_PT_ai_texture_generator, TEXTURE_OT_generate_ai_material]       
        
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls) 
        
if __name__ == "__main__":
    register()