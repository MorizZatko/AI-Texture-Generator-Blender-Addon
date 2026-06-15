import bpy
import urllib.request
import os
import json
import time
import traceback
from . import __init__
from . import workflow



def download_comfy_image(prompt):
    folder_name = "".join([c if c.isalnum() else "_" for c in prompt[:20]])
    current_save_dir = os.path.join(save_path, folder_name)
    os.makedirs(current_save_dir, exist_ok=True)
    
    map_nodes = {
        "diffuse": "//", 
        "roughness": "11", 
        "normal": "10"
    }
    
    try:
        print(f"---DEBUG START---")
        
        url = "http://127.0.0.1:8188/prompt"
        workflow.workflow_json["6"]["inputs"]["text"] = prompt
        payload = json.dumps({"prompt": workflow.workflow_json}).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode())
            prompt_id = res_json['prompt_id']
        
            print(f"1. Prompt ID erhalten: {prompt_id}")
        
        downloaded_files = {}
        
        while len(downloaded_files) < len(map_nodes):
            try:
                with urllib.request.urlopen(f"{__init__.comfy_url}/history/{prompt_id}") as r:
                    history = json.loads(r.read().decode())
                    if prompt_id in history:
                        node_id = "//"
                        outputs = history[prompt_id]['outputs']
                        for map_type, node_id in map_nodes.items():
                            if node_id in outputs and map_type not in downloaded_files:
                                filename = outputs[node_id]['images'][0]['filename']
                                
                                
                                full_img_url = f"{__init__.comfy_url}/view?filename={filename}"
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