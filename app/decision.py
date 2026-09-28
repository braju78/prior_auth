from .state import AuthorizationState, Recommendation
def evaluate_policy(state: AuthorizationState) -> tuple[Recommendation, str]:
    if not state["plan_active"]:
        return "Deny", "The patient's plan is inactive."
    pain, physio = state.get("pain_weeks"), state.get("physio_weeks")
    pain_threshold, physio_threshold = state["pain_threshold_weeks"], state["physio_threshold_weeks"]
    if pain is not None and pain < pain_threshold:
        return "Deny", f"Back pain duration is {pain:g} weeks, below the {pain_threshold:g}-week requirement."
    if physio is not None and physio < physio_threshold:
        return "Deny", f"Physiotherapy duration is {physio:g} weeks, below the {physio_threshold:g}-week requirement."
    if pain is None or physio is None:
        return "Need more information", "The note does not establish both required durations."
    return "Approve", "The plan is active and both required durations meet the six-week threshold."
