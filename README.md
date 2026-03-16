# NexusOS

AI-native operating system. Claude is the brain, Ollama is the hands.

NexusOS sees your screen, understands your intent, and controls the computer for you. It combines Claude's strategic reasoning with local model execution to create a seamless AI-powered OS layer.

## Quick Start

```bash
pip install -e .
cp .env.example .env  # Add your ANTHROPIC_API_KEY
python run.py
```

## Architecture

- **Brain** (`nexus/brain.py`) — Claude plans multi-step tasks from screenshots
- **Executor** (`nexus/executor.py`) — Translates plans into system actions
- **Bridge** (`nexus/bridge.py`) — Low-level interface to screen, keyboard, mouse
- **Core** (`nexus/core.py`) — Main loop tying everything together
