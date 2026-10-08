import os
import re

output_dir = "world_c_results"
html_file_path = os.path.join(output_dir, "morphospace_gallery.html")

# Get all PNG files in the output directory that match the parameter sweep pattern
png_files = [f for f in os.listdir(output_dir) if f.startswith('gray_scott_F') and f.endswith('.png')]

# Sort files based on F and k values extracted from their names
def extract_params(filename):
    match = re.search(r'F([0-9.]+)_k([0-9.]+)', filename)
    if match:
        return float(match.group(1)), float(match.group(2))
    return 0.0, 0.0 # Default if no match

sorted_png_files = sorted(png_files, key=extract_params)


html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Gray-Scott Morphospace Gallery</title>
    <style>
        body { font-family: sans-serif; }
        .gallery { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
        .gallery-item { border: 1px solid #ccc; padding: 5px; text-align: center; }
        .gallery-item img { max-width: 100%; height: auto; }
    </style>
</head>
<body>
    <h1>Gray-Scott Morphospace Gallery</h1>
    <div class="gallery">
"""

for filename in sorted_png_files:
    F, k = extract_params(filename)
    # The image path in the HTML should be relative to the HTML file itself
    # Since HTML file is in world_c_results, and images are in world_c_results,
    # the path is just the filename.
    html_content += f"""
        <div class="gallery-item">
            <img src="{filename}" alt="Gray-Scott F={F:.4f} k={k:.4f}">
            <p>F={F:.4f}<br>k={k:.4f}</p>
        </div>
"""

html_content += """
    </div>
</body>
</html>
"""

with open(html_file_path, "w") as f:
    f.write(html_content)

print(f"Generated morphospace gallery at {html_file_path}")