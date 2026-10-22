import colony_lib
import json

def inspect_module(module, module_name):
    contents = []
    for item in dir(module):
        if not item.startswith('__'):
            contents.append(item)
    return {module_name: contents}

inspection_results = {}

# Inspect top-level colony_lib
inspection_results.update(inspect_module(colony_lib, 'colony_lib'))

# Try to inspect colony_lib.recurrence if it exists
if hasattr(colony_lib, 'recurrence'):
    inspection_results.update(inspect_module(colony_lib.recurrence, 'colony_lib.recurrence'))
else:
    inspection_results['colony_lib.recurrence'] = 'Module not found'

# Save results to JSON
output_filename = "colony_lib_inspection_results.json"
with open(output_filename, 'w') as f:
    json.dump(inspection_results, f, indent=4)

print(f"colony_lib inspection completed. Results saved to {output_filename}")
