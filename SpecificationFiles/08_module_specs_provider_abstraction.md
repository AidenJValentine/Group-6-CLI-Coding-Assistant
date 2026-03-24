# Module Spec: Provider Abstraction

## Goal
Create a model-agnostic provider interface supporting Ollama and one cloud provider.

## Files
- `src/assistant/providers/base.py`
- `src/assistant/providers/ollama_provider.py`
- `src/assistant/providers/openai_provider.py`
- optional: `src/assistant/config.py`

## Functional requirements
1. Define a common provider interface
2. Support:
   - send messages
   - receive text
   - optional streaming
   - tool-capable completion format
3. Implement at least:
   - Ollama provider
   - one cloud provider

## Recommended base interface
```python
class BaseProvider(ABC):
    def generate(self, messages, tools=None, stream=False):
        ...
```

## Normalized response shape
Return a consistent structure such as:
- `text`
- `tool_calls`
- `finish_reason`
- `raw`

## Notes
- Normalize provider-specific schemas so the agent loop does not care which backend is active.
- Keep credentials/config outside the provider logic where possible.

## Done criteria
- same agent code can switch providers by config only
- both providers produce the same normalized response shape
