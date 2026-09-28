from app.decision import evaluate_policy
def state(**overrides):
    value = {"plan_active":True,"pain_weeks":10,"physio_weeks":8,"pain_threshold_weeks":6,"physio_threshold_weeks":6}; value.update(overrides); return value
def test_inactive_plan(): assert evaluate_policy(state(plan_active=False))[0] == "Deny"
def test_exactly_six_weeks(): assert evaluate_policy(state(pain_weeks=6, physio_weeks=6))[0] == "Approve"
def test_short_pain(): assert evaluate_policy(state(pain_weeks=5))[0] == "Deny"
def test_short_physio(): assert evaluate_policy(state(physio_weeks=5))[0] == "Deny"
def test_missing_duration(): assert evaluate_policy(state(physio_weeks=None))[0] == "Need more information"
def test_no_physio_is_zero(): assert evaluate_policy(state(physio_weeks=0))[0] == "Deny"
