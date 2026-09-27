import base64
import json
import os

import pyautogui


def scan_screen():
    """Capture the current screen and save it locally for inspection."""
    path = os.path.join("screenshots", "latest.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = pyautogui.screenshot()
    img.save(path)
    return {"path": path, "message": "Screenshot saved successfully."}


tools = [
    {
        "type": "function",
        "function": {
            "name": "scan_screen",
            "description": "Capture the current screen and save it locally.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }
]

TOOL_MAPPING = {"scan_screen": scan_screen}


def format_tool_result(result):
    if isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False)
    return str(result)


def build_local_screen_message(path):
    with open(path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("ascii")

    return {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Here is the screenshot captured by scan_screen. Describe what is visible in it.",
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{encoded_image}",
                    "detail": "auto",
                },
            },
        ],
    }


def build_screen_prompt(public_image_url):
    if not public_image_url:
        raise RuntimeError(
            "Vision-capable models cannot fetch a local screenshot. "
            "Set SCREENSHOT_URL to a public image URL as a fallback."
        )
    return {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Describe the visible screen contents in one short paragraph. "
                "Focus on UI elements, layout, and any obvious text.",
            },
            {
                "type": "input_image",
                "image_url": {"url": public_image_url},
                "detail": "auto",
            },
        ],
    }