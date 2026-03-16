import pyautogui
import mss
import subprocess
import os
import platform
import io
import base64
import time
from PIL import Image


class SystemBridge:
    """Low-level interface between NexusOS AI and the actual computer."""

    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05
        self.sct = mss.mss()
        self.screen_size = pyautogui.size()

    def screenshot(self, scale_to=(1024, 768)) -> tuple[Image.Image, str]:
        """Capture screen, return PIL Image and base64 encoded version."""
        monitor = self.sct.monitors[1]  # Primary monitor
        raw = self.sct.grab(monitor)
        img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
        if scale_to:
            img = img.resize(scale_to, Image.LANCZOS)
        # Convert to base64 for API
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        b64 = base64.standard_b64encode(buf.getvalue()).decode()
        return img, b64

    def click(self, x: int, y: int, button: str = "left", clicks: int = 1):
        """Click at screen coordinates (in model space, will be scaled)."""
        sx, sy = self._scale_coords(x, y)
        pyautogui.click(sx, sy, button=button, clicks=clicks)

    def double_click(self, x: int, y: int):
        self.click(x, y, clicks=2)

    def right_click(self, x: int, y: int):
        self.click(x, y, button="right")

    def move_mouse(self, x: int, y: int):
        sx, sy = self._scale_coords(x, y)
        pyautogui.moveTo(sx, sy)

    def drag(self, x1: int, y1: int, x2: int, y2: int, duration: float = 0.5):
        sx1, sy1 = self._scale_coords(x1, y1)
        sx2, sy2 = self._scale_coords(x2, y2)
        pyautogui.moveTo(sx1, sy1)
        pyautogui.drag(sx2 - sx1, sy2 - sy1, duration=duration)

    def type_text(self, text: str, interval: float = 0.02):
        if text.isascii():
            pyautogui.typewrite(text, interval=interval)
        else:
            pyautogui.write(text)

    def hotkey(self, *keys: str):
        pyautogui.hotkey(*keys)

    def key(self, key_name: str):
        pyautogui.press(key_name)

    def scroll(self, amount: int, x: int | None = None, y: int | None = None):
        if x is not None and y is not None:
            sx, sy = self._scale_coords(x, y)
            pyautogui.scroll(amount, sx, sy)
        else:
            pyautogui.scroll(amount)

    def launch_app(self, app_name: str) -> bool:
        """Launch an application by name."""
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.Popen(["start", app_name], shell=True)
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", app_name])
            else:  # Linux
                subprocess.Popen(
                    [app_name],
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            return True
        except Exception as e:
            print(f"[Bridge] Failed to launch {app_name}: {e}")
            return False

    def run_command(self, command: str, timeout: int = 30) -> tuple[str, str, int]:
        """Run a shell command, return (stdout, stderr, returncode)."""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=timeout
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out", -1

    def list_files(self, path: str = ".") -> list[str]:
        try:
            return os.listdir(os.path.expanduser(path))
        except OSError as e:
            return [f"Error: {e}"]

    def read_file(self, path: str) -> str:
        try:
            with open(os.path.expanduser(path), "r") as f:
                return f.read()
        except Exception as e:
            return f"Error: {e}"

    def write_file(self, path: str, content: str) -> bool:
        try:
            with open(os.path.expanduser(path), "w") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"[Bridge] Write failed: {e}")
            return False

    def get_system_info(self) -> dict:
        return {
            "os": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "screen": f"{self.screen_size[0]}x{self.screen_size[1]}",
        }

    def _scale_coords(self, x: int, y: int) -> tuple[int, int]:
        """Scale from model coordinates (1024x768) to actual screen."""
        scale_x = self.screen_size[0] / 1024
        scale_y = self.screen_size[1] / 768
        return int(x * scale_x), int(y * scale_y)
