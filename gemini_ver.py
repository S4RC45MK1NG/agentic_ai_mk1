import tools, json, os
from openrouter import OpenRouter
from google import genai


api_key = os.getenv("GEMINI_KEY")
if not api_key:
    raise RuntimeError("Set APIKEY or OPENROUTER_API_KEY before running this program.")

client = genai.Client()

# Default definition
messages = [
    {
        "role": "system",
        "content": (
            "You are a personal assistant. You will execute tasks described by the user, and have access to a set of tools to accomplish the defined tasks. Try to assess your tools before declaring the task as not doable."
        ),
    }
]

#MODEL = "qwen/qwen3.8-flash"  # double-check the exact model id/slug on the proxy's model list

MODEL = "gemini-3.8-flash"
MAX_TOOL_ROUNDS = 5      # safety cap so a misbehaving model can't loop forever
 
 
def call_model(text, resp=None):
    if resp: 
        return client.interactions.create(
            model=MODEL,
            input=text,
            system_instruction="You are a personal assistant. You will execute tasks described by the user, and have access to a set of tools to accomplish the defined tasks. Try to assess your tools before declaring the task as not doable.",
            previous_interaction_id=resp.id,
            stream=False,
        )
    else:
        return client.interactions.create(
                model=MODEL,
                input=text,
                system_instruction="You are a personal assistant. You will execute tasks described by the user, and have access to a set of tools to accomplish the defined tasks. Try to assess your tools before declaring the task as not doable.",
                stream=False,
            )

def prompt(text):
 
    response = call_model(text)
    return response


if __name__ == "__main__":
    print("Enter prompt: ")
    while True:
        txt = input(">")
        rep = prompt(txt)
        print(rep.content)

'''
def prompt(text):
    messages.append({
        "role": "user",
        "content": text,
    })

    response = client.chat.send(
        model="qwen/qwen3.8-flash",
        messages=messages,
        tools=tools.tools,
        stream=False,
        temperature=0.2,
    )

    assistant_message = response.choices[0].message
    messages.append({
        "role": "assistant",
        "content": assistant_message.content or "",
    })

    return assistant_message

print("Enter prompt: ")
while 1:
    txt = input(">")
    rep = prompt(txt)
    if rep.tool_calls:
        print("Tool Invoked")
        for call in rep.tool_calls:
            fn = tools.TOOL_MAPPING.get(call.function.name)
            if call.function.name == "scan_screen":
                    output = fn()
                    if isinstance(output, str) and output.startswith("data:image"):
                        pending_images.append(output)
                        result_text = "Screenshot captured. The image is attached in the next message."


def run_screen_loop():
    messages = [
        {
            "role": "user",
            "content": (
                "Can you scan the screen and describe the window after"
            ),
        }
    ]

    tool_response = client.chat.send(
        model="qwen/qwen3.8-flash",
        messages=messages,
        tools=tools.tools,
        tool_choice={"type": "function", "function": {"name": "scan_screen"}},
        max_tokens=256,
        stream=False,
        temperature=0.2,
    )

    assistant_message = tool_response.choices[0].message
    tool_calls = getattr(assistant_message, "tool_calls", None) or []
    scan_call = next(
        (tool_call for tool_call in tool_calls if tool_call.function.name == "scan_screen"),
        None,
    )
    if scan_call is None:
        print("The model did not call scan_screen.")
        return

    result = tools.scan_screen()
    messages.extend(
        [
            {
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": scan_call.id,
                        "type": scan_call.type,
                        "function": {
                            "name": scan_call.function.name,
                            "arguments": scan_call.function.arguments or "{}",
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": scan_call.id,
                "name": "scan_screen",
                "content": tools.format_tool_result(result),
            },
            tools.build_local_screen_message(result["path"]),
        ]
    )

    response = client.chat.send(
        model="qwen/qwen3.8-flash",
        messages=messages,
        stream=False,
        max_tokens=256,
        temperature=0.2,
    )
    content = response.choices[0].message.content or ""
    print(content or "The model responded without any visible content.")


#if __name__ == "__main__":
#    run_screen_loop()
'''