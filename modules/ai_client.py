"""
AI API Client
Handles communication with AI APIs (OpenAI, Gemini, Ollama) and acts as an Agent.
"""

import json
import requests
from typing import Dict, Any, List

class AIClient:
    """Client for AI API communication and agentic loop"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize AI client with configuration"""
        self.config = config
        self.provider = config.get("ai", {}).get("provider", "openai")

        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "gemini":
            self._init_gemini()
        elif self.provider == "ollama":
            self._init_ollama()
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    def _init_openai(self):
        from openai import OpenAI
        api_key = self.config.get("ai", {}).get("api_key")
        if not api_key or api_key == "your-openai-api-key-here":
            raise ValueError("OpenAI API key not configured")
        self.openai_client = OpenAI(api_key=api_key)
        self.model = self.config.get("ai", {}).get("model", "gpt-4")

    def _init_gemini(self):
        try:
            from google import genai
        except ImportError:
            raise ImportError("google-genai not installed. Run: pip install google-genai")
        api_key = self.config.get("gemini", {}).get("api_key", self.config.get("ai", {}).get("api_key"))
        if not api_key or api_key == "your-gemini-api-key-here":
            raise ValueError("Gemini API key not configured")
        self.gemini_client = genai.Client(api_key=api_key)
        self.model = self.config.get("gemini", {}).get("model", "gemini-2.5-flash")

    def _init_ollama(self):
        self.ollama_url = self.config.get("ollama", {}).get("url", "http://localhost:11434")
        self.model = self.config.get("ollama", {}).get("model", "llama3")

    def get_agent_response(self, messages: List[Dict[str, str]], available_tools: Dict[str, str]) -> Dict[str, Any]:
        """Get next agent action based on conversation history"""
        system_prompt = self._get_system_prompt(available_tools)

        if self.provider == "openai":
            return self._get_response_openai(system_prompt, messages)
        elif self.provider == "gemini":
            return self._get_response_gemini(system_prompt, messages)
        elif self.provider == "ollama":
            return self._get_response_ollama(system_prompt, messages)

    def _get_system_prompt(self, available_tools: Dict[str, str]) -> str:
        tools_str = json.dumps(available_tools, indent=2)
        return f"""You are an autonomous PC Assistant agent.
You have the following tools available to help the user:
{tools_str}

You must respond ONLY with a JSON object in one of two formats:

1. To use a tool to gather information or perform an action:
{{
  "action": "tool_call",
  "command_name": "<name_of_tool_from_the_list_above>",
  "parameters": {{ "<param_name>": "<value>" }}
}}

2. To give a final answer to the user after using tools (or if no tools are needed):
{{
  "action": "final_answer",
  "text": "<what you want to say to the user>"
}}

When you receive a tool result in your history, analyze it and either call another tool or give a final answer.
Respond ONLY with valid JSON. No markdown formatting around the JSON block.
"""

    def _extract_json(self, content: str) -> Dict[str, Any]:
        content = content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            return {"action": "final_answer", "text": f"Error parsing my own thoughts: {e}. Raw: {content}"}

    def _get_response_openai(self, system_prompt: str, messages: list) -> Dict[str, Any]:
        api_messages = [{"role": "system", "content": system_prompt}] + messages
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=api_messages,
                temperature=0.2
            )
            return self._extract_json(response.choices[0].message.content)
        except Exception as e:
            return {"action": "final_answer", "text": str(e)}

    def _get_response_gemini(self, system_prompt: str, messages: list) -> Dict[str, Any]:
        # Convert roles for Gemini
        gemini_contents = [system_prompt]
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            gemini_contents.append(f"{role.upper()}: {m['content']}")
            
        prompt = "\n\n".join(gemini_contents)
        try:
            response = self.gemini_client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return self._extract_json(response.text)
        except Exception as e:
            return {"action": "final_answer", "text": str(e)}

    def _get_response_ollama(self, system_prompt: str, messages: list) -> Dict[str, Any]:
        api_messages = [{"role": "system", "content": system_prompt}] + messages
        try:
            response = requests.post(f"{self.ollama_url}/api/chat", json={
                "model": self.model,
                "messages": api_messages,
                "stream": False,
                "format": "json"
            })
            content = response.json()["message"]["content"]
            return self._extract_json(content)
        except Exception as e:
            return {"action": "final_answer", "text": f"Ollama connection error: {e}"}
