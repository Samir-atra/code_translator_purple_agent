import json
from a2a.server.tasks import TaskUpdater
from a2a.types import Message, TaskState, Part, TextPart
from a2a.utils import get_message_text, new_agent_text_message
from google import genai
import os
from dotenv import load_dotenv

from messenger import Messenger

load_dotenv()

class Agent:
    def __init__(self):
        self.messenger = Messenger()
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model = "gemini-2.5-flash"

    async def run(self, message: Message, updater: TaskUpdater) -> None:
        """Implement your agent logic here.

        Args:
            message: The incoming message
            updater: Report progress (update_status) and results (add_artifact)

        Use self.messenger.talk_to_agent(message, url) to call other agents.
        """
        input_text = get_message_text(message)
        
        try:
            input_data = json.loads(input_text)
            code = input_data.get("code_to_translate", input_text)
            source_lang = input_data.get("source_language", "the source language")
            target_lang = input_data.get("target_language", "the target language")
        except json.JSONDecodeError:
            code = input_text
            source_lang = "unknown"
            target_lang = "target language"

        await updater.update_status(
            TaskState.working, new_agent_text_message("Translating code...")
        )

        prompt = f"""
You are a professional code translator. 
Translate the following code from {source_lang} to {target_lang}.
Return ONLY a valid JSON object with a single key "translated_code" containing the translation as a string.
Do not include markdown formatting (like ```json) around the output.

Code to translate:
{code}
"""

        # Models that support JSON mode (ordered by preference and quota independence)
        json_supported_models = [
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.5-flash",
            "gemini-2.0-flash-001",
            "gemini-2.0-flash-lite-001",
            "gemini-flash-latest", 
            "gemini-flash-lite-latest",
            "gemini-pro-latest",
            "gemini-2.5-pro",
            "gemini-exp-1206",
            "gemini-3-flash-preview",
            "gemini-3-pro-preview"
        ]
        
        # Models that don't support JSON mode (use text and parse manually)
        text_only_models = [
            "gemma-3-1b-it",
            "gemma-3-4b-it",
            "gemma-3-12b-it",
            "gemma-3-27b-it",
            "gemma-3n-e2b-it",
            "gemma-3n-e4b-it"
        ]
        
        models_to_try = json_supported_models + text_only_models
        
        last_error = None
        for model in models_to_try:
            try:
                print(f"[DEBUG] Trying translation with model: {model}")
                
                # Determine if model supports JSON mode
                use_json_mode = model in json_supported_models
                
                if use_json_mode:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=[prompt],
                        config=genai.types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    translation_json = response.text
                else:
                    # For Gemma models - use text mode and extract JSON manually
                    response = self.client.models.generate_content(
                        model=model,
                        contents=[prompt]
                    )
                    response_text = response.text
                    
                    # Try to extract JSON from the response
                    import re
                    # Look for JSON object
                    json_match = re.search(r'\{[^{}]*"translated_code"[^{}]*\}', response_text, re.DOTALL)
                    if json_match:
                        translation_json = json_match.group(0)
                    else:
                        # Fallback: wrap the response in JSON format
                        # Strip markdown code blocks if present
                        clean_code = re.sub(r'```\w*\n?', '', response_text).strip()
                        translation_json = json.dumps({"translated_code": clean_code})
                
                await updater.add_artifact(
                    parts=[Part(root=TextPart(text=translation_json))],
                    name="Translation",
                )
                
                # Return the JSON in the completion message so Green Agent can parse it
                await updater.update_status(
                    TaskState.completed, new_agent_text_message(translation_json)
                )
                return # Success!

            except Exception as e:
                print(f"[DEBUG] Model {model} failed: {e}")
                last_error = e
                # Check for resource exhausted and wait if needed
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print("[DEBUG] Quota exhausted. Waiting 30 seconds before trying next model...", flush=True)
                    import asyncio
                    await asyncio.sleep(30)
                # Continue to next model
        
        # If all models failed
        await updater.failed(new_agent_text_message(f"Translation failed with all models. Last error: {last_error}"))

