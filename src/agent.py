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

        await updater.update_status(
            TaskState.working, new_agent_text_message("Translating code...")
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=[f"You are a professional code translator. Translate the following code and explain the changes briefly:\n\n{input_text}"]
        )
        
        translation = response.text

        await updater.add_artifact(
            parts=[Part(root=TextPart(text=translation))],
            name="Translation",
        )
        
        await updater.update_status(
            TaskState.completed, new_agent_text_message("Translation complete.")
        )
