import chainlit as cl
import ollama
import asyncio

@cl.on_chat_start
async def start_chat():
    # Initialize session variables
    cl.user_session.set(
        "interaction",
        [{"role": "system", "content": "You are a helpful assistant."}]
    )

    # Welcome message
    msg = cl.Message(content="")
    start_message = "Hello, I'm your 100% local alternative to ChatGPT running on Llama3.2-Vision. How can I help you today?"
    for token in start_message:
        await msg.stream_token(token)
    await msg.send()

@cl.step(type="tool")
async def tool(input_message: str, images: list = None):
    interaction = cl.user_session.get("interaction")

    # Append user message with optional images
    user_message = {"role": "user", "content": input_message}
    if images:
        user_message["images"] = images
    interaction.append(user_message)

    try:
        # Stream response from Ollama
        stream = ollama.chat(model="llama3.2-vision", messages=interaction, stream=True)
        response_content = ""
        for chunk in stream:
            # Ensure chunk has 'message' and 'content' keys
            if "message" in chunk and "content" in chunk["message"]:
                response_content += chunk["message"]["content"]
                yield chunk["message"]["content"]
        interaction.append({"role": "assistant", "content": response_content})
    except Exception as e:
        error_msg = f"Error with Ollama: {str(e)}"
        interaction.append({"role": "assistant", "content": error_msg})
        yield error_msg

@cl.on_message
async def main(message: cl.Message):
    # Extract images from message elements
    images = [file.path for file in message.elements if "image" in file.mime] if message.elements else None

    # Stream response
    msg = cl.Message(content="")
    async for token in tool(message.content, images):
        await msg.stream_token(token)
    await msg.send()

if __name__ == "__main__":
    import os
    os.system("chainlit run app.py -w")