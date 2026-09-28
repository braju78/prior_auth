import json
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
class MCPApplicationClient:
    def __init__(self):
        server = Path(__file__).resolve().parents[1] / "mcp_server" / "server.py"
        self.params = StdioServerParameters(command=sys.executable, args=[str(server)])
        self.stack, self.session = AsyncExitStack(), None
    async def __aenter__(self):
        read, write = await self.stack.enter_async_context(stdio_client(self.params))
        self.session = await self.stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()
        return self
    async def __aexit__(self, exc_type, exc, tb): await self.stack.aclose()
    async def _call(self, name, arguments):
        result = await self.session.call_tool(name, arguments)
        if result.isError: raise RuntimeError(f"MCP tool {name} failed")
        if getattr(result, "structuredContent", None): return result.structuredContent
        if result.content and getattr(result.content[0], "text", None): return json.loads(result.content[0].text)
        raise RuntimeError(f"MCP tool {name} returned no data")
    async def get_patient(self, patient_id): return await self._call("get_patient", {"patient_id": patient_id})
    async def get_rule(self): return await self._call("get_rule", {})
