"""LangGraph state machine for the assistant agent loop.

Graph topology:
    input_handler
        ├─ slash command ──► handle_slash_command ──► END
        └─ task ──────────► mode_classifier
                                ├─ debug ──► [Debug subgraph]
                                │             agent_node
                                │               ├─ tool_call ──► tool_executor ──► agent_node
                                │               └─ done ───────────────────────► responder
                                └─ build ──► [Build subgraph]
                                              planner_node
                                                └─ Send() fan-out ──► parallel_executor
                                                                         └─ synthesizer ──► responder
    responder ──► END
"""

import asyncio

from langgraph.graph import StateGraph, END
from langgraph.types import Send

from assistant.agent.state import AgentState
from assistant.agent.planner import make_plan
from assistant.providers.litellm_client import call_llm
from assistant.config import load_provider_config, RuntimeConfig
from assistant.mcp.mock_client import MockMCPClient
from assistant.tools.executor import invoke_tool
from assistant.tools.registry import TOOL_REGISTRY, load_rag_tool

# Register real tools once at import time
load_rag_tool()


# ---------------------------------------------------------------------------
# Tool classification and mock tool schema
# ---------------------------------------------------------------------------

TOOL_CLASSES = {
    "read":  ["read_file", "list_directory", "search_docs", "web_search"],
    "write": ["write_file", "edit_file", "run_command", "delete_file"],
}

MOCK_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Search the documentation index for relevant information about a library or API",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "the search query"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file at the given path",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file at the given path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def input_handler(state: AgentState) -> AgentState:
    """Passthrough — routing is handled by the route_input conditional edge."""
    return state


def handle_slash_command(state: AgentState) -> AgentState:
    """Process a slash command and return updated state."""
    content = state["messages"][-1]["content"].strip()
    update: dict = {}

    if content == "/mode debug":
        reply = "Mode switched to debug."
        update["execution_mode"] = "debug"
    elif content == "/mode build":
        reply = "Mode switched to build."
        update["execution_mode"] = "build"
    elif content == "/help":
        reply = "Available commands: /mode debug, /mode build, /help, /exit"
    elif content == "/exit":
        reply = "Goodbye."
        update["exit_requested"] = True
    else:
        reply = "Unknown command. Try /help."

    update["messages"] = list(state["messages"]) + [{"role": "system", "content": reply}]
    update["status"] = "completed"
    return update


def mode_classifier(state: AgentState) -> AgentState:
    """Passthrough — routing is handled by the route_mode conditional edge."""
    return state


# --- Debug subgraph (ReAct) -------------------------------------------------

SYSTEM_PROMPT = """You are a helpful coding assistant with access to these tools: {tool_names}.

Rules:
- Call tools to find information before answering
- After getting tool results, write your answer as plain conversational text
- Never output JSON, dicts, or code blocks as your final answer
- Never invent tool names outside the list above
- When you have enough information, just answer directly in plain English"""


def agent_node(state: AgentState) -> AgentState:
    """Call the LLM (agent_model) and append the response to messages."""
    # Early exit if already at or over the limit (guards against LangGraph queuing
    # one extra tick after the post-increment check fires)
    if state["iteration_count"] >= state["max_iterations"]:
        return {
            "status": "failed",
            "final_answer": "Max iterations reached. Stopping.",
        }

    agent_model = load_provider_config()["agent_model"]
    tool_names = ", ".join([t["function"]["name"] for t in MOCK_TOOLS])

    system_message = {"role": "system", "content": SYSTEM_PROMPT.format(tool_names=tool_names)}

    # On turn 1 (no prior assistant messages) inject a conversational primer so
    # the model responds with prose rather than a structured JSON blob.
    # On turns 2+ the accumulated tool/assistant history already anchors tone —
    # inserting the primer would produce two consecutive assistant messages, which
    # is invalid for strict providers like Claude.
    has_prior_assistant = any(m.get("role") == "assistant" for m in state["messages"])
    if not has_prior_assistant:
        first_user = state["messages"][0] if state["messages"] else {"role": "user", "content": ""}
        rest = state["messages"][1:]
        messages_with_system = [
            system_message,
            first_user,
            {"role": "assistant", "content": "I'll help with that. Let me search the documentation."},
        ] + rest
    else:
        messages_with_system = [system_message] + state["messages"]

    result = call_llm(agent_model, messages_with_system, tools=MOCK_TOOLS)
    iteration_count = state["iteration_count"] + 1

    if result["tool_calls"]:
        # Tool-call turn: keep in history so tool_executor can read it
        messages = list(state["messages"]) + [
            {
                "role": "assistant",
                "content": result["text"],
                "tool_calls": result["tool_calls"],
            }
        ]
        update: dict = {"messages": messages, "iteration_count": iteration_count}
    else:
        # Final answer turn: don't append to history — stash in _pending_final
        # to avoid re-anchoring subsequent calls to whatever format the model used
        update = {"iteration_count": iteration_count, "_pending_final": result["text"] or ""}

    if iteration_count >= state["max_iterations"]:
        update["status"] = "failed"
        update["final_answer"] = "Max iterations reached. Stopping."

    return update


def tool_executor(state: AgentState) -> AgentState:
    """Execute the tool requested in the last message and append the result."""
    import json

    tool_call = state["messages"][-1]["tool_calls"][0]
    name = tool_call["function"]["name"]
    raw_args = tool_call["function"]["arguments"]
    args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
    tool_call_id = tool_call.get("id", name)

    # Write-class tools in debug mode require confirmation
    is_write = name in TOOL_CLASSES["write"]
    needs_confirm = is_write and state["execution_mode"] == "debug"

    if needs_confirm:
        print(f"Tool: {name} | Args: {args} | Approve? (y/n): ", end="", flush=True)
        answer = input().strip().lower()
        if answer != "y":
            messages = list(state["messages"]) + [
                {"role": "tool", "content": "User denied tool execution.", "tool_call_id": tool_call_id}
            ]
            return {"messages": messages}

    if name in TOOL_REGISTRY:
        result = invoke_tool(name, args)
    else:
        result = asyncio.run(MockMCPClient().call_tool(name, args))

    messages = list(state["messages"]) + [
        {"role": "tool", "content": result, "tool_call_id": tool_call_id}
    ]
    return {"messages": messages, "tool_history": [{"tool": name, "args": args, "result": result}]}


# --- Build subgraph (plan-and-execute) --------------------------------------

def planner_node(state: AgentState) -> AgentState:
    """Call planner.py to produce state['plan'] (list of step dicts)."""
    task = state["messages"][-1]["content"]
    plan = make_plan(task)
    return {"plan": plan}


def parallel_executor(state: AgentState) -> AgentState:
    """Execute a single plan step. Invoked once per Send() fan-out."""
    step = state["current_step"]
    print(f"[build] executing: {step['step']}")
    result = asyncio.run(MockMCPClient().call_tool("read_file", {"path": "mock"}))
    # Return delta only — operator.add reducer accumulates across parallel invocations
    return {"tool_history": [{"step_id": step["id"], "step": step["step"], "result": result}]}


def synthesizer(state: AgentState) -> AgentState:
    """Collect all tool_history entries and build the final answer."""
    lines = [
        f"- [{entry['step_id']}] {entry['step']}: {entry['result']}"
        for entry in state["tool_history"]
    ]
    final_answer = "Build results:\n" + "\n".join(lines)
    return {"final_answer": final_answer}


# --- Shared exit node -------------------------------------------------------

def responder(state: AgentState) -> AgentState:
    """Set final_answer and print to stdout.

    Priority: _pending_final (set by agent_node for text-only turns) >
              state["final_answer"] (set by max-iterations guard) >
              last assistant message content (fallback).
    """
    final_answer = (
        state.get("_pending_final")
        or state["final_answer"]
        or next(
            (m.get("content") or "" for m in reversed(state["messages"]) if m.get("role") == "assistant"),
            "",
        )
    )
    print(final_answer)
    return {"final_answer": final_answer, "status": "completed"}


# ---------------------------------------------------------------------------
# Conditional edge functions
# ---------------------------------------------------------------------------

def route_input(state: AgentState) -> str:
    """Return 'slash' if the last message content starts with '/', else 'task'."""
    content = state["messages"][-1]["content"]
    return "slash" if content.startswith("/") else "task"


def route_mode(state: AgentState) -> str:
    """Return 'debug' or 'build' based on state['execution_mode']."""
    mode = state["execution_mode"]
    if mode not in ("debug", "build"):
        raise ValueError(f"Invalid execution_mode: {mode!r}. Must be 'debug' or 'build'.")
    return mode


def route_agent(state: AgentState) -> str:
    """Return 'tool' if the last assistant message has pending tool calls, else 'done'."""
    if state["status"] == "failed":
        return "done"
    last = state["messages"][-1] if state["messages"] else {}
    if last.get("role") == "assistant" and last.get("tool_calls"):
        return "tool"
    return "done"


def fan_out_plan(state: AgentState) -> list[Send]:
    """Return a Send() for each plan step. MVP: all steps are independent."""
    return [
        Send("parallel_executor", {**state, "current_step": step})
        for step in state["plan"]
    ]


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
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


# Compiled graph — import this in the CLI
agent_graph = build_graph().compile()


# ---------------------------------------------------------------------------
# LangGraph-free fallback (from CLI-Interface branch)
# Mirrors the graph control flow without the LangGraph dependency.
# Uses state["messages"][-1]["content"] for slash detection (abhi convention).
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_agent(task: str, config: RuntimeConfig) -> AgentState:
    """Run one user task through the compiled graph.

    Builds a fresh AgentState from make_initial_state(), applies runtime
    config, appends the task as the first user message, then invokes the
    compiled LangGraph.
    """
    from assistant.agent.state import make_initial_state

    state = make_initial_state(
        execution_mode=config.execution_mode,
        max_iterations=config.max_iterations,
    )
    state["approval_mode"] = config.approval_mode
    state["messages"].append({"role": "user", "content": task})
    return agent_graph.invoke(state)
