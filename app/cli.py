import argparse, asyncio
from pathlib import Path
from dotenv import load_dotenv
from langgraph.types import Command
from .graph import build_graph
async def main():
    load_dotenv()
    parser = argparse.ArgumentParser(); parser.add_argument("--patient-id", required=True); parser.add_argument("--note", required=True)
    args = parser.parse_args(); graph = build_graph(); config = {"configurable": {"thread_id": f"cli-{args.patient_id}"}}
    note = Path(args.note).read_text(encoding="utf-8")
    result = await graph.ainvoke({"patient_id": args.patient_id, "clinical_note": note}, config)
    if result.get("error"): print(f"ERROR: {result['error']}"); return
    print(f"Proposed recommendation: {result['recommendation']}"); print(f"Reason: {result['reason']}")
    final = await graph.ainvoke(Command(resume=input("Accept this recommendation? (yes/no) ")), config)
    print(final["final_outcome"])
if __name__ == "__main__": asyncio.run(main())
