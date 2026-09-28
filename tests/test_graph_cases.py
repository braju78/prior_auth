from pathlib import Path
import pytest
from langgraph.types import Command
from app.graph import build_graph
from app.reader import ClinicalFacts, FixtureReader
@pytest.mark.anyio
async def test_required_cases():
    root = Path(__file__).resolve().parents[1]
    for patient_id, pain, physio, expected in [("P001",10,8,"Approve"),("P002",12,8,"Deny"),("P003",9,None,"Need more information")]:
        note = (root / "data" / f"{patient_id}.txt").read_text(encoding="utf-8")
        graph = build_graph(FixtureReader({note.strip(): ClinicalFacts(pain_weeks=pain, physio_weeks=physio)}))
        config = {"configurable": {"thread_id": f"pytest-{patient_id}"}}
        proposed = await graph.ainvoke({"patient_id":patient_id,"clinical_note":note}, config)
        assert proposed["recommendation"] == expected
        final = await graph.ainvoke(Command(resume="yes"), config)
        assert final["final_outcome"].startswith(expected + ":")
