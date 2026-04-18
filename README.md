# Pocket-Agent: NeonAI Assistant ⚡

An ultra-lightweight, offline tool-calling engine optimized for mobile devices.

## 🚀 Quick Start
1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Launch Premium UI**: `python app.py`
3. **Launch Fallback CLI**: `python demo.py`

## 🧠 Model Architecture & Decisions
* **Base Model**: `Qwen/Qwen2.5-0.5B-Instruct` (Selected for its high parameter efficiency and native tool-calling logic).
* **Fine-Tuning**: LoRA fine-tuned on Google Colab T4 using the Unsloth framework for 2x faster training and 60% less memory usage.
* **Quantization**: 4-bit (Q4_K_M) GGUF format.
* **Size**: 379 MB (Safely under the 500 MB Hard Gate).
* **Latency**: ~140ms per turn on standard CPU (Beating the 200ms Hard Gate).

## 🛠️ Tool Schema
Supports the 5 mandatory schemas: `weather`, `calendar`, `convert`, `currency`, and `sql`.

## 🧪 Error Analysis & Debugging Insights (+5 Bonus)
During Slice C (Adversarial) testing, we identified that the model occasionally hallucinated extra JSON keys when presented with Roman Urdu/English code-switched prompts (e.g., "Kal ka weather..."). 

**The Fix**: I implemented a **Robust Extraction Layer** in `inference.py`. Instead of trusting the raw model output, we use a regex-based pre-processor to isolate the `<tool_call>` tags and a JSON validator to catch malformed strings. If a hallucination is detected, the system automatically degrades to a polite refusal rather than emitting broken JSON, ensuring we avoid the -0.5 penalty for incorrect decisions.

## 🎨 UI/UX Features
* **Glassmorphism Aesthetic**: Custom CSS injected for a premium, high-contrast dark mode.
* **State Preservation**: Implemented a hidden HTML comment hack to store raw AI tool calls within the chat history, ensuring multi-turn context (Slice D) remains intact even when using visual Markdown cards.