# Group 6 — CLI Coding Assistant

Senior design project. Takes natural language instructions from a developer, reasons about a local codebase, and autonomously reads, edits, and executes code to complete tasks — similar to Claude Code, Codex, and OpenCode.

---

## What it does

- **Debug mode (ReAct loop):** the agent calls tools one at a time, shows you what it's doing, and asks for confirmation before any write-class tool runs.
- **Build mode (plan-and-execute):** the agent breaks the task into parallel steps, fans them out, and synthesizes results.
- **RAG search:** the agent can search ingested documentation via `search_docs` — backed by ChromaDB + sentence-transformers.
- **Slash commands:** `/mode debug`, `/mode build`, `/help`, `/exit` — switchable mid-session.
- **Provider-agnostic:** swap between Ollama (local), Anthropic, OpenAI, or Groq by changing a single flag — no code changes needed.

---

## Prerequisites

| Tool | Min version | Install |
|---|---|---|
| Python | 3.13+ | [python.org](https://python.org) |
| uv | latest | `pip install uv` or [docs.astral.sh/uv](https://docs.astral.sh/uv) |
| Ollama | latest | [ollama.com](https://ollama.com) — only needed for local models |
| Git | any | [git-scm.com](https://git-scm.com) |

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/<your-org>/Group-6-CLI-Coding-Assistant.git
cd Group-6-CLI-Coding-Assistant
```

### 2. Install dependencies

```bash
cd coding-assistant
uv sync
```

`uv sync` reads `pyproject.toml` and installs everything into a local `.venv`. No manual pip needed.

Installed packages: `langgraph`, `litellm`, `chromadb`, `sentence-transformers`.

### 3. Pull a local model (Ollama only)

If you plan to use a local model:

```bash
ollama pull llama3.2
```

Make sure Ollama is running (`ollama serve`) before starting the assistant.

### 4. Set API keys (cloud providers only)

Skip this if you're only using Ollama.

```bash
# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# OpenAI
export OPENAI_API_KEY=sk-...

# Groq
export GROQ_API_KEY=gsk_...
```

On Windows (PowerShell):
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

### 5. Build the RAG index

The RAG server needs source documents to index. The spec files are already suitable:

```bash
# From repo root
mkdir -p coding-assistant/rag_server/data/raw
cp SpecificationFiles/*.md coding-assistant/rag_server/data/raw/

# Build the index (runs once; reused on subsequent starts)
cd coding-assistant
uv run python -c "
import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'src')
from rag_server.ingest import build_index
result = build_index(force_rebuild=True)
print(result)
"
```

Expected output:
```
{'status': 'built', 'file_count': 13, 'chunk_count': 45, ...}
```

To use your own docs instead, drop `.md` or `.txt` files into `coding-assistant/rag_server/data/raw/` and re-run with `force_rebuild=True`.

---

## Running the assistant

All commands run from inside the `coding-assistant/` directory.

### Local model (Ollama)

```bash
uv run python src/assistant/main.py \
  --provider ollama \
  --agent-model ollama/llama3.2 \
  --executor-model ollama/llama3.2 \
  --mode debug
```

### Anthropic (Claude)

```bash
uv run python src/assistant/main.py \
  --provider anthropic \
  --agent-model anthropic/claude-sonnet-4-6 \
  --executor-model anthropic/claude-sonnet-4-6 \
  --mode debug
```

### OpenAI

```bash
uv run python src/assistant/main.py \
  --provider openai \
  --agent-model openai/gpt-4o \
  --executor-model openai/gpt-4o \
  --mode debug
```

### All flags

| Flag | Default | Description |
|---|---|---|
| `--provider` | `mock` | Label for display only; model string drives actual routing |
| `--agent-model` | `mock-agent` | LiteLLM model string for the reasoning agent |
| `--executor-model` | `mock-executor` | LiteLLM model string for build-mode parallel steps |
| `--mode` | `debug` | Starting execution mode: `debug` or `build` |
| `--approval-mode` | `confirm` | `confirm` = prompt before write tools; `auto` = skip prompts |
| `--max-iterations` | `10` | Max ReAct loop iterations before stopping |

---

## Slash commands

Once the REPL is running:

| Command | Effect |
|---|---|
| `/mode debug` | Switch to ReAct (tool-by-tool) mode |
| `/mode build` | Switch to plan-and-execute mode |
| `/help` | List available commands |
| `/exit` | Quit |

Type `exit` or `quit` (without `/`) to also quit.

---

## Example session

```
[debug] > search the docs for how the agent loop works
[tool]
  name: search_docs
  args: {'query': 'agent loop'}
  result: {'query': 'agent loop', 'results': [...]}
assistant> The agent loop is implemented as a LangGraph state machine ...
[status] completed

[debug] > /mode build
Mode switched to build.

[build] > read all the spec files and summarize the architecture
...
```

---

## Project structure

```
Group-6-CLI-Coding-Assistant/
├── SpecificationFiles/          # Architecture and module spec docs
├── coding-assistant/
│   ├── pyproject.toml           # Dependencies (uv)
│   ├── rag_server/              # RAG pipeline
│   │   ├── server.py            # docs_search() entry point
│   │   ├── ingest.py            # Index builder
│   │   ├── retrieval.py         # Query + fusion retrieval
│   │   ├── config.py            # RAGConfig, paths, model names
│   │   └── data/
│   │       ├── raw/             # Drop source docs here
│   │       └── chroma/          # ChromaDB persisted index
│   └── src/assistant/
│       ├── main.py              # CLI entry point (argparse)
│       ├── config.py            # RuntimeConfig + load_provider_config()
│       ├── agent/
│       │   ├── loop.py          # LangGraph graph, all nodes, run_agent()
│       │   ├── state.py         # AgentState TypedDict + make_initial_state()
│       │   └── planner.py       # Build-mode plan generator
│       ├── providers/
│       │   └── litellm_client.py  # call_llm() wrapper over LiteLLM
│       ├── tools/
│       │   ├── registry.py      # TOOL_REGISTRY + load_rag_tool()
│       │   └── executor.py      # invoke_tool()
│       ├── mcp/
│       │   └── mock_client.py   # MockMCPClient (fallback for unregistered tools)
│       └── cli/
│           ├── app.py           # run_cli() REPL loop
│           └── renderer.py      # render_banner, render_result, etc.
```

---

## Adding your own documents to the RAG index

1. Drop `.md` or `.txt` files into `coding-assistant/rag_server/data/raw/`
2. Rebuild the index:
   ```bash
   cd coding-assistant
   uv run python -c "
   import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'src')
   from rag_server.ingest import build_index
   build_index(force_rebuild=True)
   "
   ```
3. The next `docs_search` call will use the new index.

To point the RAG server at a different directory entirely, set `RAG_DOCS_DIR` before running:
```bash
RAG_DOCS_DIR=/path/to/my/docs uv run python src/assistant/main.py ...
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'sentence_transformers'`**
```bash
cd coding-assistant && uv add sentence-transformers
```

**`ModuleNotFoundError: No module named 'chromadb'`**
```bash
cd coding-assistant && uv add chromadb
```

**`No documentation files found in .../data/raw`**
The raw docs directory is empty. Run step 5 of setup above.

**Ollama connection refused**
Make sure Ollama is running: `ollama serve`

**`VIRTUAL_ENV does not match project environment` warning**
Safe to ignore — uv prints this when a system Python venv is active. uv always uses `.venv` inside `coding-assistant/`.

**Model returns JSON instead of plain text**
Known behavior with smaller local models (e.g. llama3.2) — the model ignores the plain-text instruction in the system prompt. Use a larger model or a cloud provider for better instruction-following.
