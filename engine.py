import os
import sys
import io
import time
import argparse

# Force stdout/stderr to use UTF-8 and gracefully handle unprintable characters on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from llm_client import generate_next_action
from tools import TOOLS_SCHEMA, AVAILABLE_TOOLS
from memory import load_history, append_to_history

PROMPT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "config", "initial_prompt.txt"))

def run_loop(instance: str, ticks: int):
    # Set active instance environment variable
    os.environ["ACTIVE_INSTANCE"] = instance
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    instance_dir = os.path.join(base_dir, "instances", instance)
    
    # Check if instance exists (if it's not the default fallback)
    if instance and not os.path.exists(instance_dir):
        print(f"Error: Instance '{instance}' has not been set up. Run 'python setup_instance.py --name {instance}' first.")
        return

    # Ensure workspace directory exists (important for clean checkouts from git since git ignores empty folders)
    if instance:
        workspace_dir = os.path.join(instance_dir, "agent_workspace")
    else:
        workspace_dir = os.path.join(base_dir, "agent_workspace")
    os.makedirs(workspace_dir, exist_ok=True)

    # Load the initial system prompt
    if not os.path.exists(PROMPT_FILE):
        print(f"Error: Initial prompt not found at {PROMPT_FILE}")
        return
        
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        system_prompt = f.read()

    print(f"Starting evolutionary sandbox for instance '{instance}' for {ticks} ticks...")
    
    for i in range(ticks):
        print(f"\n--- Tick {i+1}/{ticks} ---")
        history = load_history()
        
        print("Thinking...")
        action = generate_next_action(system_prompt, history, TOOLS_SCHEMA)
        
        if action["type"] == "error":
            print(action["content"])
            break
            
        elif action["type"] == "thought":
            print(f"Agent Thought:\n{action['content']}")
            append_to_history({
                "role": "assistant",
                "content": action["content"]
            })
            
        elif action["type"] == "tool_call":
            if action["content"]:
                print(f"Agent Thought: {action['content']}")
                
            tool_name = action["tool_name"]
            arguments = action["arguments"]
            tool_call_id = action["tool_call_id"]
            
            print(f"Action: Call tool '{tool_name}' with args {arguments}")
            
            # Record the assistant's decision to call the tool
            assistant_message = {
                "role": "assistant",
                "content": action["content"],
                "tool_calls": [{
                    "id": tool_call_id,
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": str(arguments).replace("'", '"') # LLMs expect JSON string
                    }
                }]
            }
            append_to_history(assistant_message)
            
            # Execute the tool safely
            if tool_name in AVAILABLE_TOOLS:
                try:
                    result = AVAILABLE_TOOLS[tool_name](**arguments)
                except TypeError as e:
                    result = f"TypeError: {str(e)}. Please verify you are passing only the allowed parameters: {list(arguments.keys())}"
                except Exception as e:
                    result = f"Error executing tool '{tool_name}': {str(e)}"
            else:
                result = f"Error: Tool '{tool_name}' not found."
                
            print(f"Result:\n{result[:500]}..." if len(result) > 500 else f"Result:\n{result}")
            
            # Record the tool's result
            tool_message = {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": tool_name,
                "content": str(result)
            }
            append_to_history(tool_message)

        # Brief pause between ticks to avoid rate limiting
        time.sleep(2)
        
    print("\nSandbox execution complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the evolutionary sandbox")
    parser.add_argument("--instance", type=str, default="", help="Name of the isolated instance workspace to use")
    parser.add_argument("--ticks", type=int, default=1, help="Number of steps the agent should take")
    args = parser.parse_args()
    
    run_loop(args.instance, args.ticks)
