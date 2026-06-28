import os
from dotenv import load_dotenv
from litellm import completion

# Load the environment variables from config/.env
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, "config", ".env")
load_dotenv(dotenv_path=dotenv_path)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-openrouter-key-here":
    print("Error: Please set your OPENROUTER_API_KEY in config/.env before running diagnostics.")
    exit(1)

# Minimal test tool schema
TEST_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Writes content to a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The relative path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write"
                    }
                },
                "required": ["path", "content"]
            }
        }
    }
]

# List of Llama models to diagnose
LLAMA_MODELS = [
    "openrouter/meta-llama/llama-3.3-70b-instruct",
    "openrouter/meta-llama/llama-3.1-70b-instruct",
    "openrouter/meta-llama/llama-3.1-8b-instruct",
    "openrouter/meta-llama/llama-3-70b-instruct"
]

def test_model(model_name: str) -> bool:
    print(f"\nTesting model: {model_name}...")
    messages = [
        {"role": "system", "content": "You are a test agent. You MUST write your initial thoughts to a file named 'hello.txt' using the write_file tool."},
        {"role": "user", "content": "Begin by calling the write_file tool to write 'Hello World' to 'hello.txt'."}
    ]
    
    try:
        response = completion(
            model=model_name,
            messages=messages,
            tools=TEST_TOOLS,
            tool_choice="auto"
        )
        # type: ignore
        message = response.choices[0].message
        
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            print(f"  SUCCESS! Model called tool '{tool_call.function.name}' with args {tool_call.function.arguments}")
            return True
        else:
            print(f"  PARTIAL: Model responded with text but did NOT call the tool. Response: {message.content}")
            return False
            
    except Exception as e:
        print(f"  FAILED: {str(e)}")
        return False

def run_diagnostics():
    print("=" * 80)
    print("LLAMA TOOL-CALLING DIAGNOSTICS")
    print("=" * 80)
    
    successful_models = []
    
    for model in LLAMA_MODELS:
        if test_model(model):
            successful_models.append(model)
            
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY:")
    print("=" * 80)
    if successful_models:
        print("The following Llama models successfully supported tool calling:")
        for sm in successful_models:
            print(f" - {sm}")
        print("\nYou should use one of these slugs for your Llama sandbox instance.")
    else:
        print("No Llama models succeeded. This usually means OpenRouter has provider restrictions on these endpoints for tool use.")
    print("=" * 80)

if __name__ == "__main__":
    run_diagnostics()
