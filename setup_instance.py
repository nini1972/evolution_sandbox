import os
import argparse
import shutil
from dotenv import load_dotenv

def setup_instance(name: str, model: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    instance_dir = os.path.join(base_dir, "instances", name)
    workspace_dir = os.path.join(instance_dir, "agent_workspace")
    logs_dir = os.path.join(instance_dir, "logs")

    os.makedirs(workspace_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    print(f"Created workspace and logs directories for instance '{name}'.")

    # Try to load existing API key from config/.env to copy it automatically
    config_env = os.path.join(base_dir, "config", ".env")
    api_key = "your-openrouter-key-here"
    if os.path.exists(config_env):
        load_dotenv(dotenv_path=config_env)
        api_key = os.getenv("OPENROUTER_API_KEY", api_key)

    # Write instance specific .env file
    env_content = f"""# Configured for instance '{name}'
OPENROUTER_API_KEY="{api_key}"
AGENT_MODEL="{model}"
"""
    env_path = os.path.join(instance_dir, ".env")
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)

    print(f"Created .env file at {env_path} with model '{model}'.")
    if api_key == "your-openrouter-key-here":
        print("WARNING: Please fill in your OPENROUTER_API_KEY in the new .env file.")
    else:
        print("Successfully copied OPENROUTER_API_KEY from config/.env.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup a new agent instance space")
    parser.add_argument("--name", type=str, required=True, help="Unique name for the instance space")
    parser.add_argument("--model", type=str, default="openrouter/google/gemini-2.5-flash", help="The LLM model to run for this instance")
    args = parser.parse_args()

    setup_instance(args.name, args.model)
