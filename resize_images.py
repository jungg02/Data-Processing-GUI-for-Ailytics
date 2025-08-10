from PIL import Image
import os

def resize_images(filepath, filename, folder_path, app):
    width = 1920
    height = 1080

    # create new directory for resized images
    save_image_path = f"{folder_path}/resized_images"
    if not os.path.exists(save_image_path):
       os.makedirs(save_image_path)
    try:
        if filepath.endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff")):
            try:
                # Open and resize the image
                image = Image.open(filepath)
                width_original, height_original = image.size
                if width_original == width and height_original == height:
                    app.log(f"skipping {filename} because it is already in specified dimensions")
                else:
                    resized_image = image.resize((width, height))
                    resized_image.save(rf"{save_image_path}/{filename}")
                    app.log(f"{filename} has been resized")
            except Exception as e:
                app.log(f"Error resizing {filename}: {e}")
        else:
            app.log(f"{filename} is an invalid input", error = True)

    except Exception as e:
        app.log(f"Error processing the folder: {e}")
    return


