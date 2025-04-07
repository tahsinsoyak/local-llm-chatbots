import chainlit as cl
import ollama
import json
import os
from datetime import datetime

# File to store chat history
HISTORY_FILE = "chat_history_llama31.json"

@cl.on_chat_start
async def start_chat():
    # Load existing history if available, or start fresh
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            interaction = json.load(f)
    else:
        interaction = [{"role": "system", "content": "You are a helpful assistant powered by Llama 3.1."}]

    cl.user_session.set("interaction", interaction)

    # Display welcome message and previous chat history
    msg = cl.Message(content="")
    start_message = "Hello! I'm running Llama 3.1 locally. Ask me anything (text-only)!\n\n**Chat History:**\n"
    for entry in interaction[1:]:  # Skip system prompt
        role = "You" if entry["role"] == "user" else "Llama 3.1"
        start_message += f"- {role}: {entry['content']}\n"
    for token in start_message:
        await msg.stream_token(token)
    await msg.send()

@cl.step(type="tool")
async def tool(input_message: str):
    interaction = cl.user_session.get("interaction")
    interaction.append({"role": "user", "content": input_message})
    
    try:
        stream = ollama.chat(model="llama3.1", messages=interaction, stream=True)
        response_content = ""
        for chunk in stream:
            if "message" in chunk and "content" in chunk["message"]:
                response_content += chunk["message"]["content"]
                yield chunk["message"]["content"]
        interaction.append({"role": "assistant", "content": response_content})
    except Exception as e:
        error_msg = f"Error with Llama 3.1: {str(e)}"
        interaction.append({"role": "assistant", "content": error_msg})
        yield error_msg
    
    # Save updated history to file
    with open(HISTORY_FILE, "w") as f:
        json.dump(interaction, f, indent=2)

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="")
    async for token in tool(message.content):
        await msg.stream_token(token)
    await msg.send()

if __name__ == "__main__":
    import os
    os.system("chainlit run app_llama31.py -w")