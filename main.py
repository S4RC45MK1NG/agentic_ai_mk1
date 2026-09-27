import tools, json, os, sys, wikipedia
from openrouter import OpenRouter
from google import genai


api_key = os.getenv("KEY") or "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"

api_key = "unused"


hc_ai_key = "sk-hc-v1-ac73b332852252bfa446ea9edc27525ca3314e3807298968a78719113bd89fe7"


if not api_key:
    raise RuntimeError("Set APIKEY or OPENROUTER_API_KEY before running this program.")


client = OpenRouter(
    api_key=api_key,
    server_url="http://127.0.0.1:8080/v1",
)

# Default definition
messages = [
    {
        "role": "system",
        "content": (
            "You are a personal assistant. You will execute tasks described by the user, and have access to a set of tools to accomplish the defined tasks. Try to assess your tools before declaring the task as not doable. Try to not use md file formatting as your text is not being processed as md text, but only plaintext."
        ),
    }
]

#MODEL = "qwen/qwen3.8-flash"  # double-check the exact model id/slug on the proxy's model list
MODEL = "qwen/qwen3.8-27b:free" # qwen flash isnt available for free tier

MAX_TOOL_ROUNDS = 5      # safety cap so a misbehaving model can't loop forever
 
 
def call_model():
    return client.chat.send(
        model=MODEL,
        messages=messages,
        tools=tools.tools,
        timeout_ms=30000,
        stream=False,
        temperature=0.2,
    )
 
 
def prompt(text):
    messages.append({"role": "user", "content": text})

    if text == "quit":
        sys.exit()
 
    for _ in range(MAX_TOOL_ROUNDS):
        response = call_model()

        print(response.choices[0].message.model_dump(), "\n")
        assistant_message = response.choices[0].message
 
        # Preserve tool_calls too, not just content — the model needs this
        # history to make sense of the tool results that follow.
        messages.append(assistant_message.model_dump(exclude_none=True))
 
        if not assistant_message.tool_calls:
            # No tool call -> this is the final answer, we're done.
            return assistant_message
 
        print("Tool Invoked")
        pending_image_messages = []
 
        for call in assistant_message.tool_calls:
            fn = tools.TOOL_MAPPING.get(call.function.name)
            args = json.loads(call.function.arguments or "{}")
 
            if fn is None:
                result_text = f"Unknown tool: {call.function.name}"
            else:
                try:
                    output = fn(**args)
                except Exception as e:
                    result_text = f"Tool error: {e}"
                    output = None
                else:
                    result_text = tools.format_tool_result(output)
                    # scan_screen returns {"path": ..., "message": ...};
                    # queue the actual image as a follow-up message.
                    if isinstance(output, dict) and output.get("path"):
                        pending_image_messages.append(
                            tools.build_local_screen_message(output["path"])
                        )
 
            # Send the tool's result back, tagged with the same tool_call_id,
            # so the model can see it on the next call_model() call.
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result_text,
            })
 
        # Tool messages are text-only, so the image(s) go in as follow-up
        # user messages, placed after all the tool messages for this round.
        messages.extend(pending_image_messages)
 
        # loop again: send messages (now including tool results) back to
        # the model so it can produce the actual final answer
 
    # Fallback if the model keeps calling tools past the safety cap
    class _Stub:
        content = "(stopped: too many tool rounds)"
        tool_calls = None
    return _Stub()
 
 
if __name__ == "__main__":
    print("Enter prompt: ")
    while True:
        txt = input("\n>")
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