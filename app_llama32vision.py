import chainlit as cl
import ollama

@cl.on_chat_start
async def start_chat():
    cl.user_session.set(
        "interaction",
        [{"role": "system", "content": "You are a helpful assistant powered by Llama 3.2 Vision."}]
    )
    msg = cl.Message(content="")
    start_message = "Hello! I'm Llama 3.2 Vision, running locally. I can handle text and images. How can I help you?"
    for token in start_message:
        await msg.stream_token(token)
    await msg.send()

@cl.step(type="tool")
async def tool(input_message: str, images: list = None):
    interaction = cl.user_session.get("interaction")
    user_message = {"role": "user", "content": input_message}
    if images:
        user_message["images"] = images
    interaction.append(user_message)
    
    try:
        stream = ollama.chat(model="llama3.2-vision", messages=interaction, stream=True)
        response_content = ""
        for chunk in stream:
            if "message" in chunk and "content" in chunk["message"]:
                response_content += chunk["message"]["content"]
                yield chunk["message"]["content"]
        interaction.append({"role": "assistant", "content": response_content})
    except Exception as e:
        error_msg = f"Error with Llama 3.2 Vision: {str(e)}"
        interaction.append({"role": "assistant", "content": error_msg})
        yield error_msg

@cl.on_message
async def main(message: cl.Message):
    images = [file.path for file in message.elements if "image" in file.mime] if message.elements else None
    msg = cl.Message(content="")
    async for token in tool(message.content, images):
        await msg.stream_token(token)
    await msg.send()

if __name__ == "__main__":
    import os
    os.system("chainlit run app_llama32vision.py -w")