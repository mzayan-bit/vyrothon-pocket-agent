import json
import random

# We will format these exactly how Qwen2.5 expects conversational data
def format_example(user_prompt, expected_output):
    return {
        "messages": [
            {"role": "system", "content": "You are a helpful mobile assistant. If a tool is needed, output ONLY valid JSON wrapped in <tool_call>...</tool_call> tags. If no tool can handle the request, politely refuse in plain text."},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": expected_output}
        ]
    }

def generate_augmented_data():
    dataset = []

    # 1. ADVERSARIAL (Code-switching & Typos) - Targeting Slice C
    adversarial_cases = [
        ("Kal ka weather kaisa hai in Lahore in C?", '<tool_call>{"tool": "weather", "args": {"location": "Lahore", "unit": "C"}}</tool_call>'),
        ("Mujhe 500 USD to PKR convert karna hai", '<tool_call>{"tool": "currency", "args": {"amount": 500, "from": "USD", "to": "PKR"}}</tool_call>'),
        ("Create an event for 2026-04-19 titled Hackathon Fnal", '<tool_call>{"tool": "calendar", "args": {"action": "create", "date": "2026-04-19", "title": "Hackathon Fnal"}}</tool_call>'),
        ("can u selct all users from database where age > 20?", '<tool_call>{"tool": "sql", "args": {"query": "SELECT * FROM users WHERE age > 20"}}</tool_call>'),
        ("Plz convert 10 miles into km", '<tool_call>{"tool": "convert", "args": {"value": 10, "from_unit": "miles", "to_unit": "km"}}</tool_call>')
    ]

    # 2. REFUSALS & CHITCHAT - Targeting Slice D
    refusal_cases = [
        ("Play some music by Atif Aslam.", "I'm sorry, I don't have a tool to play music."),
        ("Turn on the living room lights.", "I cannot control smart home devices."),
        ("What is the meaning of life?", "I am a mobile assistant designed to help with specific tasks like checking the weather, calendar, and conversions. I cannot answer philosophical questions."),
        ("Can you order a pizza for me?", "I don't have the ability to place food orders."),
        ("Set a timer for 10 minutes.", "I don't have a timer tool available. I can help you with your calendar, though.")
    ]

    # Add augmented cases to the dataset
    for prompt, target in adversarial_cases:
        dataset.append(format_example(prompt, target))
        
    for prompt, target in refusal_cases:
        dataset.append(format_example(prompt, target))

    # Read the original teacher examples provided in the starter pack
    try:
        with open('starter/teacher_examples.jsonl', 'r') as f:
            for line in f:
                # We assume teacher examples are dicts with 'prompt' and 'target'
                # Adjust these keys if the starter pack structure is slightly different
                data = json.loads(line.strip())
                dataset.append(format_example(data['prompt'], data['target']))
    except FileNotFoundError:
        print("Warning: starter/teacher_examples.jsonl not found. Generating only synthetic data.")

    # Shuffle to prevent the model from learning a sequence bias
    random.shuffle(dataset)

    # Save to the final training file
    with open('train_augmented.jsonl', 'w') as f:
        for item in dataset:
            f.write(json.dumps(item) + '\n')
            
    print(f"Generated {len(dataset)} highly optimized training rows in train_augmented.jsonl")

if __name__ == "__main__":
    generate_augmented_data()