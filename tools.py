import os
import subprocess
import json
from duckduckgo_search import DDGS

def get_workspace_dir():
    instance_name = os.getenv("ACTIVE_INSTANCE", "")
    if not instance_name:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "agent_workspace"))
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "instances", instance_name, "agent_workspace"))

def get_shared_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "instances", "shared_space"))

def _is_safe_path(path_str):
    workspace = get_workspace_dir()
    shared = get_shared_dir()
    
    # Resolve the target path
    target = os.path.abspath(os.path.join(workspace, path_str))
    
    # Allow access if it is inside the instance's local workspace OR the global shared space
    return target.startswith(workspace) or target.startswith(shared)

def _get_absolute_path(path_str):
    return os.path.abspath(os.path.join(get_workspace_dir(), path_str))

def read_file(path: str) -> str:
    """Reads a file from the workspace."""
    if not _is_safe_path(path):
        return "Error: Path is outside of allowed workspace."
        
    abs_path = _get_absolute_path(path)
    if not os.path.exists(abs_path):
        return f"Error: File {path} does not exist."
        
    if os.path.isdir(abs_path):
        return f"Error: '{path}' is a directory, not a file. If you want to list files in a directory, use the 'run_command' tool with the 'dir' command."
        
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(path: str, content: str) -> str:
    """Writes content to a file in the workspace."""
    if not _is_safe_path(path):
        return "Error: Path is outside of allowed workspace."
        
    abs_path = _get_absolute_path(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    
    try:
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def edit_file(path: str, old_content: str, new_content: str) -> str:
    """Edits an existing file by replacing a unique block of text (old_content) with new_content."""
    if not _is_safe_path(path):
        return "Error: Path is outside of allowed workspace."
        
    abs_path = _get_absolute_path(path)
    if not os.path.exists(abs_path):
        return f"Error: File {path} does not exist."
        
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            file_data = f.read()
            
        if old_content not in file_data:
            return "Error: The exact search content (old_content) was not found in the file."
            
        if file_data.count(old_content) > 1:
            return "Error: Multiple occurrences of the search content found. Please provide more surrounding lines as context."
            
        updated_data = file_data.replace(old_content, new_content)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(updated_data)
        return f"Successfully edited file {path}."
    except Exception as e:
        return f"Error editing file: {str(e)}"

def run_command(command: str) -> str:
    """Runs a shell command inside the workspace directory."""
    try:
        p = subprocess.Popen(
            command,
            shell=True,
            cwd=get_workspace_dir(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            stdout, stderr = p.communicate(timeout=15)
            output = stdout or ""
            if stderr:
                output += f"\nSTDERR:\n{stderr}"
            return output if output else "Command executed silently."
        except subprocess.TimeoutExpired:
            # Terminate the entire process tree on Windows to prevent pipe lockups from orphan children
            subprocess.run(f"taskkill /F /T /PID {p.pid}", shell=True, capture_output=True)
            p.kill()
            # Flush streams
            stdout, stderr = p.communicate()
            return "Error: Command timed out. Execution exceeded 15 seconds."
    except Exception as e:
        return f"Error running command: {str(e)}"

def search_web(query: str) -> str:
    """Searches the web for the query and returns results."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
            return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error searching the web: {str(e)}"

# The schema definition for the LLM
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the contents of a file within your sandbox workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The relative path to the file (e.g. 'notes.txt' or 'src/main.py')"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Creates or overwrites a file within your sandbox workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The relative path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edits an existing file by replacing a unique block of text (old_content) with new_content. Use this to modify specific lines of code without overwriting the entire file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The relative path to the file"
                    },
                    "old_content": {
                        "type": "string",
                        "description": "The exact block of code/text to be replaced. Must match exactly including indentation."
                    },
                    "new_content": {
                        "type": "string",
                        "description": "The new block of code/text to replace old_content with."
                    }
                },
                "required": ["path", "old_content", "new_content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Executes a shell command in the root of your sandbox workspace (Windows PowerShell). Use this to run scripts, list files, or interact with the OS.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The powershell command to run"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Searches the web for information using DuckDuckGo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Dispatcher mapping
AVAILABLE_TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "run_command": run_command,
    "search_web": search_web
}
