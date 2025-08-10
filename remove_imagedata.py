import json

def remove_image_data(file_path,filename, folderpath, app):
    if file_path.lower().endswith(".json"):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        data["imageData"] = None

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            app.log(f"Removed 'imageData' from {filename}")
