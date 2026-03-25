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

from langgraph.graph import StateGraph, END
from langgraph.types import Send

from assistant.agent.state import AgentState


# ---------------------------------------------------------------------------
# Node stubs — topology only, no logic yet
# ---------------------------------------------------------------------------

def input_handler(state: AgentState) -> AgentState:
    """Route slash commands out early; pass regular tasks to mode_classifier."""
    raise NotImplementedError


def handle_slash_command(state: AgentState) -> AgentState:
    """Process a slash command (e.g. /mode debug) and return to idle."""
    raise NotImplementedError


def mode_classifier(state: AgentState) -> AgentState:
    """Read execution_mode and route to the appropriate subgraph."""
    raise NotImplementedError


# --- Debug subgraph (ReAct) -------------------------------------------------

def agent_node(state: AgentState) -> AgentState:
    """Call the LLM (agent_model) and decide: tool call or final answer."""
    raise NotImplementedError


def tool_executor(state: AgentState) -> AgentState:
    """Execute the tool requested in the last message and append the result."""
    raise NotImplementedError


# --- Build subgraph (plan-and-execute) --------------------------------------

def planner_node(state: AgentState) -> AgentState:
    """Call planner.py to produce state['plan'] (list of step dicts)."""
    raise NotImplementedError


def parallel_executor(state: AgentState) -> AgentState:
    """Execute a single plan step. Invoked once per Send() fan-out."""
    raise NotImplementedError


def synthesizer(state: AgentState) -> AgentState:
    """Collect parallel_executor results and build the final context."""
    raise NotImplementedError


# --- Shared exit node -------------------------------------------------------

def responder(state: AgentState) -> AgentState:
    """Stream final output to CLI and save to history."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Conditional edge functions
# ---------------------------------------------------------------------------

def route_input(state: AgentState) -> str:
    """Return 'slash' if input starts with '/', else 'task'."""
    raise NotImplementedError


def route_mode(state: AgentState) -> str:
    """Return 'debug' or 'build' based on state['execution_mode']."""
    raise NotImplementedError


def route_agent(state: AgentState) -> str:
    """Return 'tool' if last message has a tool_call, else 'done'."""
    raise NotImplementedError


def fan_out_plan(state: AgentState) -> list[Send]:
    """Return a Send() for each step in state['plan'] (all independent in MVP)."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("input_handler", input_handler)
    graph.add_node("handle_slash_command", handle_slash_command)
    graph.add_node("mode_classifier", mode_classifier)
    graph.add_node("agent_node", agent_node)
    graph.add_node("tool_executor", tool_executor)
    graph.add_node("planner_node", planner_node)
    graph.add_node("parallel_executor", parallel_executor)
    graph.add_node("synthesizer", synthesizer)
    graph.add_node("responder", responder)

    # Entry point
    graph.set_entry_point("input_handler")

    # input_handler → slash command path or task path
    graph.add_conditional_edges(
        "input_handler",
        route_input,
        {"slash": "handle_slash_command", "task": "mode_classifier"},
    )
    graph.add_edge("handle_slash_command", END)

    # mode_classifier → debug or build subgraph
    graph.add_conditional_edges(
        "mode_classifier",
        route_mode,
        {"debug": "agent_node", "build": "planner_node"},
    )

    # Debug subgraph: ReAct loop
    graph.add_conditional_edges(
        "agent_node",
        route_agent,
        {"tool": "tool_executor", "done": "responder"},
    )
    graph.add_edge("tool_executor", "agent_node")

    # Build subgraph: plan → fan-out → synthesize
    graph.add_conditional_edges("planner_node", fan_out_plan)
    graph.add_edge("parallel_executor", "synthesizer")
    graph.add_edge("synthesizer", "responder")

    # Shared exit
    graph.add_edge("responder", END)

    return graph


# Compiled graph — import this in the CLI
agent_graph = build_graph().compile()
