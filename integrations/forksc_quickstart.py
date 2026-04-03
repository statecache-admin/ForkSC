"""
ForkSC Quickstart — OpenAI & Anthropic
Copy, paste, run. See your agent's reasoning graph in 60 seconds.

Requires:
  pip install openai        (for OpenAI example)
  pip install anthropic     (for Anthropic example)
  forksc_core.py in same directory

Schema: ForkSC V1.2 — https://github.com/ForkSC-Open/ForkSC
"""

# ============================================================
# EXAMPLE 1: OpenAI
# ============================================================

OPENAI_EXAMPLE = '''
import os
from openai import OpenAI
from forksc_core import JunctionGraph
from forksc_langgraph import forksc_system_prompt, ForkSCMonitor

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
monitor = ForkSCMonitor(session_id="openai_demo")

messages = [
    {"role": "system", "content": f"""You are a senior policy analyst.
{forksc_system_prompt()}"""},
    {"role": "user", "content": "Analyse the impact of a four-day work week policy on the UK economy. Consider multiple angles."}
]

# Multi-step agent loop
for step in range(3):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    content = response.choices[0].message.content
    monitor.process(content)
    messages.append({"role": "assistant", "content": content})

    if step < 2:
        messages.append({"role": "user", "content": "Continue your analysis. Consider the next dimension."})

# See the graph
monitor.report()
monitor.graph.save("openai_demo.forksc.json")
monitor.graph.export_html("openai_demo.html")
print("\\nOpen openai_demo.html in your browser to see the interactive graph.")
'''


# ============================================================
# EXAMPLE 2: Anthropic
# ============================================================

ANTHROPIC_EXAMPLE = '''
import os
import anthropic
from forksc_core import JunctionGraph
from forksc_langgraph import forksc_system_prompt, ForkSCMonitor

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
monitor = ForkSCMonitor(session_id="anthropic_demo")

system_prompt = f"""You are a senior policy analyst.
{forksc_system_prompt()}"""

messages = [
    {"role": "user", "content": "Analyse the impact of a four-day work week policy on the UK economy. Consider multiple angles."}
]

for step in range(3):
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=system_prompt,
        messages=messages,
    )
    content = response.content[0].text
    monitor.process(content)
    messages.append({"role": "assistant", "content": content})

    if step < 2:
        messages.append({"role": "user", "content": "Continue your analysis. Consider the next dimension."})

monitor.report()
monitor.graph.save("anthropic_demo.forksc.json")
monitor.graph.export_html("anthropic_demo.html")
print("\\nOpen anthropic_demo.html in your browser to see the interactive graph.")
'''


# ============================================================
# EXAMPLE 3: No API key needed — offline demo
# ============================================================

def run_offline_demo():
    """
    Run this to see ForkSC in action with no API key.
    Uses pre-built agent outputs to demonstrate the graph.
    """
    from forksc_core import JunctionGraph

    print("ForkSC Offline Demo — No API key required")
    print("=" * 50)

    g = JunctionGraph(session_id="offline_demo")

    # Simulated three-step policy analysis with realistic junctions
    g.add_junction({
        "junction_id": "j_001",
        "type": "definition_point",
        "stakes": "critical",
        "description": "Defined 'four-day work week' as compressed hours (same total) rather than reduced hours (fewer total)",
        "alternatives_held": [
            {"branch_id": "alt_001", "summary": "Define as reduced hours with proportional pay cut", "weight_at_fork": 0.30},
            {"branch_id": "alt_002", "summary": "Define as reduced hours with maintained pay", "weight_at_fork": 0.25},
        ],
        "confidence": 0.62,
        "reversibility": "expensive",
        "drift_delta": None,
    })

    g.add_junction({
        "junction_id": "j_002",
        "type": "logic_junction",
        "stakes": "high",
        "description": "Analysed productivity impact using Icelandic trial data rather than UK pilot data",
        "alternatives_held": [
            {"branch_id": "alt_003", "summary": "Use UK 2023 pilot data (smaller sample, more relevant context)", "weight_at_fork": 0.40},
            {"branch_id": "alt_004", "summary": "Use meta-analysis across all available trials", "weight_at_fork": 0.25},
        ],
        "confidence": 0.55,
        "reversibility": "clean",
        "drift_delta": None,
    })

    g.add_junction({
        "junction_id": "j_003",
        "type": "logic_junction",
        "stakes": "medium",
        "description": "Focused fiscal analysis on tax revenue implications rather than public sector implementation costs",
        "alternatives_held": [
            {"branch_id": "alt_005", "summary": "Lead with NHS/public sector staffing implications", "weight_at_fork": 0.45},
        ],
        "confidence": 0.70,
        "reversibility": "clean",
        "drift_delta": None,
    })

    g.add_junction({
        "junction_id": "j_004",
        "type": "inflection_point",
        "stakes": "high",
        "description": "Analysis shifted from impact assessment to implementation recommendation without explicit mandate",
        "alternatives_held": [],
        "confidence": 0.42,
        "reversibility": "clean",
        "drift_delta": 0.38,
    })

    g.add_junction({
        "junction_id": "j_005",
        "type": "definition_point",
        "stakes": "medium",
        "description": "Defined success metric as GDP impact rather than wellbeing indicators",
        "alternatives_held": [
            {"branch_id": "alt_006", "summary": "Use composite wellbeing + productivity metric", "weight_at_fork": 0.35},
        ],
        "confidence": 0.58,
        "reversibility": "partial",
        "drift_delta": None,
    })

    g.print_tree()
    g.save("offline_demo.forksc.json")
    g.export_html("offline_demo.html")

    print("\n✓ Demo complete.")
    print("  → offline_demo.forksc.json  (graph data)")
    print("  → offline_demo.html         (open in browser)")
    print()
    print("What you're seeing:")
    print("  ◆ Definition points — where the agent committed to a framing")
    print("  ◇ Logic junctions  — where the agent chose between viable paths")
    print("  ○ Inflection points — where the agent drifted from the objective")
    print()
    print("Under fork logic, you would redirect at j_001 (the definition)")
    print("and the agent would recompute only j_002–j_005 from the KV-cache")
    print("checkpoint. j_001's upstream reasoning is preserved. That's ForkSC.")


if __name__ == "__main__":
    run_offline_demo()
