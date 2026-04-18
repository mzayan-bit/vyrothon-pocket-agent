import sys
from inference import run

def print_colored(text, color_code):
    print(f"\033[{color_code}m{text}\033[0m")

def main():
    print_colored("=============================================", "36")
    print_colored("  Pocket-Agent: Offline Tool-Calling Engine  ", "36;1")
    print_colored("=============================================", "36")
    print_colored("Type 'exit' or 'quit' to end the session.\n", "33")

    history = []

    while True:
        try:
            user_input = input("\033[32;1mUser > \033[0m")
            if user_input.lower() in ['exit', 'quit']:
                print_colored("Shutting down...", "33")
                break
            if not user_input.strip():
                continue

            # Run inference
            print_colored("Agent is thinking...", "90")
            response = run(user_input, history)

            # Display response
            print_colored(f"\nAssistant > {response}\n", "34;1")

            # Update history for multi-turn context
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})

        except KeyboardInterrupt:
            print_colored("\nShutting down...", "33")
            break
        except Exception as e:
            print_colored(f"\nError: {e}", "31")

if __name__ == "__main__":
    main()