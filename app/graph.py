from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from .decision import evaluate_policy
from .mcp_client import MCPApplicationClient
from .reader import LLMReader, Reader
from .state import AuthorizationState
def build_graph(reader: Reader | None = None):
    reader = reader or LLMReader()
    async def load_context(state):
        try:
            async with MCPApplicationClient() as mcp:
                patient, rule = await mcp.get_patient(state["patient_id"]), await mcp.get_rule()
        except Exception as exc: return {"error": f"MCP error: {exc}"}
        return {"patient_name": patient["name"], "plan_active": patient["plan_active"], "rule_text": rule["rule_text"], "evaluation_order": rule["evaluation_order"], "pain_threshold_weeks": rule["pain_threshold_weeks"], "physio_threshold_weeks": rule["physio_threshold_weeks"]}
    async def read_note(state):
        if state.get("error"): return {}
        try: facts = await reader.extract(state["clinical_note"])
        except Exception as exc: return {"error": f"Reader error: {exc}"}
        return {"pain_weeks": facts.pain_weeks, "physio_weeks": facts.physio_weeks}
    def decide(state):
        if state.get("error"): return {}
        recommendation, reason = evaluate_policy(state)
        return {"recommendation": recommendation, "reason": reason}
    def human_review(state):
        if state.get("error"): return {}
        response = interrupt({"recommendation": state["recommendation"], "reason": state["reason"], "message": "Accept this recommendation? (yes/no)"})
        return {"final_outcome": f"{state['recommendation']}: {state['reason']}"} if str(response).strip().lower() == "yes" else {"final_outcome": "Decision rejected by reviewer"}
    def route(state): return "error" if state.get("error") else "read_note"
    def route_read(state): return "error" if state.get("error") else "decide"
    workflow = StateGraph(AuthorizationState)
    for name, node in [("load_context", load_context), ("read_note", read_note), ("decide", decide), ("human_review", human_review), ("error", lambda state: {})]: workflow.add_node(name, node)
    workflow.add_edge(START, "load_context")
    workflow.add_conditional_edges("load_context", route, {"read_note": "read_note", "error": "error"})
    workflow.add_conditional_edges("read_note", route_read, {"decide": "decide", "error": "error"})
    workflow.add_edge("decide", "human_review"); workflow.add_edge("human_review", END); workflow.add_edge("error", END)
    return workflow.compile(checkpointer=InMemorySaver())
