"""Mock MCP client for development and testing before the real MCP module is ready."""


class MockMCPClient:
    async def call_tool(self, name: str, args: dict) -> str:
        return f"[mock result for {name} with args {args}]"
