# ForkSC Integrations

**Working code. Import and run.**

These integrations add ForkSC junction instrumentation to your existing agent workflows. No new infrastructure required. No API keys needed for the offline demo.

## Quick Start

```bash
python forksc_quickstart.py
```

See a five-junction reasoning graph in your terminal in 60 seconds. Open `offline_demo.html` for the interactive browser visualisation.

## Files

| File | What It Does |
|---|---|
| `forksc_core.py` | Zero-dependency junction graph engine. Parses junction tags, builds the reasoning DAG, exports terminal + HTML visualisation. This is the foundation — everything else imports from here. |
| `forksc_prompt.py` | System prompt fragment that teaches any LLM the junction taxonomy and structured output format. Copy-paste into your agent's system prompt. |
| `forksc_langgraph.py` | LangGraph integration. `@forksc_node` decorator for node-level instrumentation. `ForkSCMonitor` for framework-agnostic processing. |
| `forksc_autogen.py` | AutoGen integration. Multi-agent junction tracking with per-agent prefixed IDs. `ForkSCGroupChatMonitor` for cross-agent drift detection. |
| `forksc_llamaindex.py` | LlamaIndex integration. `ForkSCQueryMonitor` for RAG pipelines. `ForkSCAgentMonitor` for ReAct agent loops with tool-call tracking. |
| `forksc_quickstart.py` | Offline demo + copy-paste examples for OpenAI and Anthropic APIs. Start here. |

## How It Works

All integrations follow the same pattern:

1. **Prompt**: Add the junction taxonomy to your agent's system prompt (see `forksc_prompt.py`)
2. **Parse**: After each agent response, pass the output through the monitor — it extracts junction tags from the structured output
3. **Graph**: The monitor builds the reasoning DAG in real time — inspect it, export it, navigate it

Junction self-reporting via structured output is Phase 1 instrumentation. It is an imperfect but immediately useful signal. See Appendix B of the specification for the full instrumentation roadmap.

## Requirements

- Python 3.8+
- No external dependencies for offline demo
- OpenAI or Anthropic API key for live examples (optional)

## Schema

All integrations emit junction tags conforming to `/schemas/junction_tag.schema.json`. The schema is the contract — any tool that reads the schema can consume the output of any integration.
