#!/usr/bin/env python3
"""
Real Working Agent - Actually executes tools instead of just returning JSON
"""
import json
import re
import os
import subprocess
import requests
from typing import List, Dict, Any, Optional


class RealAgent:
    """An agent that actually executes tool calls instead of just returning JSON"""
    
    def __init__(self, model="qwen2.5-coder:3b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.working_dir = "/tmp/real_agent_work"
        os.makedirs(self.working_dir, exist_ok=True)
        
    def call_ollama(self, messages: List[Dict], tools: Optional[List[Dict]] = None) -> str:
        """Call Ollama API and get response"""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": 0.1
        }
        
        if tools:
            payload["tools"] = tools
            
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Ollama API error: {response.status_code}")
    
    def parse_tool_calls(self, content: str) -> List[Dict]:
        """Parse tool calls from LLM response content"""
        tool_calls = []
        
        # Look for ```json blocks
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                data = json.loads(match.strip())
                if 'name' in data and 'arguments' in data:
                    tool_calls.append(data)
                    print(f"📋 Found tool call: {data['name']}")
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parse error: {e}")
                
        return tool_calls
    
    def execute_file_edit(self, command: str, path: str, file_text: str = "", view_range: List[int] = None) -> str:
        """Actually execute file editing commands"""
        full_path = os.path.join(self.working_dir, path)
        
        try:
            if command == "create":
                # Create the file with content
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w') as f:
                    f.write(file_text)
                print(f"✅ Created file: {full_path}")
                return f"File {path} created successfully with {len(file_text)} characters"
                
            elif command == "view":
                # View file contents
                if os.path.exists(full_path):
                    with open(full_path, 'r') as f:
                        content = f.read()
                    print(f"👀 Viewed file: {full_path}")
                    return f"File contents:\n{content}"
                else:
                    return f"File {path} does not exist"
                    
            elif command == "str_replace":
                # Replace text in file
                if os.path.exists(full_path):
                    with open(full_path, 'r') as f:
                        content = f.read()
                    # Simple replacement - you could enhance this
                    if '<<<' in file_text and '>>>' in file_text:
                        old_text = file_text.split('<<<')[1].split('>>>')[0]
                        new_text = file_text.split('>>>')[1]
                        new_content = content.replace(old_text, new_text)
                    else:
                        new_content = file_text
                    with open(full_path, 'w') as f:
                        f.write(new_content)
                    print(f"✏️ Modified file: {full_path}")
                    return f"File {path} modified successfully"
                else:
                    return f"File {path} does not exist"
                    
        except Exception as e:
            error_msg = f"❌ File operation failed: {e}"
            print(error_msg)
            return error_msg
    
    def execute_bash_command(self, command: str) -> str:
        """Actually execute bash commands"""
        try:
            # Change to working directory
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
                
            print(f"🔧 Executed: {command}")
            print(f"📤 Output: {output[:200]}...")
            return output
            
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds"
        except Exception as e:
            error_msg = f"❌ Command failed: {e}"
            print(error_msg)
            return error_msg
    
    def execute_tool_call(self, tool_call: Dict) -> str:
        """Actually execute a tool call instead of just returning JSON"""
        name = tool_call["name"]
        args = tool_call["arguments"]
        
        if name == "str_replace_based_edit_tool":
            return self.execute_file_edit(
                command=args.get("command", ""),
                path=args.get("path", ""),
                file_text=args.get("file_text", ""),
                view_range=args.get("view_range", [])
            )
            
        elif name == "bash":
            return self.execute_bash_command(args.get("command", ""))
            
        elif name == "task_done":
            return "✅ Task completed successfully!"
            
        else:
            return f"❌ Unknown tool: {name}"
    
    def run_task(self, task: str, max_steps: int = 5) -> str:
        """Run a task with actual tool execution"""
        print(f"🎯 Starting task: {task}")
        print(f"📁 Working directory: {self.working_dir}")
        
        # Define available tools
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "str_replace_based_edit_tool",
                    "description": "Create, view, or edit files",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "enum": ["create", "view", "str_replace"]},
                            "path": {"type": "string"},
                            "file_text": {"type": "string"},
                            "view_range": {"type": "array", "items": {"type": "integer"}}
                        },
                        "required": ["command", "path"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "bash",
                    "description": "Execute bash commands",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string"}
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "task_done",
                    "description": "Mark task as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "summary": {"type": "string"}
                        }
                    }
                }
            }
        ]
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful coding assistant. Use the provided tools to complete tasks. Always use tool calls to perform actions - don't just describe what you would do."
            },
            {
                "role": "user", 
                "content": f"Task: {task}\n\nPlease complete this task using the available tools."
            }
        ]
        
        for step in range(max_steps):
            print(f"\n📍 Step {step + 1}/{max_steps}")
            
            # Get LLM response
            response_content = self.call_ollama(messages, tools)
            print(f"🤖 LLM Response: {response_content[:200]}...")
            
            # Parse and execute tool calls
            tool_calls = self.parse_tool_calls(response_content)
            
            if not tool_calls:
                print("ℹ️ No tool calls found - asking for clarification")
                messages.append({
                    "role": "assistant",
                    "content": response_content
                })
                messages.append({
                    "role": "user",
                    "content": "Please use the available tools to complete the task. You must use tool calls, not just describe what to do."
                })
                continue
                
            # Execute each tool call
            tool_results = []
            for tool_call in tool_calls:
                result = self.execute_tool_call(tool_call)
                tool_results.append(result)
                print(f"🔧 Tool result: {result[:100]}...")
                
                # Add tool result to conversation
                messages.append({
                    "role": "assistant",
                    "content": response_content
                })
                messages.append({
                    "role": "user", 
                    "content": f"Tool result: {result}"
                })
                
                # Check if task is done
                if tool_call["name"] == "task_done":
                    print("✅ Task marked as complete!")
                    return result
        
        print("⚠️ Reached maximum steps")
        return "Task execution completed (max steps reached)"
    
    def list_created_files(self) -> List[str]:
        """List all files created by the agent"""
        files = []
        for root, dirs, filenames in os.walk(self.working_dir):
            for filename in filenames:
                rel_path = os.path.relpath(os.path.join(root, filename), self.working_dir)
                files.append(rel_path)
        return files


if __name__ == "__main__":
    # Test the real agent
    agent = RealAgent()
    
    # Test 1: Create a simple file
    print("🧪 Test 1: Create hello.py")
    result = agent.run_task("Create a file called hello.py that prints 'Hello Real Agent!'")
    print(f"Result: {result}")
    
    # Show created files
    files = agent.list_created_files()
    print(f"📁 Created files: {files}")
    
    # Show file contents
    if files:
        for file in files:
            full_path = os.path.join(agent.working_dir, file)
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    content = f.read()
                print(f"📄 {file}:\n{content}")
    
    print(f"\n🎯 Working directory: {agent.working_dir}")
    print("✅ Real agent test complete!")
