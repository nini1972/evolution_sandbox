
import os
import re
import json
import colony_lib.morphospace

def analyze_gray_scott_patterns():
    # Updated image_dir to point to the shared World C artifacts directory
    # and the specific job that generated the images.
    image_dir = "../../shared_space/world_c/artifacts/job_llama_3_3_1791426134_4acc/"
    results = []

    # List of files to process, explicitly filtering for the Gray-Scott patterns
    gray_scott_files = [
        f for f in os.listdir(image_dir) 
        if f.startswith("gray_scott_F") and f.endswith(".png") 
    ]

    for filename in gray_scott_files:
        filepath = os.path.join(image_dir, filename)
        match = re.match(r"gray_scott_F(\d+\.\d+)_k(\d+\.\d+)\.png", filename)
        if match:
            F_val = float(match.group(1))
            k_val = float(match.group(2))

            print(f"Analyzing {filename} (F={F_val}, k={k_val})...")
            try:
                # Assuming generate_persistence_curve takes a filepath and returns curve data
                persistence_curve_data = colony_lib.morphospace.generate_persistence_curve(filepath)
                results.append({
                    "filename": filename,
                    "F": F_val,
                    "k": k_val,
                    "persistence_curve": persistence_curve_data
                })
                print(f"Successfully processed {filename}.")
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                results.append({
                    "filename": filename,
                    "F": F_val,
                    "k": k_val,
                    "error": str(e)
                })

    # Save results to a JSON file
    output_path = "morphospace_persistence_analysis.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Analysis complete. Results saved to {output_path}")

if __name__ == "__main__":
    analyze_gray_scott_patterns()
