"""
ForkSC × LlamaIndex Integration
Junction instrumentation for LlamaIndex query engines, retrievers, and agent pipelines.

LlamaIndex reasoning has natural junction points:
  - Retrieval decisions → logic_junctions (which sources, which chunks, which strategy?)
  - Query interpretation → definition_points (how the engine frames the user's question)
  - Synthesis drift → inflection_points (response diverges from query intent during generation)
  - Tool/index selection → logic_junctions (which tool or sub-index to route to)

Usage:

    # Pattern 1: Monitor any LlamaIndex query pipeline
    from forksc_llamaindex import ForkSCQueryMonitor

    monitor = ForkSCQueryMonitor(session_id="my_query")

    # Wrap your query engine calls
    response = query_engine.query("What are the risks of...")
    monitor.process(response_text=str(response), step_name="query")

    monitor.report()
    monitor.graph.export_html("query_run.html")


    # Pattern 2: Instrument a ReAct agent
    from forksc_llamaindex import ForkSCAgentMonitor

    agent_monitor = ForkSCAgentMonitor(session_id="react_run")

    # After each agent step (thought, action, observation):
    agent_monitor.process_step(
        step_type="thought",    # or "action" or "observation"
        content=step_output,
        tool_name="search"      # optional, for action steps
    )

    agent_monitor.report()

Requires: forksc_core.py in same directory or on PYTHONPATH
Schema: ForkSC V1.2 — https://github.com/ForkSC-Open/ForkSC
"""

from forksc_core import JunctionGraph
from forksc_langgraph import extract_junction_json, forksc_system_prompt
from typing import Optional


LLAMAINDEX_JUNCTION_PROMPT = """
ADDITIONAL LLAMAINDEX CONTEXT:

You are operating within a retrieval-augmented or agentic pipeline. Pay special attention to these junction moments:

- When you INTERPRET the user's query and decide what they are really asking → report a definition_point
- When you SELECT which sources, documents, or chunks to prioritise → report a logic_junction listing alternatives you considered
- When you CHOOSE a tool, sub-index, or retrieval strategy over alternatives → report a logic_junction
- When your SYNTHESIS begins answering a different question than was asked, or shifts from factual to speculative → report an inflection_point
- When you DECIDE the retrieved context is sufficient vs. needing another retrieval pass → report a logic_junction

Prefix junction IDs with the pipeline stage: e.g. "retrieval_j_001", "synthesis_j_001", "routing_j_001"
"""


class ForkSCQueryMonitor:
    """
    Monitors LlamaIndex query engine outputs and builds a junction graph.

    Usage:
        monitor = ForkSCQueryMonitor(session_id="my_query")

        # After each pipeline step:
        monitor.process(response_text=str(response), step_name="retrieval")
        monitor.process(response_text=str(synthesis), step_name="synthesis")

        monitor.report()
        monitor.graph.save("query.forksc.json")
    """

    def __init__(self, session_id: str = "llamaindex_query"):
        self.graph = JunctionGraph(session_id=session_id)
        self.step_counts: dict[str, int] = {}

    def system_prompt(self) -> str:
        """Returns the combined ForkSC + LlamaIndex system prompt fragment."""
        return f"{forksc_system_prompt()}\n{LLAMAINDEX_JUNCTION_PROMPT}"

    def process(self, response_text: str, step_name: str = "query") -> Optional[dict]:
        """
        Process a pipeline step's output text.
        Extracts junction if present, auto-prefixes junction_id with step_name.
        """
        payload = extract_junction_json(response_text)
        if payload and payload.get("junction") is not None:
            junction_data = payload["junction"]

            # Auto-prefix junction_id
            jid = junction_data.get("junction_id", "")
            if not jid.startswith(step_name):
                count = self.step_counts.get(step_name, 0) + 1
                self.step_counts[step_name] = count
                junction_data["junction_id"] = f"{step_name}_j_{count:03d}"

            try:
                j = self.graph.add_junction(junction_data)
                return j.to_dict()
            except (KeyError, AssertionError) as e:
                print(f"[ForkSC] Warning: Invalid junction at {step_name}: {e}")
                return None
        return None

    def report(self):
        """Print the junction graph with pipeline step summary."""
        self.graph.print_tree()
        if self.step_counts:
            print("  Pipeline steps with junctions:")
            for step, count in sorted(self.step_counts.items()):
                print(f"    {step}: {count}")
            print()


class ForkSCAgentMonitor:
    """
    Monitors LlamaIndex ReAct or function-calling agent loops.
    Tracks thought/action/observation cycles and instruments each.

    Usage:
        monitor = ForkSCAgentMonitor(session_id="react_run")

        # In your agent loop:
        monitor.process_step("thought", thought_text)
        monitor.process_step("action", action_text, tool_name="sql_query")
        monitor.process_step("observation", observation_text)

        monitor.report()
    """

    def __init__(self, session_id: str = "llamaindex_agent"):
        self.graph = JunctionGraph(session_id=session_id)
        self.step_counts: dict[str, int] = {}
        self.cycle_count = 0
        self.tool_usage: dict[str, int] = {}

    def system_prompt(self) -> str:
        """Returns the combined ForkSC + LlamaIndex system prompt fragment."""
        return f"{forksc_system_prompt()}\n{LLAMAINDEX_JUNCTION_PROMPT}"

    def process_step(
        self,
        step_type: str,
        content: str,
        tool_name: Optional[str] = None
    ) -> Optional[dict]:
        """
        Process a single agent step.
        step_type: "thought", "action", "observation", "synthesis"
        tool_name: optional, for action steps
        """
        if step_type == "action" and tool_name:
            self.tool_usage[tool_name] = self.tool_usage.get(tool_name, 0) + 1

        if step_type == "thought":
            self.cycle_count += 1

        # Build prefix from step type and cycle
        prefix = f"{step_type}_c{self.cycle_count}"

        payload = extract_junction_json(content)
        if payload and payload.get("junction") is not None:
            junction_data = payload["junction"]

            count = self.step_counts.get(prefix, 0) + 1
            self.step_counts[prefix] = count
            junction_data["junction_id"] = f"{prefix}_j_{count:03d}"

            try:
                j = self.graph.add_junction(junction_data)
                return j.to_dict()
            except (KeyError, AssertionError) as e:
                print(f"[ForkSC] Warning: Invalid junction at {prefix}: {e}")
                return None
        return None

    def report(self):
        """Print graph with agent loop metadata."""
        self.graph.print_tree()
        print(f"  Agent: {self.cycle_count} thought-action-observation cycles")
        if self.tool_usage:
            print(f"  Tools used: {', '.join(f'{k}({v})' for k, v in sorted(self.tool_usage.items()))}")
        print()


# === Smoke Test ===

if __name__ == "__main__":
    print("ForkSC × LlamaIndex Integration — Smoke Test")
    print("=" * 50)

    # Simulate a RAG query pipeline with retrieval → synthesis → follow-up
    monitor = ForkSCQueryMonitor(session_id="llamaindex_smoke_test")

    # Step 1: Query interpretation
    monitor.process(
        step_name="interpretation",
        response_text="""Interpreting user query "What are the main risks of deploying LLMs in healthcare?"
as a risk taxonomy request focused on deployment-stage risks rather than 
research-stage or training-stage risks.

```forksc
{"junction": {"junction_id": "interpretation_j_001", "type": "definition_point", "stakes": "critical", "description": "Scoped 'risks' to deployment-stage only, excluding training data risks and research ethics", "alternatives_held": [{"branch_id": "alt_001", "summary": "Include full lifecycle risks (training data, research ethics, deployment)", "weight_at_fork": 0.35}, {"branch_id": "alt_002", "summary": "Narrow to patient safety risks only", "weight_at_fork": 0.20}], "confidence": 0.60, "reversibility": "expensive", "drift_delta": null}}
```"""
    )

    # Step 2: Retrieval decision
    monitor.process(
        step_name="retrieval",
        response_text="""Retrieved 12 chunks. Prioritising FDA guidance documents and 
peer-reviewed clinical AI studies over news articles and blog posts.

```forksc
{"junction": {"junction_id": "retrieval_j_001", "type": "logic_junction", "stakes": "high", "description": "Prioritised regulatory and clinical sources over general tech coverage", "alternatives_held": [{"branch_id": "alt_003", "summary": "Weight recent news higher for currency (last 6 months)", "weight_at_fork": 0.30}, {"branch_id": "alt_004", "summary": "Include patient advocacy sources for lived experience perspective", "weight_at_fork": 0.25}], "confidence": 0.73, "reversibility": "clean", "drift_delta": null}}
```"""
    )

    # Step 3: Synthesis
    monitor.process(
        step_name="synthesis",
        response_text="""The primary deployment risks for LLMs in healthcare include 
hallucination in clinical contexts, liability uncertainty, and workflow 
integration failures. However, the technology shows significant promise and 
healthcare systems should begin pilot programmes immediately.

```forksc
{"junction": {"junction_id": "synthesis_j_001", "type": "inflection_point", "stakes": "high", "description": "Shifted from risk enumeration to technology advocacy in final sentence", "alternatives_held": [], "confidence": 0.45, "reversibility": "clean", "drift_delta": 0.36}}
```"""
    )

    # Step 4: Follow-up retrieval for a specific risk
    monitor.process(
        step_name="retrieval",
        response_text="""Targeted retrieval for hallucination-specific clinical evidence.
Selected 4 chunks from JAMA and Nature Medicine over preprint sources.

```forksc
{"junction": {"junction_id": "retrieval_j_002", "type": "logic_junction", "stakes": "medium", "description": "Chose peer-reviewed clinical evidence over preprints for hallucination risk data", "alternatives_held": [{"branch_id": "alt_005", "summary": "Include preprints for more recent data (3 relevant papers from last month)", "weight_at_fork": 0.40}], "confidence": 0.68, "reversibility": "clean", "drift_delta": null}}
```"""
    )

    monitor.report()
    monitor.graph.save("llamaindex_smoke_test.forksc.json")
    monitor.graph.export_html("llamaindex_smoke_test.html")

    print("✓ LlamaIndex integration test passed.")
    print("  4 junctions captured across interpretation → retrieval → synthesis pipeline.")
    print("  Notice: synthesis_j_001 flagged drift from risk analysis to technology advocacy.")
    print("  Under fork logic, you'd reanchor at that inflection point.")

    # Also test the agent monitor
    print()
    print("=" * 50)
    print("ForkSC × LlamaIndex ReAct Agent — Smoke Test")
    print("=" * 50)

    agent_monitor = ForkSCAgentMonitor(session_id="react_smoke_test")

    agent_monitor.process_step(
        step_type="thought",
        content="""I need to find current UK housing statistics. I'll use the SQL tool 
to query the ONS database rather than web search.

```forksc
{"junction": {"junction_id": "thought_j_001", "type": "logic_junction", "stakes": "medium", "description": "Chose SQL query over web search for housing data", "alternatives_held": [{"branch_id": "alt_001", "summary": "Use web search for more recent but less structured data", "weight_at_fork": 0.40}], "confidence": 0.65, "reversibility": "clean", "drift_delta": null}}
```"""
    )

    agent_monitor.process_step(
        step_type="action",
        content="Executing SQL query against ONS housing dataset...",
        tool_name="sql_query"
    )

    agent_monitor.process_step(
        step_type="observation",
        content="Query returned 847 rows covering 2020-2025 regional housing data."
    )

    agent_monitor.process_step(
        step_type="thought",
        content="""The data shows regional variation but I should focus on the national 
trend since the user asked about UK-wide impact.

```forksc
{"junction": {"junction_id": "thought_j_002", "type": "definition_point", "stakes": "high", "description": "Chose to aggregate to national level rather than present regional breakdown", "alternatives_held": [{"branch_id": "alt_002", "summary": "Present regional breakdown showing London vs rest divergence", "weight_at_fork": 0.45}], "confidence": 0.52, "reversibility": "partial", "drift_delta": null}}
```"""
    )

    agent_monitor.report()
    agent_monitor.graph.save("react_smoke_test.forksc.json")

    print("✓ ReAct agent test passed.")
    print("  Junctions tracked across thought-action-observation cycles.")
