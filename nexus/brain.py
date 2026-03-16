import json
import anthropic
from .config import Config


class NexusBrain:
    """Claude-powered strategic layer. Plans multi-step tasks."""

    def __init__(self, config: Config):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        self.conversation: list[dict] = []
        self.system_prompt = """You are NexusOS, an AI that controls a computer. You can see the screen and execute actions.

When given a task, you create a STEP-BY-STEP action plan. Each step must be one of:
- CLICK x y - click at coordinates (1024x768 space)
- DOUBLE_CLICK x y
- RIGHT_CLICK x y
- TYPE text - type text
- HOTKEY key1 key2 ... - press key combination (e.g. HOTKEY ctrl c)
- KEY keyname - press a single key (e.g. KEY enter)
- SCROLL amount [x y] - scroll (positive=up, negative=down)
- DRAG x1 y1 x2 y2 - drag from point to point
- LAUNCH app_name - open an application
- RUN command - run a shell command
- WAIT seconds - pause for a duration
- SCREENSHOT - take a fresh screenshot to see current state
- DONE - task is complete

Respond with a JSON object:
{
    "thinking": "Brief analysis of what I see and what I need to do",
    "steps": [
        {"action": "CLICK", "x": 500, "y": 300},
        {"action": "TYPE", "text": "hello world"},
        {"action": "KEY", "key": "enter"}
    ]
}

Rules:
- Always analyze the screenshot before acting
- Use SCREENSHOT between complex actions to verify state
- Coordinates are in 1024x768 space
- Be precise with click targets — aim for the center of buttons/links
- Use HOTKEY for keyboard shortcuts (faster than clicking menus)
- After completing a task, end with DONE"""

    def plan(self, user_request: str, screenshot_b64: str) -> dict:
        """Given a user request and current screen, create an action plan."""
        self.conversation.append({
            "role": "user",
            "content": [
                {"type": "text", "text": user_request},
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": screenshot_b64,
                    },
                },
            ],
        })

        response = self.client.messages.create(
            model=self.config.claude_model,
            max_tokens=2048,
            system=self.system_prompt,
            messages=self.conversation,
        )

        assistant_text = response.content[0].text
        self.conversation.append({"role": "assistant", "content": assistant_text})

        # Parse JSON from response
        try:
            start = assistant_text.find("{")
            end = assistant_text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(assistant_text[start:end])
        except json.JSONDecodeError:
            pass

        return {"thinking": "Failed to parse plan", "steps": []}

    def followup(self, observation: str, screenshot_b64: str) -> dict:
        """Send a follow-up with new screenshot after executing actions."""
        return self.plan(
            f"Previous actions executed. Result: {observation}. What's next?",
            screenshot_b64,
        )

    def reset(self):
        """Clear conversation history."""
        self.conversation = []
