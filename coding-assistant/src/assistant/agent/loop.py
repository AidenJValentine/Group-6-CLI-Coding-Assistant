"""Minimal agent loop for coordinating assistant turns."""

from assistant.providers.dummy_provider import DummyProvider


def run_agent(task: str) -> str:
    """Run the current single-task agent flow."""
    provider = DummyProvider()
    max_iterations = 3

    # Represent the task as a message list so the interface matches future providers.
    messages = [{"role": "user", "content": task}]
    final_text = ""

    for iteration in range(1, max_iterations + 1):
        # Each pass through this loop can later represent one reasoning step.
        current_iteration = iteration

        # This is where the agent would decide whether to call a tool.
        # Future tool outputs can be captured as observations and added to messages.

        response = provider.generate(messages)
        final_text = response.get("text", "")

        # Observations from tool calls or intermediate reasoning will later be
        # appended to the message list here before the next iteration begins.

        # For now, the dummy provider completes the task in one pass.
        if final_text:
            break

    return final_text
