from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, END
from app.agents.planner.planner import plan_checkin

# -------------------------
# Agent State Definition
# -------------------------


# class AgentState(TypedDict):
#     patient_id: int
#     checkin_id: str  # using string to accommodate UUIDs

#     # planner output (later)
#     plan: Optional[Dict[str, Any]]

#     # policy-gated plan (later)
#     gated_plan: Optional[Dict[str, Any]]

#     # tool execution results (later)
#     tool_results: List[Dict[str, Any]]

#     # lifecycle status
#     status: str

class AgentState(TypedDict):
    # identifiers
    patient_id: int
    checkin_id: str

    # hydrated context (READ-ONLY for planner)
    patient: Dict[str, Any]
    checkin: Dict[str, Any]

    # planner output
    plan: Optional[Dict[str, Any]]

    # policy-gated plan
    gated_plan: Optional[Dict[str, Any]]

    # tool execution results
    tool_results: List[Dict[str, Any]]

    # lifecycle status
    status: str



# -------------------------
# Node Implementations
# -------------------------

# def planner_node(state: AgentState) -> AgentState:
#     """
#     Placeholder planner.
#     No LLM yet.
#     """
#     state["plan"] = None
#     state["status"] = "PLANNED_NOOP"
#     return state


def planner_node(state):
    plan = plan_checkin(
        checkin=state["checkin"],
        patient=state["patient"],
    )

    state["plan"] = plan
    return state


def policy_gate_node(state: AgentState) -> AgentState:
    """
    Placeholder policy gate.
    """
    state["gated_plan"] = None
    state["status"] = "GATED_NOOP"
    return state


def act_node(state: AgentState) -> AgentState:
    """
    Placeholder action executor.
    """
    state["tool_results"] = []
    state["status"] = "COMPLETED_NOOP"
    return state


# -------------------------
# Graph Builder
# -------------------------


def build_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("policy_gate", policy_gate_node)
    graph.add_node("act", act_node)

    graph.set_entry_point("planner")

    graph.add_edge("planner", "policy_gate")
    graph.add_edge("policy_gate", "act")
    graph.add_edge("act", END)

    return graph.compile()
