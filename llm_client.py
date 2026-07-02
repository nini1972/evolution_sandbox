import os
import json
import time
from dotenv import load_dotenv
from litellm import completion
def prune_history(history: list, max_messages: int = 6) -> list:
    """Limits history length while ensuring no orphan tool responses at start."""
    if len(history) <= max_messages:
        pruned = list(history)
    else:
        slice_start = len(history) - max_messages
        while slice_start < len(history) and history[slice_start].get("role") == "tool":
            slice_start += 1
        pruned = list(history[slice_start:])
    
    if pruned and pruned[0].get("role") == "assistant":
        pruned.insert(0, {"role": "user", "content": "Please continue."})
    return pruned

def merge_consecutive_messages(messages: list) -> list:
    merged = []
    for msg in messages:
        if not merged:
            merged.append(msg)
            continue
        prev = merged[-1]
        if msg["role"] == prev["role"] and msg["role"] in ("assistant", "user"):
            if msg.get("content"):
                if prev.get("content"):
                    prev["content"] = prev["content"] + "\n\n" + msg["content"]
                else:
                    prev["content"] = msg["content"]
            if "tool_calls" in msg and msg["tool_calls"]:
                if "tool_calls" not in prev:
                    prev["tool_calls"] = []
                existing_ids = {tc.get("id") for tc in prev["tool_calls"]}
                for tc in msg["tool_calls"]:
                    if tc.get("id") not in existing_ids:
                        prev["tool_calls"].append(tc)
        else:
            merged.append(msg)
    return merged

def generate_next_action(system_prompt: str, history: list, tools: list) -> dict:
    """
    Calls the LLM with the given prompt, history, and tools.
    Returns a dictionary representing the action to take.
    """
    # Load global env (e.g., API keys)
    global_dotenv = os.path.abspath(os.path.join(os.path.dirname(__file__), "config", ".env"))
    load_dotenv(dotenv_path=global_dotenv, override=False)

    # Load instance-specific env (e.g., model overrides)
    instance_name = os.getenv("ACTIVE_INSTANCE", "")
    if instance_name:
        instance_dotenv = os.path.abspath(os.path.join(os.path.dirname(__file__), "instances", instance_name, ".env"))
        load_dotenv(dotenv_path=instance_dotenv, override=True)
    
    # Try to load git-tracked model routing mappings (useful for CI/CD runners where .env is ignored)
    agent_model = os.getenv("AGENT_MODEL")
    if not agent_model and instance_name:
        routing_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "config", "model_routing.json"))
        if os.path.exists(routing_path):
            try:
                with open(routing_path, "r", encoding="utf-8") as f:
                    routing = json.load(f)
                    agent_model = routing.get(instance_name)
            except Exception as e:
                print(f"Warning: Failed to load model routing file: {e}")
                
    if not agent_model:
        agent_model = "openrouter/google/gemini-2.5-flash"

    messages = [{"role": "system", "content": system_prompt}]
    
    # Append history to messages
    pruned = prune_history(history)
    for entry in pruned:
        msg = {
            "role": entry["role"],
            "content": entry.get("content", ""),
        }
        if entry["role"] == "assistant" and "tool_calls" in entry and entry["tool_calls"]:
            msg["tool_calls"] = []
            for tc in entry["tool_calls"]:
                func = tc.get("function", {})
                args = func.get("arguments", "{}")
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        pass
                args = json.dumps(args)
                msg["tool_calls"].append({
                    "id": tc.get("id"),
                    "type": "function",
                    "function": {
                        "name": func.get("name"),
                        "arguments": args
                    }
                })
        if entry["role"] == "tool":
            msg["tool_call_id"] = entry["tool_call_id"]
            msg["name"] = entry.get("name")
        messages.append(msg)

    messages = merge_consecutive_messages(messages)

    retries = 5
    for attempt in range(retries):
        try:
            response = completion(
                model=agent_model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=1024,
            )
            # type: ignore
            message = response.choices[0].message
            
            # If the model wants to call a tool
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except Exception as json_err:
                    return {
                        "type": "json_error",
                        "content": f"JSON Decoding Error: {str(json_err)}. Received arguments string: {tool_call.function.arguments}"
                    }
                return {
                    "type": "tool_call",
                    "tool_call_id": tool_call.id,
                    "tool_name": tool_call.function.name,
                    "arguments": arguments,
                    "content": message.content or "" # Also capture any thoughts the model had
                }

            else:
                # Model didn't call a tool, maybe it just wants to think or hit an error
                return {
                    "type": "thought",
                    "content": message.content
                }
                
        except Exception as e:
            err_str = str(e).lower()
            if attempt < retries - 1 and ("rate" in err_str or "limit" in err_str or "429" in err_str or "400" in err_str or "delimit" in err_str):
                print(f"[Rate limited or temporary error. Sleeping 15 seconds before retry {attempt + 2}/{retries}...] ({str(e)})")
                time.sleep(15)
                continue
            return {
                "type": "error",
                "content": f"LLM Error: {str(e)}"
            }
    
    return {
        "type": "error",
        "content": "LLM Error: Max retries exceeded without action."
    }
