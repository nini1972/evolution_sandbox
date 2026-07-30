import os

catalog_file = 'ecosystem_catalog.txt'
current_files = os.listdir('../../shared_space/')

with open(catalog_file, 'r') as f:
    # This assumes the file contains the output of 'ls -R' which is not ideal for parsing.
    # Let me just re-save a simple list of filenames.
    pass

with open('file_listing_base.txt', 'w') as f:
    for filename in current_files:
        f.write(f"{filename}\n")

print("Ecosystem base updated.")
