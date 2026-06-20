"""
AI API Client
Handles communication with AI APIs (OpenAI, Gemini)
"""

import json
import requests
from typing import Dict, Any, Optional
from openai import OpenAI
try:
    from google import genai
except ImportError:
    genai = None


class AIClient:
    """Client for AI API communication"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize AI client with configuration"""
        self.config = config
        self.provider = config.get("ai", {}).get("provider", "openai")

        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "gemini":
            self._init_gemini()
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    def _init_openai(self):
        """Initialize OpenAI client"""
        api_key = self.config.get("ai", {}).get("api_key")
        if not api_key or api_key == "your-openai-api-key-here":
            raise ValueError("OpenAI API key not configured")

        # Initialize OpenAI client (new 1.0+ syntax)
        self.openai_client = OpenAI(api_key=api_key)
        self.model = self.config.get("ai", {}).get("model", "gpt-4")

    def _init_gemini(self):
        """Initialize Gemini client"""
        if genai is None:
            raise ImportError("google-genai not installed. Run: pip install google-genai")

        api_key = self.config.get("gemini", {}).get("api_key")
        if not api_key or api_key == "your-gemini-api-key-here":
            raise ValueError("Gemini API key not configured")

        self.gemini_client = genai.Client(api_key=api_key)
        self.model = self.config.get("gemini", {}).get("model", "gemini-2.5-flash")

    def get_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Get command intent from user input

        Args:
            user_input: Natural language command from user

        Returns:
            Dictionary with intent, parameters, and confidence
        """
        system_prompt = self._get_system_prompt()

        if self.provider == "openai":
            return self._get_intent_openai(system_prompt, user_input)
        elif self.provider == "gemini":
            return self._get_intent_gemini(system_prompt, user_input)

    def _get_system_prompt(self) -> str:
        """Get system prompt for AI"""
        return """You are a PC automation assistant that converts natural language commands into structured intents.

Analyze the user's command and respond with a JSON object containing:
- intent: The action type (open_app, close_app, find_files, system_control, process_control, system_info, plugin_command, etc.)
- parameters: Dictionary of parameters needed for the command
- confidence: Float between 0 and 1
- requires_confirmation: Boolean if action is destructive

Command Categories:
1. Application Control: open, close, restart apps
2. File Operations: find, create, delete, move, copy files
3. System Control: shutdown, reboot, sleep, lock
4. Process Management: list, kill processes
5. System Info: disk usage, ram usage, cpu usage
6. Complex Tasks & Plugins: Map commands that involve browsing, web searches, or other external actions to "plugin_command".
   For browsers, use `command_name` as "open_url" and provide the "url".

Examples:
User: "open chrome"
Response: {"intent": "open_app", "parameters": {"app_name": "chrome"}, "confidence": 0.95, "requires_confirmation": false}

User: "find all pdf files"
Response: {"intent": "find_files", "parameters": {"extension": "pdf"}, "confidence": 0.9, "requires_confirmation": false}

User: "shutdown in 5 minutes"
Response: {"intent": "shutdown", "parameters": {"delay_minutes": 5}, "confidence": 0.95, "requires_confirmation": true}

User: "kill chrome"
Response: {"intent": "kill_process", "parameters": {"process_name": "chrome"}, "confidence": 0.9, "requires_confirmation": true}

User: "open youtube and search for cats"
Response: {"intent": "plugin_command", "parameters": {"command_name": "open_url", "url": "https://www.youtube.com/results?search_query=cats"}, "confidence": 0.95, "requires_confirmation": false}

User: "go to google.com"
Response: {"intent": "plugin_command", "parameters": {"command_name": "open_url", "url": "https://google.com"}, "confidence": 0.95, "requires_confirmation": false}

Respond ONLY with valid JSON, no additional text."""

    def _get_intent_openai(self, system_prompt: str, user_input: str) -> Dict[str, Any]:
        """Get intent using OpenAI API"""
        try:
            # Use new OpenAI 1.0+ client syntax
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=self.config.get("ai", {}).get("temperature", 0.3),
                max_tokens=self.config.get("ai", {}).get("max_tokens", 500)
            )

            content = response.choices[0].message.content.strip()

            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            return json.loads(content)

        except json.JSONDecodeError as e:
            return {
                "intent": "unknown",
                "parameters": {},
                "confidence": 0.0,
                "error": f"Failed to parse AI response: {e}"
            }
        except Exception as e:
            return {
                "intent": "error",
                "parameters": {},
                "confidence": 0.0,
                "error": str(e)
            }

    def _get_intent_gemini(self, system_prompt: str, user_input: str) -> Dict[str, Any]:
        """Get intent using Gemini API"""
        try:
            prompt = f"{system_prompt}\n\nUser command: {user_input}"
            response = self.gemini_client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            content = response.text.strip()

            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            return json.loads(content)

        except json.JSONDecodeError as e:
            return {
                "intent": "unknown",
                "parameters": {},
                "confidence": 0.0,
                "error": f"Failed to parse AI response: {e}"
            }
        except Exception as e:
            return {
                "intent": "error",
                "parameters": {},
                "confidence": 0.0,
                "error": str(e)
            }
