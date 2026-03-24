"""CLI application loop for reading input and printing responses."""

from assistant.agent.loop import run_agent


def run_cli() -> None:
    """Run the minimal assistant REPL."""
    # Print a short instruction so the user knows how to leave the loop.
    print("Coding Assistant CLI. Type 'exit' or 'quit' to stop.")

    while True:
        try:
            # Read the next line of input using the requested prompt format.
            user_input = input(">> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        normalized_input = user_input.strip()

        # End the session when the user enters a common quit command.
        if normalized_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        # Send the user's task into the agent loop and print the returned response.
        response_text = run_agent(user_input)
        print(response_text)
