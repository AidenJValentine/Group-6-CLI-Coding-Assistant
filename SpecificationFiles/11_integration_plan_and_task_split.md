# Integration Plan and Suggested Task Split

## Milestone 1: Planning and repo setup
Owner: architecture lead

Deliverables:
- repo created
- planning docs committed
- folder structure created
- issue/task list created

## Milestone 2: Skeleton app running
Owners:
- CLI lead
- agent loop lead
- provider lead

Deliverables:
- REPL starts
- mocked provider response displays
- mocked tool-call event renders

## Milestone 3: MCP integration
Owners:
- MCP lead
- filesystem/external server lead

Deliverables:
- connect required servers
- tools dynamically listed
- at least one tool from each required server invoked

## Milestone 4: Custom RAG server
Owner: RAG lead

Deliverables:
- docs ingested
- Chroma persisted
- docs_search MCP tool callable
- Fusion Retrieval demonstrated

## Milestone 5: Full integration and demo
Owners:
- integration/testing lead
- polish/UX/demo lead

Deliverables:
- end-to-end tasks working
- demo script written
- reflection notes started

## Suggested work split for 4 people

### Person 1
Architecture, repo setup, diagrams, integration oversight

### Person 2
CLI + renderer + approval flow

### Person 3
Provider abstraction + agent loop

### Person 4
MCP client + external/filesystem servers

RAG can be handled by Person 3 or 4 depending on strengths, or shared.

## Suggested work split for 5 people

### Person 1
Architecture, diagrams, integration oversight

### Person 2
CLI + UX + demo flow

### Person 3
Provider abstraction + agent loop

### Person 4
MCP client + filesystem + external server

### Person 5
Custom RAG server + indexing + retrieval evaluation

## Vacation-friendly handoff rule
The architecture lead should step back after:
- docs are committed
- repo structure exists
- skeleton is agreed upon
- owners are assigned
