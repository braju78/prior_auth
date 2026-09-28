from pathlib import Path
import json
from mcp.server.fastmcp import FastMCP
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
mcp = FastMCP("prior-authorization-server")
def _load(name):
    with (DATA_DIR / name).open(encoding="utf-8") as f: return json.load(f)
@mcp.tool()
def get_patient(patient_id: str) -> dict:
    """Return fictional patient name and plan status."""
    for patient in _load("patients.json"):
        if patient["patient_id"] == patient_id: return patient
    raise ValueError(f"Unknown patient ID: {patient_id}")
@mcp.tool()
def get_rule() -> dict:
    """Return the prior-authorization rule and thresholds."""
    return _load("rule.json")
if __name__ == "__main__": mcp.run(transport="stdio")
