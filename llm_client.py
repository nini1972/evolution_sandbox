import os
import json
from dotenv import load_dotenv
from litellm import completion

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
    
    agent_model = os.getenv("AGENT_MODEL", "openrouter/google/gemini-2.5-flash")

    messages = [{"role": "system", "content": system_prompt}]
    
    # Append history to messages
    for entry in history:
        messages.append({
            "role": entry["role"],
            "content": entry.get("content", ""),
            **({"tool_calls": entry["tool_calls"]} if "tool_calls" in entry else {}),
            **({"tool_call_id": entry["tool_call_id"], "name": entry.get("name")} if entry["role"] == "tool" else {})
        })

    try:
        response = completion(
            model=agent_model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        # type: ignore
        message = response.choices[0].message
        
        # If the model wants to call a tool
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            return {
                "type": "tool_call",
                "tool_call_id": tool_call.id,
                "tool_name": tool_call.function.name,
                "arguments": json.loads(tool_call.function.arguments),
                "content": message.content or "" # Also capture any thoughts the model had
            }
        else:
            # Model didn't call a tool, maybe it just wants to think or hit an error
            return {
                "type": "thought",
                "content": message.content
            }
            
    except Exception as e:
        return {
            "type": "error",
            "content": f"LLM Error: {str(e)}"
        }
