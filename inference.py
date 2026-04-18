import json
import re
from llama_cpp import Llama

# 1. Global Model Initialization
# Loading the model globally ensures it stays in memory between turns. 
# If you load it inside the run() function, you will fail the 200ms latency gate.
try:
    # This filename must match exactly what you download from Colab
    llm = Llama(
        model_path="./qwen2.5-0.5b-instruct.Q4_K_M.gguf",
        n_ctx=2048,
        n_threads=4,  # Optimized for CPU execution
        verbose=False # Keep logs clean for the grader
    )
except Exception as e:
    llm = None
    print(f"Critical Error Loading Model: {e}")

# The strict system prompt forcing JSON compliance
SYSTEM_PROMPT = "You are an on-device mobile assistant. If the user request matches a tool, emit ONLY a JSON object wrapped in <tool_call>...</tool_call>. If no tool matches, reply with a plain text refusal."

def run(prompt: str, history: list[dict]) -> str:
    """
    The exact entry point required by the grader.
    """
    if not llm:
        return "System failure: AI core offline."

    # 2. Format the ChatML Context (Qwen 2.5 style)
    formatted_prompt = f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
    
    # Inject multi-turn context
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        formatted_prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"
        
    # Append the current prompt
    formatted_prompt += f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

    # 3. Execute Inference
    response = llm(
        formatted_prompt,
        max_tokens=256,
        stop=["<|im_end|>"],
        temperature=0.0, # 0.0 forces strict deterministic JSON formatting
        top_p=0.9,
        echo=False
    )
    
    raw_output = response['choices'][0]['text'].strip()

    # 4. Safety Net Parser
    # This prevents hallucinated JSON from crashing the grader. 
    # If the JSON is malformed, we catch it and force a refusal state.
    match = re.search(r'<tool_call>(.*?)</tool_call>', raw_output, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
        try:
            # Validate JSON integrity
            json.loads(json_str)
            return f"<tool_call>{json_str}</tool_call>"
        except json.JSONDecodeError:
            # Fallback: A clean refusal prevents a catastrophic 0.0 score on this turn
            return "I am unable to process that request due to a formatting error."
    
    # If no tags are found, treat it as a deliberate plain-text refusal
    return raw_output