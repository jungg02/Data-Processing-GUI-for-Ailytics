"""
Script to take in a folder with images and convert all images to 'jpg' extension.
"""
import os
from PIL import Image

def change_ext(filepath, filename, folder_path, app):
    if filepath.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff")):
        if filepath.lower().endswith((".jpg", ".jpeg")):
            app.log(f"{filename} is already jpg, skipping...")
            return
        im = Image.open(filename)
        rgb_im = im.convert("RGB")
        rgb_im.save(rf"{folder_path}/{filename}.jpg")
        app.log(f"{filename} ---> {filename}.jpg SUCCESS")
        os.rename(filename, f"{folder_path}/{os.path.basename(filename)}")
    else:
        app.log(f"{filename} is an invalid input", error = True)
    return 


