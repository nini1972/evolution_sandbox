import colony_lib
import json
import inspect

inspection_results = {}

try:
    from colony_lib.recurrence import takens_embedding
    signature = inspect.signature(takens_embedding)
    inspection_results['takens_embedding_signature'] = str(signature)
except Exception as e:
    inspection_results['takens_embedding_signature'] = f"Error: {e}"

# Save results to JSON
output_filename = "takens_embedding_signature_inspection.json"
with open(output_filename, 'w') as f:
    json.dump(inspection_results, f, indent=4)

print(f"takens_embedding signature inspection completed. Results saved to {output_filename}")
