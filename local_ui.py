import gradio as gr
from core.message_handler import handle_ask_command, handle_image_upload, handle_summarize_command

# We use a static ID for local debugging to maintain a consistent state
PLATFORM = "gradio"
DEBUG_USER_ID = "admin_developer"

async def chat_wrapper(message, _history):
    """Wraps our RAG ask command for Gradio's ChatInterface."""
    # Gradio passes the current message and the UI history.
    # We ignore the UI history because our state_manager.py handles it!
    response = await handle_ask_command(PLATFORM, DEBUG_USER_ID, message)
    return response

async def summarize_wrapper():
    """Wraps our summarize command."""
    return await handle_summarize_command(PLATFORM, DEBUG_USER_ID)

async def image_wrapper(image_filepath):
    """Wraps our vision command."""
    if not image_filepath:
        return "❌ Please upload an image first."
    response = await handle_image_upload(PLATFORM, DEBUG_USER_ID, image_filepath)
    return response

# Build the UI using Gradio Blocks
with gr.Blocks(title="Hybrid Bot - Debug UI") as demo:
    gr.Markdown("# 🤖 Hybrid Bot - Local Debugger")
    gr.Markdown("Use this interface to test the RAG and Vision engines without needing API tokens.")

    with gr.Tab("💬 RAG & Chat"):
        # Built-in chat UI that automatically handles the input box and submit button
        gr.ChatInterface(fn=chat_wrapper)
        
        gr.Markdown("### Advanced Commands")
        with gr.Row():
            summarize_btn = gr.Button("📝 Run /summarize", variant="secondary")
            summary_output = gr.Textbox(label="Summary Result", interactive=False)
            
        summarize_btn.click(fn=summarize_wrapper, outputs=summary_output)

    with gr.Tab("🖼️ Vision Engine"):
        with gr.Row():
            with gr.Column():
                image_input = gr.Image(type="filepath", label="Upload Image to Test")
                image_btn = gr.Button("🔍 Analyze Image", variant="primary")
            
            with gr.Column():
                image_output = gr.Textbox(label="Vision Model Output", lines=5, interactive=False)
                
        image_btn.click(fn=image_wrapper, inputs=image_input, outputs=image_output)

if __name__ == "__main__":
    print("🚀 Launching Gradio Debug UI...")
    # http://127.0.0.1:7860
    demo.launch(theme=gr.themes.Soft())