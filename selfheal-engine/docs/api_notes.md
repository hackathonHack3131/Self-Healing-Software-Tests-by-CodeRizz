# Deep Agents & Gemini API Notes

> Verified against installed packages (`deepagents==0.7.23`, `langchain-google-genai==4.4.0`, `langchain==1.4.4`, `langchain-core==1.6.9`) and official documentation per Rule 13.

## create_deep_agent signature

`create_deep_agent` is imported from `deepagents` and has the following signature:

```python
def create_deep_agent(
    model: str | BaseChatModel | None = None,
    tools: Sequence[BaseTool | Callable | dict[str, Any]] | None = None,
    *,
    system_prompt: str | SystemMessage | None = None,
    middleware: Sequence[AgentMiddleware] = (),
    subagents: Sequence[SubAgent | CompiledSubAgent | AsyncSubAgent] | None = None,
    skills: list[str] | None = None,
    memory: list[str] | None = None,
    permissions: list[FilesystemPermission] | None = None,
    backend: BackendProtocol | None = None,
    interrupt_on: dict[str, bool | InterruptOnConfig] | None = None,
    response_format: ResponseFormat[ResponseT] | type[ResponseT] | dict[str, Any] | None = None,
    state_schema: type[DeepAgentState] | None = None,
    context_schema: type[ContextT] | None = None,
    checkpointer: None | bool | BaseCheckpointSaver = None,
    store: BaseStore | None = None,
    debug: bool = False,
    name: str | None = None,
    cache: BaseCache | None = None,
) -> CompiledStateGraph:
    ...
```

The returned object is a LangGraph `CompiledStateGraph` with a recursion limit defaulted to 9,999.

## Gemini model string format

- String format: `google_genai:<model_id>` (e.g., `google_genai:gemini-2.5-flash` or `google_genai:gemini-2.0-flash`).
- Resolution: `deepagents._models.resolve_model` routes model strings through `langchain.chat_models.init_chat_model`.
- Provider routing: The `google_genai` prefix specifically routes to `langchain-google-genai` (`ChatGoogleGenerativeAI`) which requires `GOOGLE_API_KEY`.
- Note: A bare `gemini...` string without prefix infers `google_vertexai`, so the explicit `google_genai:` prefix is mandatory when using Google AI Studio API keys.

## Structured output result key

- Passing a Pydantic model type to `response_format` configures structured output in `create_agent`.
- The graph output state schema (`OutputAgentState`) defines the key `structured_response` (`NotRequired[ResponseT]`).
- When running `await agent.ainvoke({"messages": [...]})`, the parsed structured model output is accessed via:
  ```python
  result["structured_response"]
  ```
  while conversation history is in `result["messages"]`.

## Streaming call

- The compiled graph provides async streaming via `astream`:
  ```python
  async for chunk in agent.astream({"messages": [HumanMessage(content=prompt)]}, stream_mode="updates"):
      ...
  ```
- Standard LangGraph `stream_mode` options (`"updates"`, `"values"`, `"messages"`) are supported.

## Tool definition style

- Tools can be defined using the standard `@tool` decorator from `langchain_core.tools`:
  ```python
  from langchain_core.tools import tool

  @tool
  def click_button(accessible_name: str) -> str:
      """Click a button identified by its exact accessible name."""
      ...
  ```
- Function docstrings serve as the tool description, and parameter type hints define the JSON Schema arguments passed to the LLM.
