# Module Spec: Provider Abstraction

## Goal
Expose a unified LLM call surface using LiteLLM. No provider-specific code paths — switching providers is a config-only change.

## Files
- `src/assistant/providers/litellm_client.py` — thin wrapper around `litellm.completion()`
- `src/assistant/config.py` — config loader (env vars or YAML/TOML)

> The hand-rolled `base.py`, `ollama_provider.py`, and `openai_provider.py` files from the original skeleton are replaced by this design.

## How LiteLLM is used

LiteLLM provides a single call surface across all supported backends:

```python
import litellm

response = litellm.completion(
    model=model_string,   # e.g. "anthropic/claude-opus-4-6"
    messages=messages,
    tools=tools,          # optional
    stream=stream,        # optional
)
```

Model strings follow LiteLLM convention:

| Backend | Example model string |
|---|---|
| Anthropic | `"anthropic/claude-opus-4-6"` |
| OpenAI | `"openai/gpt-4o"` |
| Ollama (local) | `"ollama/llama3"` |
| Groq | `"groq/llama3-70b-8192"` |

## Two required config keys

```yaml
agent_model: "anthropic/claude-opus-4-6"
# Used by: agent_node (debug mode), planner_node (build mode)
# Should be the strongest available model.

executor_model: "ollama/llama3"
# Used by: parallel_executor steps (build mode)
# Should be a cheaper/faster model.
```

These are loaded from environment variables or a config file. The agent loop reads them at startup; no provider-specific imports are needed.

## litellm_client.py interface

```python
def generate(
    model: str,
    messages: list[dict],
    tools: list[dict] | None = None,
    stream: bool = False,
) -> dict:
    ...
```

Returns a normalized response dict:

```python
{
    "text": str,           # assistant text content (empty string if tool call only)
    "tool_calls": list,    # list of tool call dicts (empty list if text only)
    "finish_reason": str,  # "stop" | "tool_calls" | "length" | "error"
    "raw": object,         # raw LiteLLM ModelResponse for debugging
}
```

The wrapper extracts these fields from LiteLLM's `ModelResponse`; the agent loop never inspects the raw response directly.

## Supported providers (no extra code required)
- Ollama (local)
- Anthropic
- OpenAI
- Groq

Additional LiteLLM-supported providers (Azure, Cohere, etc.) work automatically via the same model string convention.

## config.py

Loads the two required keys plus any optional overrides:

```python
def load_config() -> dict:
    """Return config dict with at least agent_model and executor_model."""
    ...
```

Credentials (API keys) are read from environment variables as LiteLLM expects (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.). They are never stored in config files.

## Done criteria
- Switching `agent_model` string in config routes to a different provider with no code change
- `executor_model` is independently configurable from `agent_model`
- `generate()` produces the normalized response shape for all supported providers
- Streaming path returns tokens incrementally
