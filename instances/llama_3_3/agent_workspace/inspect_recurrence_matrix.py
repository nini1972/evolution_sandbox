import colony_lib
import json
import inspect

inspection_results = {}

try:
    from colony_lib.recurrence import recurrence_matrix
    signature = inspect.signature(recurrence_matrix)
    inspection_results['recurrence_matrix_signature'] = str(signature)
except Exception as e:
    inspection_results['recurrence_matrix_signature'] = f"Error: {e}"

# Save results to JSON
output_filename = "recurrence_matrix_signature_inspection.json"
with open(output_filename, 'w') as f:
    json.dump(inspection_results, f, indent=4)

print(f"recurrence_matrix signature inspection completed. Results saved to {output_filename}")
