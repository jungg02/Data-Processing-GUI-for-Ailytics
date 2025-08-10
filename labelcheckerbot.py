from PIL import Image
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, scrolledtext
import os
import json
from worker_check import uncontained_ppe
from resize_images import resize_images
from convert_img_to_jpg import change_ext
from remove_imagedata import remove_image_data
import threading

keys = ["boot","bumpcap","glove","hardhat","lifeline","carabiner","lifevest","longvest","overalls","safetyharness","vest","worker",
        "barricade","beam","bin","compressor","concretebucket","formwork","frame","hook_top","householdshelter","pipe","precastplank",
        "precastroof", "rebar", "scaffold","scaffolding","tank","timber","wall","windowfacade","boomlift","bus","car","crane","excavator",
        "forklift","loader","mixer","motorcycle","pilier","roller","scissorlift","truck","aframeladder_m","barricade_m","blockade_m",
        "compressor_m","cone_m","platformladder_m","spotlight_m","straightladder_m","open_edge","box","fire", "smoke"]

loads = ["barricade","beam","bin","compressor","concretebucket","formwork","frame","hook_top","householdshelter","pipe","precastplank",
        "precastroof", "rebar", "scaffold","scaffolding","tank","timber","wall","windowfacade"]


class LabelCheckerBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LabelCheckerBot")
        self.root.geometry("900x600")

        self.file_checkboxes = {}
        self.selected_files = []
        self.all_selected = False
        self.scripts = {"Reduce File Size": remove_image_data, 
                        "Resize Images": resize_images,
                        "Convert to JPG": change_ext }
        self.classes =  dict.fromkeys(keys, 0)

        self.setup_ui()
    
    def setup_ui(self):
        # Layout frames
        self.bottom_frame = tb.Frame(self.root, height=150, width=400)
        self.bottom_frame.pack(side=tb.BOTTOM, fill=tb.X, padx=10, pady=5)

        self.left_frame = tb.Frame(self.root, width=300)
        self.left_frame.pack(side=tb.LEFT, fill=tb.Y, padx=10, pady=10)

        self.right_frame = tb.Frame(self.root)
        self.right_frame.pack(side=tb.RIGHT, fill=tb.BOTH, expand=True, padx=10, pady=10)

        # ----- Left Panel: Scripts -----
        
        tb.Button(self.left_frame, text="Apply General Check", bootstyle="primary", command=self.general_check).pack(pady=10, fill="x")
        tb.Button(self.left_frame, text="Get Summary", bootstyle="info", command=self.get_summary).pack(pady=10, fill="x")

        tb.Label(self.left_frame, text="Search for Label", font=('Arial', 12, 'bold')).pack(pady=(20, 5))
        self.search_entry = tb.Entry(self.left_frame)
        self.search_entry.pack(fill="x", padx=5)
        tb.Button(self.left_frame, text="Search Label", bootstyle="warning", command=self.search_label).pack(pady=5, fill="x")

        tb.Label(self.left_frame, text="Scripts", font=('Arial', 12, 'bold')).pack(pady=5)
        self.script_vars = {}
        for script_name in self.scripts:
            var = tb.BooleanVar()
            cb = tb.Checkbutton(self.left_frame, text=script_name, variable=var, bootstyle="round-toggle")
            cb.pack(fill="x", padx=5, anchor="w")
            self.script_vars[script_name] = var

        tb.Button(self.left_frame, text="Apply Selected Scripts", bootstyle="success", command=self.apply_selected_scripts).pack(pady=20, fill="x")
       
        # ----- Right Panel: File Management -----
        tb.Button(self.right_frame, text="Browse Folder", bootstyle="warning", command=self.browse_folder).pack(pady=10)
        self.folder_label = tb.Label(self.right_frame, text="No folder selected", wraplength=400)
        self.folder_label.pack(pady=5)

        self.selection_buttons_frame = tb.Frame(self.right_frame)
        self.selection_buttons_frame.pack(pady=5)

        self.select_all_button = tb.Button(self.selection_buttons_frame, text="Select All", command=self.toggle_select_all)
        self.select_all_button.pack(side="left", padx=5)

        self.select_jpeg_button = tb.Button(self.selection_buttons_frame, text="Select All JPEG", command=self.select_all_jpeg)
        self.select_jpeg_button.pack(side="left", padx=5)

        self.select_json_button = tb.Button(self.selection_buttons_frame, text="Select All JSON", command=self.select_all_json)
        self.select_json_button.pack(side="left", padx=5)

        # Scrollable file list area
        self.canvas = tb.Canvas(self.right_frame)
        self.scrollbar = tb.Scrollbar(self.right_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tb.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tb.LEFT, fill=tb.BOTH, expand=True)
        self.scrollbar.pack(side=tb.RIGHT, fill=tb.Y)

        # ----- Bottom Panel: Error Output / Log -----
        tb.Label(self.bottom_frame, text="Labelling Errors", font=('Arial', 10, 'bold')).pack(anchor="w")
        self.log_area = scrolledtext.ScrolledText(self.bottom_frame, height=6, wrap="word", state="disabled")
        self.log_area.pack(fill=tb.BOTH, expand=True)

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_label.config(text=folder_path)
            self.load_files(folder_path)

    def load_files(self, folder_path):
        # Clear previous
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.file_checkboxes.clear()

        for filename in os.listdir(folder_path):
            full_path = os.path.join(folder_path, filename)
            if os.path.isfile(full_path):
                var = tb.BooleanVar()
                var.trace_add("write", lambda *_: self.update_selected_files())
                cb = tb.Checkbutton(self.scrollable_frame, text=filename, variable=var)
                cb.pack(fill="x", padx=5, anchor="w")
                self.file_checkboxes[full_path] = var

        self.update_selected_files()

    def update_selected_files(self):
        self.selected_files = [f for f, var in self.file_checkboxes.items() if var.get()]

    def toggle_select_all(self):
        self.all_selected = not self.all_selected
        for var in self.file_checkboxes.values():
            var.set(self.all_selected)
        self.select_all_button.config(text="Deselect All" if self.all_selected else "Select All")
        self.update_selected_files()
        self.log(f"Selected files: {len(self.selected_files)}")

    def select_all_jpeg(self):
        count = 0
        for filepath, var in self.file_checkboxes.items():
            if filepath.lower().endswith((".jpg", ".jpeg")):
                var.set(True)
                count += 1
            else:
                var.set(False)
        self.update_selected_files()
        self.select_all_button.config(text="Deselect All")
        self.all_selected = True
        self.log(f"Selected {count} JPEG files.")

    def select_all_json(self):
        count = 0
        for filepath, var in self.file_checkboxes.items():
            if filepath.lower().endswith(".json"):
                var.set(True)
                count += 1
            else:
                var.set(False)
        self.update_selected_files()
        self.select_all_button.config(text="Deselect All")
        self.all_selected = True
        self.log(f"Selected {count} JSON files.")


    def apply_selected_scripts(self):
        self.log("Applying scripts...")
        if not self.selected_files:
            self.log("⚠️ No files selected.", error=True)
            return

        selected_scripts = [self.scripts[name] for name, var in self.script_vars.items() if var.get()]
        if not selected_scripts:
            self.log("⚠️ No scripts selected.", error=True)
            return

        for file_path in self.selected_files:
            filename = os.path.basename(file_path)
            for script in selected_scripts:
                if "error" in file_path.lower():
                    self.log(f"[{script}] Error found in {filename}", error=True)
                else:
                    script(file_path, filename, os.path.dirname(file_path), self)

    def general_check(self):
        threading.Thread(target=self._general_check_thread, daemon=True).start()

    def _general_check_thread(self):
        self.root.after(0, lambda: self.log("Performing general check..."))
        if not self.selected_files:
            self.root.after(0, lambda: self.log("⚠️ No files selected.", error=True))
            return

        else:
            for filepath in self.selected_files:
                filename = os.path.basename(filepath)
                valid = True
                if filepath.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff")):
                    current_image = Image.open(filepath)
                    aspect_ratio = 16 / 9
                    width, height = current_image.size
                    if not (width >= 1920 and (width / height) == aspect_ratio):
                        self.root.after(0, lambda f=filename: self.log(f"{f} is in the wrong dimensions", error=True))
                        valid = False
                    if not filepath.lower().endswith((".jpg", ".jpeg")):
                        self.root.after(0, lambda f=filename: self.log(f"{f} not in jpeg/jpg format", error=True))
                        valid = False
                elif filepath.lower().endswith(".json"):
                    uncontained_ppe(filepath, filename, os.path.dirname(filepath), self)
                    with open(filepath, "r", encoding="utf-8") as json_file:
                        data = json.load(json_file)
                        seen = {}
                        for shape in data["shapes"]:
                            specific_class = shape["label"]
                            points = shape["points"]
                            (x1, y1), (x2, y2) = points[0], points[1]
                            x, y = min(x1, x2), min(y1, y2)
                            w, h = abs(x2 - x1), abs(y2 - y1)
                            area = round(w * h, 2)
                            key = (specific_class, area)
                            if key in seen:
                                self.root.after(0, lambda f=filename, l=specific_class: self.log(f"{f} has duplicate label '{l}' with same area", error=True))
                                valid = False
                            else:
                                seen[key] = 1
                            if specific_class not in keys:
                                    self.root.after(0, lambda f=filename, l=specific_class: self.log(f"{f} contains unknown class: {l}", error=True))
                                    valid = False
                            if specific_class in loads:
                                if len(shape["points"]) != 4 & len(shape["points"]) != 2:
                                    self.root.after(0, lambda f=filename, l=specific_class: self.log(f"{f} has invalid bbox for {l}", error=True))
                                    valid =  False
                else:
                    self.root.after(0, lambda f=filename: self.log(f"{f} in incorrect format", error=True))
                if valid == True:
                    self.root.after(0, lambda f=filename: self.log(f"Checked ✅ : {f}"))

    def get_summary(self):
        threading.Thread(target=self._get_summary_thread, daemon=True).start()

    def _get_summary_thread(self):
        self.root.after(0, lambda: self.log("Generating Summary..."))
        if self.selected_files == []:
            self.root.after(0, lambda: self.log("⚠️ No files selected.", error=True))
        else:
            for filepath in self.selected_files:
                if filepath.lower().endswith(".json"):
                    with open(filepath, "r", encoding="utf-8") as json_file:
                        data = json.load(json_file)
                        for shape in data["shapes"]:
                            specific_class = shape["label"]
                            if specific_class in keys:
                                self.classes[specific_class] += 1
            for key, value in self.classes.items():
                if value > 0:
                    self.root.after(0, lambda l=key, c=value: self.log(f"{l}: {c}"))
        self.classes = dict.fromkeys(keys, 0)

    def search_label(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            self.log("⚠️ Enter a label to search.", error=True)
            return

        self.log(f"Searching for label: '{query}'...")
        found = False

        for filepath in self.selected_files:
            if filepath.lower().endswith(".json"):
                with open(filepath, "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)
                    labels_in_file = [shape["label"].lower() for shape in data.get("shapes", [])]
                    if query in labels_in_file:
                        filename = os.path.basename(filepath)
                        self.log(f"✅ Label '{query}' found in {filename}")
                        found = True

        if not found:
            self.log(f"❌ Label '{query}' not found in selected files.", error=True)


    def log(self, message, error=False):
        self.log_area.configure(state="normal")
        self.log_area.insert(tb.END, ("[ERROR] " if error else "") + message + "\n")
        self.log_area.see(tb.END)
        self.log_area.configure(state="disabled")
    

# Run app
if __name__ == "__main__":
    root = tb.Window(themename="superhero")
    app = LabelCheckerBotApp(root)
    root.mainloop()
