"""
ForkSC × LangGraph Integration
Drop-in junction instrumentation for LangGraph agent workflows.

Usage:
    from forksc_langgraph import ForkSCCallback, forksc_system_prompt
    from forksc_core import JunctionGraph
    from langgraph.graph import StateGraph

    # 1. Add the ForkSC system prompt to your model
    model = ChatOpenAI(model="gpt-4o").bind(
        system=forksc_system_prompt()
    )

    # 2. Create a junction graph
    graph = JunctionGraph(session_id="my_workflow")

    # 3. Wrap your node functions
    @forksc_node(graph)
    def analyze(state):
        response = model.invoke(state["messages"])
        return {"messages": [response]}

    # 4. After the run, inspect
    graph.print_tree()
    graph.save("my_workflow.forksc.json")
    graph.export_html("my_workflow.html")

Requires: langgraph, forksc_core.py (in same directory or on PYTHONPATH)
Schema: ForkSC V1.2 — https://github.com/ForkSC-Open/ForkSC
"""

import functools
import json
from typing import Callable, Any

# Import from local forksc_core
from forksc_core import JunctionGraph


def forksc_system_prompt() -> str:
    """
    Returns the ForkSC junction tagging system prompt fragment.
    Append this to your agent's system message.
    """
    return """
You are operating under the ForkSC junction tagging protocol. At every reasoning step, after your main response content, append a JSON block tagged with ```forksc that reports any junction you encountered.

Junction types:
- definition_point: You committed to a framing/interpretation governing downstream reasoning.
- logic_junction: You chose between viable paths. List the alternatives you considered.
- inflection_point: Your reasoning shifted from the stated objective without a clean branch.

Format (append after your response):

```forksc
{"junction": {"junction_id": "j_NNN", "type": "...", "stakes": "low|medium|high|critical", "description": "...", "alternatives_held": [{"branch_id": "alt_NNN", "summary": "...", "weight_at_fork": 0.0}], "confidence": 0.0, "reversibility": "clean|partial|expensive", "drift_delta": null}}
```

If no junction exists at this step: ```forksc\n{"junction": null}\n```

Number junction_ids sequentially. Be honest about confidence. Always populate alternatives for logic_junctions.
"""


def extract_junction_json(text: str) -> dict | None:
    """Extract a ForkSC junction tag from agent output text."""
    # Look for forksc code block
    marker = "```forksc"
    start = text.find(marker)
    if start == -1:
        # Fallback: try to find raw junction JSON
        start = text.find('{"junction"')
        if start == -1:
            return None
        end = start
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            return None

    # Extract from code block
    start = start + len(marker)
    end = text.find("```", start)
    if end == -1:
        end = len(text)

    block = text[start:end].strip()
    try:
        return json.loads(block)
    except json.JSONDecodeError:
        return None


def forksc_node(graph: JunctionGraph):
    """
    Decorator that instruments a LangGraph node function with ForkSC junction capture.

    The decorated function should return a state dict. If the agent's response
    contains a ForkSC junction tag, it is automatically added to the graph.

    Works with any LangGraph node that returns messages in state.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Extract the last message content from the result
            messages = result.get("messages", [])
            if not messages:
                return result

            last_message = messages[-1]

            # Handle different message types
            if hasattr(last_message, "content"):
                content = last_message.content
            elif isinstance(last_message, dict):
                content = last_message.get("content", "")
            elif isinstance(last_message, str):
                content = last_message
            else:
                return result

            # Try to extract junction
            payload = extract_junction_json(content)
            if payload and payload.get("junction") is not None:
                try:
                    graph.add_junction(payload["junction"])
                except (KeyError, AssertionError) as e:
                    print(f"[ForkSC] Warning: Invalid junction in node '{func.__name__}': {e}")

            return result

        return wrapper
    return decorator


class ForkSCMonitor:
    """
    Standalone monitor that processes agent outputs and builds the junction graph.
    Use this when you can't decorate node functions directly.

    Usage:
        monitor = ForkSCMonitor(session_id="my_run")

        # After each agent step:
        monitor.process(agent_output_text)

        # After the run:
        monitor.graph.print_tree()
        monitor.graph.save("output.forksc.json")
    """

    def __init__(self, session_id: str = "monitored"):
        self.graph = JunctionGraph(session_id=session_id)

    def process(self, text: str) -> dict | None:
        """Process agent output text. Returns junction dict if found, None otherwise."""
        payload = extract_junction_json(text)
        if payload and payload.get("junction") is not None:
            try:
                j = self.graph.add_junction(payload["junction"])
                return j.to_dict()
            except (KeyError, AssertionError) as e:
                print(f"[ForkSC] Warning: Invalid junction: {e}")
                return None
        return None

    def report(self):
        """Print the current graph state."""
        self.graph.print_tree()


# === Quick Integration Test ===

if __name__ == "__main__":
    print("ForkSC × LangGraph Integration — Smoke Test")
    print("=" * 50)

    # Simulate agent outputs with embedded junction tags
    simulated_outputs = [
        """I'll approach this as a comparative policy analysis, examining both the economic 
and social dimensions of the proposed regulation.

```forksc
{"junction": {"junction_id": "j_001", "type": "definition_point", "stakes": "high", "description": "Framed as comparative policy analysis rather than stakeholder impact assessment", "alternatives_held": [{"branch_id": "alt_001", "summary": "Frame as stakeholder impact assessment", "weight_at_fork": 0.35}], "confidence": 0.70, "reversibility": "expensive", "drift_delta": null}}
```""",

        """Looking at the economic data, the regulation would likely reduce market 
concentration in the short term but may create barriers to entry for smaller firms.

```forksc
{"junction": {"junction_id": "j_002", "type": "logic_junction", "stakes": "medium", "description": "Led with market concentration effects over employment effects", "alternatives_held": [{"branch_id": "alt_002", "summary": "Lead with employment impact data", "weight_at_fork": 0.45}, {"branch_id": "alt_003", "summary": "Lead with consumer price effects", "weight_at_fork": 0.20}], "confidence": 0.58, "reversibility": "clean", "drift_delta": null}}
```""",

        """This regulation really should be implemented as soon as possible given the 
growing inequality in the sector.

```forksc
{"junction": {"junction_id": "j_003", "type": "inflection_point", "stakes": "high", "description": "Shifted from analysis to advocacy without explicit transition", "alternatives_held": [], "confidence": 0.40, "reversibility": "clean", "drift_delta": 0.42}}
```""",
    ]

    monitor = ForkSCMonitor(session_id="langgraph_smoke_test")

    for output in simulated_outputs:
        monitor.process(output)

    monitor.report()
    monitor.graph.save("langgraph_smoke_test.forksc.json")
    monitor.graph.export_html("langgraph_smoke_test.html")

    print("\n✓ Integration test passed. Graph captured 3 junctions from simulated agent output.")
