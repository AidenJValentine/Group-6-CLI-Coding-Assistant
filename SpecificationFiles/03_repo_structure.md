# Recommended Repo Structure

```text
coding-assistant/
├── README.md
├── requirements.txt
├── .env.example
├── docs/
│   ├── architecture/
│   │   ├── system_architecture.md
│   │   ├── state_diagram.md
│   │   └── sequence_diagrams.md
│   ├── planning/
│   │   ├── project_scope.md
│   │   ├── task_split.md
│   │   └── milestones.md
│   └── reflection/
│       └── notes.md
├── src/
│   └── assistant/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── app.py
│       │   ├── renderer.py
│       │   └── prompts.py
│       ├── agent/
│       │   ├── __init__.py
│       │   ├── loop.py
│       │   ├── state.py
│       │   ├── planner.py
│       │   └── message_builder.py
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── ollama_provider.py
│       │   └── openai_provider.py
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── registry.py
│       │   ├── executor.py
│       │   └── approval.py
│       ├── mcp/
│       │   ├── __init__.py
│       │   ├── client.py
│       │   ├── server_config.py
│       │   └── adapters.py
│       └── models/
│           ├── __init__.py
│           └── schemas.py
├── rag_server/
│   ├── README.md
│   ├── server.py
│   ├── ingest.py
│   ├── retrieval.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── vectordb.py
│   ├── config.py
│   └── data/
│       ├── raw/
│       └── chroma/
├── tests/
│   ├── test_agent_loop.py
│   ├── test_providers.py
│   ├── test_mcp_client.py
│   └── test_rag_retrieval.py
└── scripts/
    ├── run_assistant.sh
    └── build_rag_index.sh
```

## Notes
- Keep the RAG server as a separable unit so the architecture is easy to explain.
- Put planning docs into the repo before implementation to satisfy rubric expectations.
- Keep provider code isolated so switching models is demonstrably clean.
