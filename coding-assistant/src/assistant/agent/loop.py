"""LangGraph state machine for the assistant agent loop."""

from dataclasses import dataclass

try:
    from langgraph.graph import END, StateGraph
    from langgraph.types import Send

    LANGGRAPH_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - fallback for local bootstrap
    END = object()
    StateGraph = None
    LANGGRAPH_AVAILABLE = False

    @dataclass
    class Send:
        """Minimal fallback Send type used when LangGraph is unavailable."""

        node: str
        arg: dict

from assistant.agent.message_builder import build_initial_messages
from assistant.agent.planner import build_mock_plan
from assistant.agent.state import AgentState
from assistant.cli.prompts import HELP_TEXT
from assistant.providers.dummy_provider import DummyProvider
from assistant.tools.executor import invoke_tool


def input_handler(state: AgentState) -> AgentState:
    """Route slash commands out early; pass regular tasks to mode_classifier."""
    state["status"] = "running"
    state["latest_events"] = []
    if state["original_task"].strip().startswith("/"):
        state["slash_command"] = state["original_task"].strip()
    else:
        state["messages"] = build_initial_messages(state["original_task"])
    return state


def handle_slash_command(state: AgentState) -> AgentState:
    """Process simple slash commands for the REPL."""
    command = state.get("slash_command", "").strip()

    if command == "/help":
        state["final_answer"] = HELP_TEXT
        state["status"] = "completed"
        return state

    if command == "/exit":
        state["final_answer"] = "Exiting assistant session."
        state["status"] = "cancelled"
        state["exit_requested"] = True
        return state

    if command == "/mode debug":
        state["execution_mode"] = "debug"
        state["final_answer"] = "Switched to debug mode."
        state["status"] = "completed"
        return state

    if command == "/mode build":
        state["execution_mode"] = "build"
        state["final_answer"] = "Switched to build mode."
        state["status"] = "completed"
        return state

    state["final_answer"] = "Unknown command. Type /help for available commands."
    state["status"] = "failed"
    return state


def mode_classifier(state: AgentState) -> AgentState:
    """Pass state through; routing happens in the edge function."""
    return state


def agent_node(state: AgentState) -> AgentState:
    """Call the mock provider and decide whether to use a tool or finish."""
    if state["iteration_count"] >= state["max_iterations"]:
        state["final_answer"] = "Max iterations reached. Stopping."
        state["status"] = "failed"
        state["pending_tool_call"] = None
        return state

    provider = state.get("provider") or DummyProvider()
    response = provider.generate(state["messages"])
    assistant_message = {
        "role": "assistant",
        "content": response.get("text", ""),
    }
    if "tool_call" in response:
        assistant_message["tool_call"] = response["tool_call"]
        state["pending_tool_call"] = response["tool_call"]
    else:
        state["pending_tool_call"] = None
        state["final_answer"] = response.get("text", "")
        state["status"] = "completed"

    state["messages"].append(assistant_message)
    state["iteration_count"] += 1
    return state


def tool_executor(state: AgentState) -> AgentState:
    """Execute the pending mock tool call and append the result."""
    tool_call = state.get("pending_tool_call")
    if not tool_call:
        return state

    event = {
        "tool_name": tool_call["name"],
        "args": tool_call.get("args", {}),
        "status": "requested",
    }

    approved = True
    if state.get("approval_mode") == "confirm":
        approval_handler = state.get("approval_handler")
        if approval_handler is not None:
            approved = approval_handler(tool_call)

    if not approved:
        event["status"] = "denied"
        event["result"] = "User denied tool execution."
        state["messages"].append(
            {"role": "tool", "name": tool_call["name"], "content": event["result"]}
        )
        state["tool_history"].append(event)
        state["latest_events"] = [event]
        state["pending_tool_call"] = None
        return state

    result = invoke_tool(tool_call["name"], tool_call.get("args", {}))
    event["status"] = "completed"
    event["result"] = result
    state["messages"].append(
        {"role": "tool", "name": tool_call["name"], "content": result}
    )
    state["tool_history"].append(event)
    state["latest_events"] = [event]
    state["pending_tool_call"] = None
    return state


def planner_node(state: AgentState) -> AgentState:
    """Build a mock one-step plan for build mode demos."""
    state["plan"] = build_mock_plan(state["original_task"])
    return state


def parallel_executor(state: AgentState) -> AgentState:
    """Execute a single mocked plan step."""
    step = state["current_step"]
    state["step_results"] = [
        {
            "id": step["id"],
            "step": step["step"],
            "result": f"Completed mocked build step: {step['step']}",
        }
    ]
    return state


def synthesizer(state: AgentState) -> AgentState:
    """Collect mocked plan results and produce a final answer."""
    step_results = state.get("step_results", [])
    if not step_results:
        state["final_answer"] = "Build mode ran, but no plan results were produced."
        state["status"] = "failed"
        return state

    lines = ["Build mode mock execution summary:"]
    for result in step_results:
        lines.append(f"- {result['result']}")
    state["final_answer"] = "\n".join(lines)
    state["status"] = "completed"
    return state


def responder(state: AgentState) -> AgentState:
    """Fill in any missing final answer before ending the graph."""
    if not state.get("final_answer"):
        last_assistant_message = next(
            (
                message["content"]
                for message in reversed(state.get("messages", []))
                if message["role"] == "assistant"
            ),
            "",
        )
        state["final_answer"] = last_assistant_message
    state["status"] = state.get("status", "completed")
    return state


def route_input(state: AgentState) -> str:
    """Return 'slash' if input starts with '/', else 'task'."""
    return "slash" if state["original_task"].strip().startswith("/") else "task"


def route_mode(state: AgentState) -> str:
    """Return 'debug' or 'build' based on execution_mode."""
    return state.get("execution_mode", "debug")


def route_agent(state: AgentState) -> str:
    """Return 'tool' if the assistant requested a tool call, else 'done'."""
    return "tool" if state.get("pending_tool_call") else "done"


def fan_out_plan(state: AgentState) -> list[Send]:
    """Return one Send per plan step."""
    return [
        Send("parallel_executor", {**state, "current_step": step})
        for step in state.get("plan", [])
    ]


def _invoke_without_langgraph(initial_state: AgentState) -> AgentState:
    """Run the same control flow without the LangGraph dependency."""
    state = input_handler(initial_state)

    if route_input(state) == "slash":
        return handle_slash_command(state)

    state = mode_classifier(state)
    if route_mode(state) == "debug":
        while True:
            state = agent_node(state)
            if route_agent(state) == "done":
                return responder(state)
            state = tool_executor(state)

    state = planner_node(state)
    sends = fan_out_plan(state)
    if not sends:
        return responder(synthesizer(state))
    step_state = parallel_executor(sends[0].arg)
    return responder(synthesizer(step_state))


if LANGGRAPH_AVAILABLE:
    def build_graph() -> StateGraph:
        """Build the Milestone 2 assistant graph."""
        graph = StateGraph(AgentState)
        graph.add_node("input_handler", input_handler)
        graph.add_node("handle_slash_command", handle_slash_command)
        graph.add_node("mode_classifier", mode_classifier)
        graph.add_node("agent_node", agent_node)
        graph.add_node("tool_executor", tool_executor)
        graph.add_node("planner_node", planner_node)
        graph.add_node("parallel_executor", parallel_executor)
        graph.add_node("synthesizer", synthesizer)
        graph.add_node("responder", responder)

        graph.set_entry_point("input_handler")
        graph.add_conditional_edges(
            "input_handler",
            route_input,
            {"slash": "handle_slash_command", "task": "mode_classifier"},
        )
        graph.add_edge("handle_slash_command", END)
        graph.add_conditional_edges(
            "mode_classifier",
            route_mode,
            {"debug": "agent_node", "build": "planner_node"},
        )
        graph.add_conditional_edges(
            "agent_node",
            route_agent,
            {"tool": "tool_executor", "done": "responder"},
        )
        graph.add_edge("tool_executor", "agent_node")
        graph.add_conditional_edges("planner_node", fan_out_plan)
        graph.add_edge("parallel_executor", "synthesizer")
        graph.add_edge("synthesizer", "responder")
        graph.add_edge("responder", END)
        return graph


    agent_graph = build_graph().compile()
else:
    agent_graph = None


def run_agent(
    task: str,
    session_state: dict,
    *,
    max_iterations: int,
    approval_mode: str,
    approval_handler,
) -> AgentState:
    """Run one user task through the compiled graph or local fallback."""
    initial_state: AgentState = {
        "original_task": task,
        "messages": [],
        "iteration_count": 0,
        "max_iterations": max_iterations,
        "execution_mode": session_state.get("execution_mode", "debug"),
        "tool_history": [],
        "plan": [],
        "final_answer": "",
        "status": "running",
        "approval_mode": approval_mode,
        "pending_tool_call": None,
        "latest_events": [],
        "step_results": [],
        "exit_requested": False,
        "provider": DummyProvider(),
        "approval_handler": approval_handler,
    }
    if agent_graph is None:
        return _invoke_without_langgraph(initial_state)
    return agent_graph.invoke(initial_state)
