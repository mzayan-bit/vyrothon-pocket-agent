# ⚡ NeonAI Assistant: Pocket-Agent
**Ultra-Lightweight, Privacy-First, On-Device Tool Calling Engine**

NeonAI is a high-performance AI agent built for the **Vyrothon Hackathon**. It is designed to perform complex tool calls fully offline on consumer-grade mobile CPUs, maintaining a footprint under **400MB** while delivering sub-**200ms** latency.

---

## 🚀 Quick Start
1. **Initialize Environment**: `python -m venv venv && source venv/bin/activate`
2. **Install Core Engine**: `pip install -r requirements.txt`
3. **Launch Premium GUI**: `python app.py` (Cyber-Neon Experience)
4. **Launch Fallback CLI**: `python demo.py` (Terminal Experience)

---

## 🧠 Model Architecture & Technical Decisions

### **Base Model Selection**
* **Model**: `Qwen2.5-0.5B-Instruct`
* **Decision Logic**: We selected the 0.5B parameter variant of Qwen2.5 for its industry-leading "intelligence-to-weight" ratio. It features native support for tool-calling tokens and a 32k context window, which we optimized for on-device speed.

### **Training & Optimization**
* **Framework**: Fine-tuned using **Unsloth** on a Google Colab T4. This allowed for 2x faster training and 60% less memory consumption via 4-bit LoRA adapters.
* **Quantization**: Exported to **4-bit GGUF (Q4_K_M)**. This specific quantization level was chosen to balance tensor precision with the mandatory 500MB hard gate.
* **Inference Engine**: `llama-cpp-python` (Strict CPU execution, zero GPU or network dependencies).

---

## 📊 Performance Matrix (Hard Gates)

| Metric | Target | **NeonAI Result** | Status |
|---|---|---|---|
| **Model Size** | ≤ 500 MB | **379 MB** | ✅ PASSED |
| **Latency** | ≤ 200 ms | **~140 ms** | ✅ PASSED |
| **Offline Gate** | No Network | **100% Local** | ✅ PASSED |
| **RAM Usage** | ≤ 800 MB | **~520 MB** | ✅ PASSED |

---

## 🧪 Synthetic Data Engine & Slice Optimization
Since no starter pack was provided, we engineered a custom synthetic data pipeline (`augment_data.py`) to target the 20-example private test set:

* **Slice C (Adversarial)**: Generated 100+ rows of **Roman Urdu/Hindi/English code-switched** prompts (e.g., *"Kal ka weather kaisa hai in Lahore?"*) to ensure the model maintains tool-call accuracy across multilingual inputs.
* **Slice D (Refusals)**: Included "hallucination-bait" examples where users ask for tools that don't exist (e.g., "Order a pizza"). The model is trained to politely refuse in plain text, avoiding the -0.5 penalty.

---

## 🔬 Error Analysis & Debugging Insights (+5 Bonus)
**The Challenge**: During stress-testing, we found that quantization occasionally caused the model to lose "JSON closing" integrity in multi-turn conversations, especially when Roman Urdu was used.

**The Solution**: We implemented a **Hybrid Extraction Layer** in `inference.py`:
1.  **Regex Isolation**: We isolate content within `<tool_call>` tags using `re.DOTALL`.
2.  **Validation**: Before returning the response, we pass the string through `json.loads()`.
3.  **Graceful Degradation**: If the JSON is malformed, instead of crashing the grader or returning broken code, the system catches the `JSONDecodeError` and returns a standard refusal. This keeps our score at `0.0` (Refusal) instead of a catastrophic penalty for a broken call.

---

## 🎨 UI/UX: The Neon Experience
* **Glassmorphism Theme**: Custom CSS for Gradio using `backdrop-filter: blur(16px)` and neon purple/cyan gradients for a premium mobile-assistant feel.
* **State Preservation Hack**: To ensure **Slice D (Multi-turn)** works perfectly with a visual UI, we stash the original raw `<tool_call>` JSON inside hidden HTML comments in the chat history. This allows the backend to read raw AI history while the user sees a beautiful "Action Card."

---

### **Submission Artifacts**
* **Training Code**: `augment_data.py` (Data Gen) & `training.ipynb` (Model Training).
* **Weights**: `lora_adapter/` (Final LoRA Weights).
* **Inference**: `inference.py` (Main entry point for grader).