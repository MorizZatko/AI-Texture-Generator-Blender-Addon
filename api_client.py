"""API Client Module.

This module handles all communication with the ComfyUI API,
including workflow submission and image retrieval.
"""

import urllib.request
import os
import json
import time


comfy_url = "http://127.0.0.1:8188"

def load_workflow():
    """Load workflow JSON file for the AI model."""
    base_path = os.path.dirname(__file__)
    json_path = os.path.join(base_path, "workflow.json")
    if not os.path.exists(json_path):
        print(f"DEBUG: JSON not found! {json_path}")
        return None
    with open(json_path, 'r') as f:
        workflow_data = json.load(f)
        return workflow_data

def download_comfy_image(prompt, save_dir):
    """Send prompt to ComfyUI and downloads the generated PBR maps.

    Args:
        prompt (str): The text description of the texture.
        save_dir (str): Path to the directory where maps should be stored.

    Returns:
        downloaded_files (dict): A dictionary mapping map types (Diffuse, etc) to their local file paths.
    """
    workflow_data = load_workflow()
    if workflow_data is None:
        return None
    
    # Setup new directory for the asset
    folder_name = "".join([c if c.isalnum() else "_" for c in prompt[:20]])
    current_save_dir = os.path.join(save_dir, folder_name)
    os.makedirs(current_save_dir, exist_ok=True)
    
    # Nodes to save each final map
    map_nodes = {
        "diffuse": "//", 
        "roughness": "11", 
        "normal": "10"
    }
    
    print(f"---DEBUG START---")
    
    # Send prompt to ComfyUI API
    url = "http://127.0.0.1:8188/prompt"
    workflow_data["6"]["inputs"]["text"] = prompt
    payload = json.dumps({"prompt": workflow_data}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})

    # Receive prompt id as response  
    with urllib.request.urlopen(req) as response:
        res_json = json.loads(response.read().decode())
        prompt_id = res_json['prompt_id']
        print(f"1. Received prompt ID: {prompt_id}")
        
    downloaded_files = {}

    # Start timeout process  
    start_time = time.time()
    timeout_seconds = 300

    # Download process
    while len(downloaded_files) < len(map_nodes):
        if time.time() - start_time > timeout_seconds:
            print(f"ERROR: Timeout! ComfyUI does not answer...")
            return None
        try:
            # Open and read ComfyUI history to check and download each map
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
                            print(f"Download succesful: {map_type} -> {save_path}")
                                
        except Exception as e:
            print(f"Waiting for images... ({e})")
        time.sleep(1)
            
    return downloaded_files