"""Prompt text and input helpers for the CLI."""

HELP_TEXT = "\n".join(
    [
        "Available commands:",
        "  /help        Show this help message",
        "  /mode debug  Switch to debug mode",
        "  /mode build  Switch to build mode",
        "  /exit        Quit the assistant",
    ]
)


def prompt_for_approval(tool_call: dict) -> bool:
    """Ask the user to approve or deny a tool call."""
    tool_name = tool_call.get("name", "unknown_tool")
    tool_args = tool_call.get("args", {})

    while True:
        reply = input(
            f"Approve tool '{tool_name}' with args {tool_args}? "
            "[approve/deny]: "
        ).strip().lower()
        if reply in {"approve", "a", "yes", "y"}:
            return True
        if reply in {"deny", "d", "no", "n"}:
            return False
        print("Please type 'approve' or 'deny'.")
