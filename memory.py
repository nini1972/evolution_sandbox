import os
import json

def get_history_file():
    instance_name = os.getenv("ACTIVE_INSTANCE", "")
    if not instance_name:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "logs", "history.jsonl"))
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "instances", instance_name, "logs", "history.jsonl"))

def append_to_history(entry: dict):
    """Appends a new turn to the history log."""
    history_file = get_history_file()
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    with open(history_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')

def load_history() -> list:
    """Loads the entire history from the JSONL file."""
    history_file = get_history_file()
    if not os.path.exists(history_file):
        return []
    
    history = []
    with open(history_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    history.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return history
