import os


class Config:
    """NexusOS configuration — loads from environment variables."""

    def __init__(self):
        self.anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")
        self.ollama_host: str = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_model: str = os.environ.get("OLLAMA_MODEL", "qwen2.5vl:7b")
        self.claude_model: str = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        self.screenshot_interval: float = float(os.environ.get("SCREENSHOT_INTERVAL", "0.5"))
        self.max_actions_per_step: int = int(os.environ.get("MAX_ACTIONS_PER_STEP", "10"))
        self.screen_scale: tuple[int, int] = tuple(
            int(v) for v in os.environ.get("SCREEN_SCALE", "1024x768").split("x")
        )

        if not self.anthropic_api_key:
            # Try loading from .env file in project root
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
            if os.path.exists(env_path):
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, _, value = line.partition("=")
                            key, value = key.strip(), value.strip()
                            if key == "ANTHROPIC_API_KEY" and value:
                                self.anthropic_api_key = value
                            elif key == "OLLAMA_HOST" and value:
                                self.ollama_host = value
                            elif key == "OLLAMA_MODEL" and value:
                                self.ollama_model = value
