import sys

def apply_markers_and_replace(target_file_path, new_logic_file_path, output_file_path):
    try:
        with open(target_file_path, 'r') as f:
            content = f.readlines()

        start_marker = "    # MARKER_START\n"
        end_marker = "    # MARKER_END\n"

        start_index = -1
        end_index = -1

        for i, line in enumerate(content):
            if line == start_marker:
                start_index = i
            if line == end_marker:
                end_index = i
                break

        if start_index == -1 or end_index == -1:
            print("Error: Start or end marker not found in target file.")
            sys.exit(1)
            
        with open(new_logic_file_path, 'r') as f_new:
            new_code_block_content = f_new.read()

        new_file_content_lines = content[:start_index] + [new_code_block_content] + content[end_index + 1:]
        new_file_content = "".join(new_file_content_lines)

        with open(output_file_path, 'w') as f_out:
            f_out.write(new_file_content)

        print(f"Successfully applied new logic to '{target_file_path}' and saved to '{output_file_path}'")
        sys.exit(0)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python get_markers_and_replace.py <target_file_path> <new_logic_file_path> <output_file_path>")
        sys.exit(1)
    
    target_file = sys.argv[1]
    new_logic_file = sys.argv[2]
    output_file = sys.argv[3]
    apply_markers_and_replace(target_file, new_logic_file, output_file)
