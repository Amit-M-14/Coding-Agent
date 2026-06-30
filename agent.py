import os
import json
import sys
from openai import OpenAI
from dotenv import load_dotenv
from tools import read_file, write_file, list_files, run_terminal_command

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# This is the manual we give the AI so it knows HOW to use its hands
tools = [
    # Write files
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Writes content to a file. Overwrites if it already exists.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The relative path to the file"},
                    "content": {"type": "string", "description": "The full content to write"} 
                },
                "required": ["path", "content"]
            },
        },
    },

    # Read Files
    {
        "type" : "function",
        "function" : {
            "name" : "read_file",
            "description" : "Reads content from a file.",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "path" : {"type": "string", "description": "The relative path to the file you want to read."},
                },
                "required": ["path"]
            },
        },
    },

    # List Files
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Lists all files and folders in the current directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "The directory to list, defaults to current '.'"}
                },
            },
        },
    },

    # Run Terminal Command
    {
        "type": "function",
        "function": {
            "name": "run_terminal_command",
            "description": "Run a shell command in the terminal to test code or check system status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The command to run, e.g., 'python script.py'"},
                },
                "required": ["command"]
            },
        },
    },
]

available_tools = {
    "write_file" : write_file,
    "read_file" : read_file,
    "list_files" : list_files,
    "run_terminal_command" : run_terminal_command,
}

def askAgent(prompt, max_steps=10):
    messages = [
        {
            "role": "system", 
            "content": """You are a professional coding assistant with a 'PLAN.md' memory system.
        
            RULES:
            1. For any complex task, your FIRST action must be to create a 'PLAN.md' file listing the steps needed.
            2. Update 'PLAN.md' after every step by marking tasks as [x].
            3. Use 'run_terminal_command' to verify your work.
            4. If a command fails, update your plan with a new 'Bug Fix' step.
            5. Respond with 'TERMINATE' only when the task is fully verified and complete."""
        },
        {"role": "user", "content": prompt}
    ]

    step = 0
    while step < max_steps:
        step += 1
        print(f"\n--- STEP {step} ---")

        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        
        messages.append(response_message)

        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_tools[function_name]
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"[ACTION]: Calling {function_name}({function_args})")
                
                # Execute the tool
                result = function_to_call(**function_args)
                print(f"[OBSERVATION]: {result}")

                # 3. Feed the result BACK into the messages history
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": result,
                })
        else:
            # If no tool calls, the agent is giving its final answer
            print(f"[FINAL RESPONSE]: {response_message.content}")
            if "TERMINATE" in response_message.content or step > 1:
                break

    return "Task Complete."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[ERROR]:no prompt provided.")
        sys.exit(1)

    user_prompt = sys.argv[1]
    result = askAgent(user_prompt)
    print(result)