import asyncio
from pathlib import Path
from langgraph.types import Command
from app.graph import build_graph
from app.reader import ClinicalFacts, FixtureReader
ROOT = Path(__file__).resolve().parent
CASES = [("P001",10,8,"Approve"),("P002",12,8,"Deny"),("P003",9,None,"Need more information")]
async def run_case(patient_id, pain, physio, expected):
    note = (ROOT / "data" / f"{patient_id}.txt").read_text(encoding="utf-8")
    graph = build_graph(FixtureReader({note.strip(): ClinicalFacts(pain_weeks=pain, physio_weeks=physio)}))
    config = {"configurable": {"thread_id": f"test-{patient_id}"}}
    proposed = await graph.ainvoke({"patient_id": patient_id, "clinical_note": note}, config)
    if proposed.get("recommendation") != expected: return False
    final = await graph.ainvoke(Command(resume="yes"), config)
    return final.get("final_outcome", "").startswith(expected + ":")
async def main():
    ok = True
    for case in CASES:
        passed = await run_case(*case); print(f"{case[0]}: {'PASS' if passed else 'FAIL'}"); ok &= passed
    return 0 if ok else 1
if __name__ == "__main__": raise SystemExit(asyncio.run(main()))
