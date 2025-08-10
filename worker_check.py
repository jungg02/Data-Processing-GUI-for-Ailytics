import json

def uncontained_ppe(file_path, filename, _, app):
    contained_classes = [
        "boot", "bumpcap", "glove", "hardhat",
        "lifevest", "longvest", "overalls", "safetyharness", "vest"
    ]
    with open(file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
        file_workers = []
        file_contained_classes = []

        for shape in data["shapes"]:
            x1, y1 = shape["points"][0]
            x2, y2 = shape["points"][1]
            x_min, x_max = min(x1, x2), max(x1, x2)
            y_min, y_max = min(y1, y2), max(y1, y2)

            if shape["label"] == "worker":
                file_workers.append((x_min, x_max, y_min, y_max))
            elif shape["label"] in contained_classes:
                file_contained_classes.append((shape["label"], x_min, x_max, y_min, y_max))

        for label, x_min, x_max, y_min, y_max in file_contained_classes:
            label_area = (x_max - x_min) * (y_max - y_min)
            partially_contained = False
            for wx_min, wx_max, wy_min, wy_max in file_workers:
                # Compute intersection coordinates
                inter_x_min = max(x_min, wx_min)
                inter_x_max = min(x_max, wx_max)
                inter_y_min = max(y_min, wy_min)
                inter_y_max = min(y_max, wy_max)

                inter_width = max(0, inter_x_max - inter_x_min)
                inter_height = max(0, inter_y_max - inter_y_min)
                intersection_area = inter_width * inter_height

                # Skip if no intersection
                if intersection_area == 0:
                    continue

                # Check if fully inside
                fully_contained = (
                    x_min >= wx_min and x_max <= wx_max and
                    y_min >= wy_min and y_max <= wy_max
                )

                # Check if intersection covers more than 50% of the label area,
                # but it's not fully contained
                if (intersection_area / label_area) > 0.5 and not fully_contained:
                    partially_contained = True
                    break

            if partially_contained:
                app.log( f"{filename} contains '{label}' bbox with coordinates (({x_min:.1f},{y_min:.1f}),({x_max:.1f},{y_max:.1f})) that is not bounded in a 'worker' bbox", error = True)
