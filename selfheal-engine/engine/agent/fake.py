"""Scripted FakeAgent for deterministic unit and integration tests.

Used only in automated tests to simulate Deep Agent actions and failure cases
without making external LLM API calls.
"""

from typing import Any, Callable
from langchain_core.tools import BaseTool


class FakeAgent:
    """Scripted mock agent conforming to LangGraph / Deep Agent ainvoke interface."""

    def __init__(
        self,
        scripted_calls: list[tuple[str, dict[str, Any]]] | None = None,
        tools: list[BaseTool] | None = None,
        custom_coro: Callable[..., Any] | None = None,
    ):
        self.scripted_calls = list(scripted_calls or [])
        self.tools = {t.name: t for t in tools} if tools else {}
        self.custom_coro = custom_coro
        self.invoked = False
        self.inputs_received: list[dict[str, Any]] = []

    def set_tools(self, tools: list[BaseTool]) -> None:
        """Register or update tools available to the fake agent."""
        self.tools = {t.name: t for t in tools}

    async def ainvoke(
        self, inputs: dict[str, Any], config: Any = None, **kwargs: Any
    ) -> dict[str, Any]:

        """Execute scripted actions sequentially through the registered tools."""
        self.invoked = True
        self.inputs_received.append(inputs)

        if self.custom_coro:
            return await self.custom_coro(self.tools, inputs)

        results = []
        for tool_name, kwargs in self.scripted_calls:
            tool = self.tools.get(tool_name)
            if tool is not None:
                res = await tool.ainvoke(kwargs)
                results.append({"tool": tool_name, "args": kwargs, "output": res})
            else:
                results.append({"tool": tool_name, "error": f"Tool '{tool_name}' not found"})

        return {
            "messages": [
                {"role": "assistant", "content": "Fake agent completed scripted plan."}
            ],
            "execution_log": results,
        }
