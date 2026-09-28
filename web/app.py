import uuid
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from langgraph.types import Command
from app.graph import build_graph
app = FastAPI(title="MRI Prior Authorization Assistant"); graph = build_graph()
PAGE = """<!doctype html><html><body><h1>MRI Prior Authorization Assistant</h1><form method="post" action="/review"><input name="patient_id" value="P001" required><textarea name="clinical_note" rows="8" required>Patient reports lower back pain for 10 weeks. Patient completed physiotherapy for 8 weeks.</textarea><button>Review Request</button></form>{body}</body></html>"""
@app.get("/", response_class=HTMLResponse)
async def index(): return PAGE.format(body="")
@app.post("/review", response_class=HTMLResponse)
async def review(patient_id: str = Form(...), clinical_note: str = Form(...)):
    thread_id = str(uuid.uuid4()); config = {"configurable":{"thread_id":thread_id}}
    result = await graph.ainvoke({"patient_id":patient_id,"clinical_note":clinical_note}, config)
    if result.get("error"): return PAGE.format(body=f"<p>Error: {result['error']}</p>")
    body=f"<h2>Proposed recommendation: {result['recommendation']}</h2><p>{result['reason']}</p><form method='post' action='/review/{thread_id}'><button name='response' value='yes'>Accept</button><button name='response' value='no'>Reject</button></form>"
    return PAGE.format(body=body)
@app.post("/review/{thread_id}", response_class=HTMLResponse)
async def resume(thread_id: str, response: str = Form(...)):
    result = await graph.ainvoke(Command(resume=response), {"configurable":{"thread_id":thread_id}})
    return PAGE.format(body=f"<h2>Final outcome</h2><p>{result['final_outcome']}</p>")
