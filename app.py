import gradio as gr
import json
import re
from inference import run

# Custom CSS for high-end Glassmorphism + Neon theme
custom_css = """
/* Force Dark Theme Base & Background */
body, .gradio-container {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    background: radial-gradient(circle at 50% 0%, rgb(20, 25, 45) 0%, rgb(5, 8, 15) 100%) !important;
    color: #e2e8f0 !important;
}

/* Hide default Gradio footer */
footer {
    display: none !important;
}

/* The Main Chatbot Window */
#chatbot {
    background: rgba(15, 23, 42, 0.4) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(56, 189, 248, 0.15) !important;
    border-radius: 24px !important;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255,255,255,0.05) !important;
}

/* Chat bubble common styling */
.message-wrap {
    padding: 14px 20px !important;
    font-size: 15px !important;
    line-height: 1.5 !important;
}

/* User Message */
.user.message {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.25), rgba(139, 92, 246, 0.25)) !important;
    border: 1px solid rgba(14, 165, 233, 0.4) !important;
    border-radius: 20px 20px 4px 20px !important;
    box-shadow: 0 4px 20px rgba(14, 165, 233, 0.15) !important;
}

/* Bot Message */
.bot.message {
    background: rgba(30, 41, 59, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 20px 20px 20px 4px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
}

/* Fade in animation for messages */
.message {
    animation: fadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Thinking state pulse */
.generating {
    animation: pulse 1.5s infinite ease-in-out !important;
    border-color: rgba(139, 92, 246, 0.8) !important;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.5) !important;
}
@keyframes pulse {
    0% { transform: scale(1); opacity: 0.8; box-shadow: 0 0 10px rgba(139, 92, 246, 0.3); }
    50% { transform: scale(1.02); opacity: 1; box-shadow: 0 0 25px rgba(139, 92, 246, 0.7); }
    100% { transform: scale(1); opacity: 0.8; box-shadow: 0 0 10px rgba(139, 92, 246, 0.3); }
}

/* Custom Tool Action Card */
.tool-card {
    background: rgba(15, 23, 42, 0.85) !important;
    border-left: 4px solid #0ea5e9 !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    margin: 12px 0 !important;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3) !important;
}
.tool-header {
    display: flex !important;
    align-items: center !important;
    color: #38bdf8 !important;
    font-weight: 800 !important;
    font-size: 1.2em !important;
    margin-bottom: 12px !important;
    border-bottom: 1px solid rgba(56, 189, 248, 0.2) !important;
    padding-bottom: 8px !important;
    letter-spacing: 0.5px !important;
}
.tool-body {
    color: #e2e8f0 !important;
    font-size: 0.95em !important;
    line-height: 1.7 !important;
}
.tool-key {
    color: #a78bfa !important;
    font-weight: 700 !important;
    margin-right: 6px !important;
}
.tool-value {
    color: #f8fafc !important;
}

/* Input Area Overrides */
.form {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
textarea {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(139, 92, 246, 0.4) !important;
    border-radius: 16px !important;
    color: white !important;
    padding: 14px !important;
    font-size: 15px !important;
    transition: all 0.3s ease !important;
    backdrop-filter: blur(8px) !important;
}
textarea:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.4) !important;
    outline: none !important;
}

/* Submit Button */
button.primary {
    background: linear-gradient(135deg, #0ea5e9, #8b5cf6) !important;
    border: none !important;
    border-radius: 14px !important;
    box-shadow: 0 0 20px rgba(14, 165, 233, 0.5) !important;
    color: white !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
button.primary:hover {
    box-shadow: 0 0 30px rgba(139, 92, 246, 0.8) !important;
    transform: translateY(-2px) !important;
}

/* Secondary Button (Clear History) */
button.secondary {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #cbd5e1 !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
button.secondary:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
}
"""

def restore_history(bot_msg):
    """Extract the original JSON from the hidden comment if it exists."""
    if not bot_msg:
        return ""
    match = re.search(r'<!-- RAW_TOOL_CALL: (.*?) -->', bot_msg, re.DOTALL)
    if match:
        return f"<tool_call>{match.group(1)}</tool_call>"
    return bot_msg

def chat_wrapper(user_message, gradio_history):
    # Map Gradio's history [[user, bot], [user, bot]] to the dict format expected by inference.py
    formatted_history = []
    for u_msg, b_msg in gradio_history:
        if u_msg:
            formatted_history.append({"role": "user", "content": u_msg})
        if b_msg:
            # Restore the original <tool_call> JSON string from HTML formatting
            original_bot_msg = restore_history(b_msg)
            formatted_history.append({"role": "assistant", "content": original_bot_msg})
            
    # Execute inference
    response = run(user_message, formatted_history)
    
    # Check for <tool_call> string and parse it into an Action Card
    match = re.search(r'<tool_call>(.*?)</tool_call>', response, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
        try:
            data = json.loads(json_str)
            
            # Extract a sensible name for the tool
            tool_name = data.pop("name", data.pop("tool", "Tool Execution"))
            
            # Format the JSON into a beautiful HTML Action Card
            html_parts = [
                '<div class="tool-card">',
                f'    <div class="tool-header">🛠️ &nbsp;TOOL TRIGGERED: {tool_name}</div>',
                '    <div class="tool-body">'
            ]
            
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                html_parts.append(f'        <div><span class="tool-key">{str(key).title()}:</span> <span class="tool-value">{value}</span></div>')
                
            html_parts.append('    </div>')
            html_parts.append('</div>')
            
            # Embed the original JSON in a hidden comment so we can reconstruct the history on the next turn
            html_parts.append(f'<!-- RAW_TOOL_CALL: {json_str} -->')
            
            # Inject the HTML back into the string
            beautiful_response = response[:match.start()] + "\\n".join(html_parts) + response[match.end():]
            return beautiful_response
            
        except json.JSONDecodeError:
            return response
            
    return response

# Define the Chatbot component outside Blocks to prevent double-rendering
chatbot = gr.Chatbot(elem_id="chatbot", bubble_full_width=False, show_label=False)

# Build the Gradio App
with gr.Blocks(css=custom_css, theme=gr.themes.Base()) as demo:
    gr.HTML('''
        <div style="text-align: center; margin-top: 40px; margin-bottom: 30px;">
            <h1 style="color: #38bdf8; text-shadow: 0 0 20px rgba(56, 189, 248, 0.6); font-family: system-ui, -apple-system, sans-serif; font-size: 2.8em; margin-bottom: 5px;">NeonAI Assistant</h1>
            <p style="color: #a78bfa; font-family: system-ui, -apple-system, sans-serif; font-size: 1.2em; letter-spacing: 1px; text-transform: uppercase;">Intelligent Mobile Companion</p>
        </div>
    ''')
    
    gr.ChatInterface(
        fn=chat_wrapper,
        chatbot=chatbot,
        retry_btn=None,
        undo_btn=None,
        clear_btn="Clear History",
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, show_api=False)

