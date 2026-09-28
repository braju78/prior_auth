from typing import Literal, TypedDict
Recommendation = Literal["Approve", "Deny", "Need more information"]
class AuthorizationState(TypedDict, total=False):
    patient_id: str
    clinical_note: str
    patient_name: str
    plan_active: bool
    rule_text: str
    evaluation_order: list[str]
    pain_threshold_weeks: float
    physio_threshold_weeks: float
    pain_weeks: float | None
    physio_weeks: float | None
    recommendation: Recommendation
    reason: str
    final_outcome: str
    error: str
