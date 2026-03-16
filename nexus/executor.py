import time
from .bridge import SystemBridge


class Executor:
    """Executes action plans from the brain via the system bridge."""

    def __init__(self, bridge: SystemBridge):
        self.bridge = bridge
        self.action_log: list[dict] = []

    def execute_plan(self, plan: dict, on_action=None) -> list[dict]:
        """Execute a plan's steps. Returns list of action results."""
        results = []
        steps = plan.get("steps", [])

        for i, step in enumerate(steps):
            action = step.get("action", "").upper()
            result = self._execute_step(step)
            results.append({"step": i, "action": action, "result": result})
            self.action_log.append(
                {"step": step, "result": result, "timestamp": time.time()}
            )

            if on_action:
                on_action(i, step, result)

            if action == "DONE":
                break

            # Small delay between actions for stability
            time.sleep(0.1)

        return results

    def _execute_step(self, step: dict) -> str:
        action = step.get("action", "").upper()

        try:
            if action == "CLICK":
                self.bridge.click(step["x"], step["y"])
                return f"Clicked at ({step['x']}, {step['y']})"

            elif action == "DOUBLE_CLICK":
                self.bridge.double_click(step["x"], step["y"])
                return f"Double-clicked at ({step['x']}, {step['y']})"

            elif action == "RIGHT_CLICK":
                self.bridge.right_click(step["x"], step["y"])
                return f"Right-clicked at ({step['x']}, {step['y']})"

            elif action == "TYPE":
                self.bridge.type_text(step["text"])
                return f"Typed: {step['text'][:50]}..."

            elif action == "HOTKEY":
                keys = step.get("keys", step.get("text", "").split())
                self.bridge.hotkey(*keys)
                return f"Hotkey: {'+'.join(keys)}"

            elif action == "KEY":
                self.bridge.key(step["key"])
                return f"Key: {step['key']}"

            elif action == "SCROLL":
                x = step.get("x")
                y = step.get("y")
                self.bridge.scroll(step.get("amount", -3), x, y)
                return f"Scrolled {step.get('amount', -3)}"

            elif action == "DRAG":
                self.bridge.drag(
                    step["x1"], step["y1"], step["x2"], step["y2"]
                )
                return f"Dragged ({step['x1']},{step['y1']}) to ({step['x2']},{step['y2']})"

            elif action == "LAUNCH":
                app = step.get("app", step.get("text", ""))
                success = self.bridge.launch_app(app)
                time.sleep(1)  # Wait for app to open
                return f"Launched {app}" if success else f"Failed to launch {app}"

            elif action == "RUN":
                cmd = step.get("command", step.get("text", ""))
                stdout, stderr, code = self.bridge.run_command(cmd)
                if code == 0:
                    return f"Exit {code}: {stdout[:200]}"
                else:
                    return f"Error: {stderr[:200]}"

            elif action == "WAIT":
                secs = step.get("seconds", step.get("duration", 1))
                time.sleep(secs)
                return f"Waited {secs}s"

            elif action == "SCREENSHOT":
                return "Screenshot requested"

            elif action == "DONE":
                return "Task complete"

            else:
                return f"Unknown action: {action}"

        except Exception as e:
            return f"Error: {e}"
