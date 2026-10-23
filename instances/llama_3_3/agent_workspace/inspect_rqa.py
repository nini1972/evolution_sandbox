import colony_lib
import json
import inspect

inspection_results = {}

try:
    from colony_lib.recurrence import rqa
    signature = inspect.signature(rqa)
    inspection_results['rqa_signature'] = str(signature)
except Exception as e:
    inspection_results['rqa_signature'] = f"Error: {e}"

# Save results to JSON
output_filename = "rqa_signature_inspection.json"
with open(output_filename, 'w') as f:
    json.dump(inspection_results, f, indent=4)

print(f"rqa signature inspection completed. Results saved to {output_filename}")
