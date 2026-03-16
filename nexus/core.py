import time
from rich.console import Console
from rich.panel import Panel
from .config import Config
from .bridge import SystemBridge
from .brain import NexusBrain
from .executor import Executor

console = Console()


class NexusOS:
    """Main NexusOS controller — the loop that connects brain to computer."""

    def __init__(self):
        self.config = Config()
        self.bridge = SystemBridge()
        self.brain = NexusBrain(self.config)
        self.executor = Executor(self.bridge)
        self.running = True
        self.total_actions = 0
        self.total_cost = 0.0

    def run_task(self, user_request: str, max_iterations: int = 10):
        """Execute a user request through the brain->executor loop."""
        console.print(
            Panel(
                f"[bold cyan]NEXUS[/] processing: {user_request}",
                border_style="cyan",
            )
        )

        for iteration in range(max_iterations):
            # 1. Capture current screen state
            console.print(
                f"\n[dim]Iteration {iteration + 1}/{max_iterations} — capturing screen...[/]"
            )
            img, screenshot_b64 = self.bridge.screenshot()

            # 2. Send to brain for planning
            console.print("[dim]Thinking...[/]")
            if iteration == 0:
                plan = self.brain.plan(user_request, screenshot_b64)
            else:
                plan = self.brain.followup(
                    "Actions executed. Here's the current screen.", screenshot_b64
                )

            # 3. Show the plan
            thinking = plan.get("thinking", "")
            steps = plan.get("steps", [])

            if thinking:
                console.print(
                    Panel(thinking, title="[cyan]Brain[/]", border_style="dim")
                )

            if not steps:
                console.print(
                    "[yellow]No actions planned. Task may be complete.[/]"
                )
                break

            # 4. Check for DONE
            if any(s.get("action", "").upper() == "DONE" for s in steps):
                console.print("[bold green]Task complete[/]")
                # Execute any steps before DONE
                pre_done = []
                for s in steps:
                    if s.get("action", "").upper() == "DONE":
                        break
                    pre_done.append(s)
                if pre_done:
                    self.executor.execute_plan(
                        {"steps": pre_done}, on_action=self._log_action
                    )
                break

            # 5. Execute the plan
            results = self.executor.execute_plan(plan, on_action=self._log_action)
            self.total_actions += len(results)

            # 6. Check if a SCREENSHOT was requested (need to loop again)
            needs_screenshot = any(r["action"] == "SCREENSHOT" for r in results)
            if not needs_screenshot and iteration < max_iterations - 1:
                # Auto-screenshot after actions to verify
                time.sleep(0.3)
                continue

        console.print(f"\n[dim]Total actions: {self.total_actions}[/]")

    def interactive(self):
        """Run NexusOS in interactive mode — REPL loop."""
        console.print(
            Panel.fit(
                "[bold cyan]NexusOS[/] — AI-Native Operating System\n"
                "[dim]Type a command and NexusOS will control the computer for you.\n"
                "Type 'quit' to exit, 'reset' to clear history.[/]",
                border_style="cyan",
            )
        )

        sys_info = self.bridge.get_system_info()
        console.print(
            f"[dim]System: {sys_info['os']} {sys_info['release']} | Screen: {sys_info['screen']}[/]\n"
        )

        while self.running:
            try:
                user_input = console.input("[bold cyan]nexus>[/] ").strip()

                if not user_input:
                    continue
                elif user_input.lower() in ("quit", "exit", "q"):
                    console.print("[dim]Shutting down NexusOS...[/]")
                    break
                elif user_input.lower() == "reset":
                    self.brain.reset()
                    console.print("[dim]Conversation history cleared.[/]")
                    continue
                elif user_input.lower() == "screenshot":
                    img, _ = self.bridge.screenshot()
                    img.save("screenshot.png")
                    console.print("[dim]Screenshot saved to screenshot.png[/]")
                    continue
                elif user_input.lower() == "history":
                    for entry in self.executor.action_log[-10:]:
                        console.print(
                            f"  [dim]{entry['step']['action']}[/] -> {entry['result']}"
                        )
                    continue

                self.run_task(user_input)

            except KeyboardInterrupt:
                console.print("\n[dim]Interrupted. Type 'quit' to exit.[/]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/]")

    def _log_action(self, index: int, step: dict, result: str):
        action = step.get("action", "?")
        console.print(f"  [cyan]->[/] {action}: {result}")
