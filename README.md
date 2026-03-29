# Group 6 — CLI Coding Assistant

Senior design project. Takes natural language instructions from a developer, reasons about a local codebase, and autonomously reads, edits, and executes code to complete tasks — similar to Claude Code, Codex, and OpenCode.

---

## What it does

- **Debug mode (ReAct loop):** the agent calls tools one at a time, shows you what it's doing, and asks for confirmation before any write-class tool runs.
- **Build mode (plan-and-execute):** the agent breaks the task into parallel steps, fans them out, and synthesizes results.
- **RAG search:** the agent can search ingested documentation via `search_docs` — backed by ChromaDB + sentence-transformers.
- **Slash commands:** `/mode debug`, `/mode build`, `/help`, `/exit` — switchable mid-session.
- **Provider-agnostic:** swap between Ollama (local), Anthropic, OpenAI, OpenRouter, or Groq by changing a single flag — no code changes needed.
- **OpenRouter support:** access 100+ models (Claude, GPT-4o, Llama, Gemini) through a single free API key at [openrouter.ai](https://openrouter.ai).

---

## Prerequisites

| Tool | Min version | Install |
|---|---|---|
| Python | 3.13+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) — required for `npx` (MCP filesystem server) |
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

**Option A — uv (recommended):**

```bash
cd coding-assistant
uv sync
```

`uv sync` reads `pyproject.toml`, resolves the lockfile, and installs everything into `.venv` automatically.

**Option B — pip + requirements.txt:**

```bash
# From repo root
python -m venv coding-assistant/.venv
# Windows
coding-assistant\.venv\Scripts\activate
# macOS / Linux
source coding-assistant/.venv/bin/activate

pip install -r requirements.txt
```

`requirements.txt` lives at the repo root and is generated from `pyproject.toml`. It contains all pinned transitive dependencies.

Key packages installed either way: `langgraph`, `litellm`, `chromadb`, `sentence-transformers`, `mcp`.

### 3. Pull a local model (Ollama only)

If you plan to use a local model:

```bash
ollama pull llama3.2
```

Make sure Ollama is running (`ollama serve`) before starting the assistant.

### 4. Create a `.env` file

The assistant loads API keys and MCP server config from a `.env` file in the **repo root** (`Group-6-CLI-Coding-Assistant/.env`). Create it now:

```bash
# From repo root
cp .env.example .env   # if an example exists, otherwise create it manually
```

Minimal `.env` — fill in whichever keys you have:

```dotenv
# --- Cloud provider keys (add whichever you use) ---
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
OPENROUTER_API_KEY=sk-or-...

# --- Tavily web search (optional — get a free key at tavily.com) ---
TAVILY_API_KEY=tvly-...

# --- MCP filesystem server (lets the agent read/write repo files) ---
ASSISTANT_FILESYSTEM_MCP_COMMAND=npx
ASSISTANT_FILESYSTEM_MCP_ARGS=-y @modelcontextprotocol/server-filesystem /absolute/path/to/Group-6-CLI-Coding-Assistant

# --- MCP Tavily web search server ---
ASSISTANT_EXTERNAL_MCP_COMMAND=npx
ASSISTANT_EXTERNAL_MCP_ARGS=-y tavily-mcp

# --- MCP RAG server (searches ingested project docs) ---
ASSISTANT_RAG_MCP_COMMAND=/absolute/path/to/Group-6-CLI-Coding-Assistant/coding-assistant/.venv/Scripts/python.exe
ASSISTANT_RAG_MCP_ARGS=-m rag_server.server
```

Replace paths in `ASSISTANT_FILESYSTEM_MCP_ARGS` and `ASSISTANT_RAG_MCP_COMMAND` with the absolute path to the repo root on your machine. On macOS/Linux the RAG command is `.venv/bin/python` instead of `.venv/Scripts/python.exe`.

The assistant reads this file automatically on startup — no `export` or shell sourcing needed.

**No API key yet?** Run the assistant with no flags and it will prompt you interactively:

```
No model configured. Options:
  1. Use local Ollama (requires ollama running)
  2. Enter OpenRouter API key (get one free at openrouter.ai)
Choice (1/2):
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

All commands run from inside the `coding-assistant/` directory with the venv activated.

### Quick start

```bash
cd coding-assistant
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

axiom --provider openrouter \
  --agent-model openrouter/anthropic/claude-sonnet-4-6 \
  --executor-model openrouter/anthropic/claude-sonnet-4-6
```

On startup you'll see which MCP servers connected, then the banner:

```
◆ filesystem   connected
◆ tavily       connected
◆ rag          connected

┌─────────────────────────────────────────────────────────────────────────────┐
│                                    AXIOM                                    │
└──────────────────── autonomous coding assistant ────────────────────────────┘
  mode=debug | provider=openrouter | model=openrouter/anthropic/claude-sonnet-4-6
  type /help for commands

 >
```

Type any task in plain English, or a slash command. Press `Ctrl+C` or type `/exit` to quit.

### Local model (Ollama)

```bash
axiom --provider ollama \
  --agent-model ollama/llama3.2 \
  --executor-model ollama/llama3.2
```

### Anthropic (Claude)

```bash
axiom --provider anthropic \
  --agent-model anthropic/claude-sonnet-4-6 \
  --executor-model anthropic/claude-sonnet-4-6
```

### OpenAI

```bash
axiom --provider openai \
  --agent-model openai/gpt-4o \
  --executor-model openai/gpt-4o
```

### OpenRouter (recommended for new users)

OpenRouter gives you access to Claude, GPT-4o, Llama, Gemini, and others through one free API key. Get one at [openrouter.ai](https://openrouter.ai).

```bash
axiom --provider openrouter \
  --agent-model openrouter/anthropic/claude-sonnet-4-6 \
  --executor-model openrouter/anthropic/claude-sonnet-4-6 \
  --openrouter-key sk-or-...
```

To see all supported OpenRouter model strings:

```bash
axiom --list-models
```

Output:
```
Supported OpenRouter models:
  openrouter/anthropic/claude-sonnet-4-6
  openrouter/openai/gpt-4o
  openrouter/meta-llama/llama-3.1-70b-instruct
  openrouter/google/gemini-pro
```

### No flags (interactive setup)

Running with no `--agent-model` flag triggers an interactive setup prompt:

```bash
axiom
```

```
No model configured. Options:
  1. Use local Ollama (requires ollama running)
  2. Enter OpenRouter API key (get one free at openrouter.ai)
Choice (1/2):
```

### Auto-approval mode

Pass `--approval-mode auto` to skip confirmation prompts for write operations (useful for demos and scripted runs):

```bash
axiom --provider openrouter \
  --agent-model openrouter/anthropic/claude-sonnet-4-6 \
  --executor-model openrouter/anthropic/claude-sonnet-4-6 \
  --approval-mode auto
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
| `--openrouter-key` | `None` | OpenRouter API key (falls back to `OPENROUTER_API_KEY` env var) |
| `--list-models` | — | Print supported OpenRouter model strings and exit |

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
 > search the docs for how the agent loop works

  ◌ thinking...
⚡ search_docs  "how the agent loop works"
  ✓ done  (2,341 chars, 0.4s)

  ◌ thinking...
╭─ axiom ───────────────────────────────────────────────────────────────────╮
│ The agent loop is implemented as a LangGraph state machine with two        │
│ subgraphs: debug mode (ReAct) and build mode (plan-and-execute)...         │
╰────────────────────────────────────────────────────────────────────────────╯
● completed  2 iterations  5.1s

 > /mode build
Mode switched to build.

 > create a folder called output and write a summary.md file inside it

  ◌ thinking...
📁 create_directory   output/
📝 write_file         output/summary.md  (0.8kb)
╭─ axiom ───────────────────────────────────────────────────────────────────╮
│ Done! Created output/summary.md with a summary of the architecture.        │
╰────────────────────────────────────────────────────────────────────────────╯
● completed  2 iterations  8.3s

 > /exit
Goodbye!
```

---

## Demo script

Run this from a fresh folder to show all three MCP servers, two non-trivial tasks, and mode switching. Assumes venv is already activated.

```
mkdir C:\Users\%USERNAME%\Desktop\demo
cd C:\Users\%USERNAME%\Desktop\demo
```

```
axiom.bat --provider openrouter --agent-model openrouter/anthropic/claude-sonnet-4-6 --executor-model openrouter/anthropic/claude-sonnet-4-6 --approval-mode auto
```

Wait for all 3 servers + banner. Then at `>`:

**Task 1 — web search + file creation:**
```
search the web for Python best practices for error handling in a calculator, then create a folder called calculator_app and write a Python file called calculator.py inside it with add, subtract, multiply, and divide functions that implement those best practices
```

**Task 2 — RAG search + test generation:**
```
search the docs to understand how the agent loop works in this project, then read calculator_app/calculator.py and write a test file called test_calculator.py in the same folder that tests every function
```

**Switch to build mode:**
```
/mode build
```

**Task 3 — build mode summarization:**
```
read calculator_app/calculator.py and summarize what it does and what error handling patterns it uses
```

**Exit:**
```
/exit
```

---

## Project structure

```
Group-6-CLI-Coding-Assistant/
├── .env                         # API keys + MCP config (not committed)
├── requirements.txt             # Pinned flat list for pip install -r
├── SpecificationFiles/          # Architecture and module spec docs
├── coding-assistant/
│   ├── pyproject.toml           # Dependency declarations (uv / PEP 517)
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
RAG_DOCS_DIR=/path/to/my/docs axiom ...
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

**`ModuleNotFoundError` after `pip install -r requirements.txt`**
Your venv is probably not activated. Run `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux) first, then retry.

**`VIRTUAL_ENV does not match project environment` warning**
Safe to ignore — uv prints this when a system Python venv is active. uv always uses `.venv` inside `coding-assistant/`.

**Model returns JSON instead of plain text**
Known behavior with smaller local models (e.g. llama3.2) — the model ignores the plain-text instruction in the system prompt. Use a larger model or a cloud provider for better instruction-following.

**OpenRouter `401 Unauthorized`**
Your key is wrong or not set. Double-check with `echo $OPENROUTER_API_KEY` (or `$env:OPENROUTER_API_KEY` on PowerShell). You can also pass it directly with `--openrouter-key sk-or-...`.

**`--list-models` shows nothing / command not found**
Make sure you're inside `coding-assistant/` with the venv activated, then run `axiom --list-models`.
