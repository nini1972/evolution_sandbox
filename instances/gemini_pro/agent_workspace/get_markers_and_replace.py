import sys

def get_markers_and_replace(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.readlines()

        start_marker_line = "    current_time = 0\n"
        end_marker_line = "    print(f\"Simulation \\\'{simulation_id}\\\' finished.\")\n"

        start_index = -1
        end_index = -1

        for i, line in enumerate(content):
            if line == start_marker_line:
                start_index = i
            if line == end_marker_line:
                end_index = i
                break # Assuming the first occurrence of end_marker_line is the correct one

        if start_index == -1 or end_index == -1:
            print("Error: Start or end marker not found.")
            print(f"Start marker: '{start_marker_line.strip()}'")
            print(f"End marker: '{end_marker_line.strip()}'")
            sys.exit(1)
            
        # Adjust start_index to capture from just after the start_marker_line
        old_code_block = "".join(content[start_index + 1 : end_index + 1])
        
        # Read new content from the separate file
        with open("new_simulation_logic.py", 'r') as f_new:
            new_code_block_content = f_new.read()

        print("---OLD_CODE_BLOCK_START---")
        print(old_code_block)
        print("---OLD_CODE_BLOCK_END---")
        print("---NEW_CODE_BLOCK_START---")
        print(new_code_block_content)
        print("---NEW_CODE_BLOCK_END---")

        sys.exit(0)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_markers_and_replace.py <file_path>")
        sys.exit(1)
    
    file_to_process = sys.argv[1]
    get_markers_and_replace(file_to_process)
