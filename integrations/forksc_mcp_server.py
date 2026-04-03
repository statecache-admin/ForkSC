"""
ForkSC MCP Server — Reasoning Graph Orchestration

A Model Context Protocol server that enables any MCP-compatible client
(Claude Desktop, Cursor, ChatGPT, VS Code, etc.) to emit typed semantic
junctions, navigate reasoning graphs, and redirect from checkpoints.

Four tools:
  - create_junction: emit a typed junction tag at a decision point
  - read_reasoning_graph: retrieve the full session reasoning graph
  - redirect_from_junction: restore to a junction, inject new context, resume
  - hold_junction: flag for asynchronous human review

Run: python forksc_mcp_server.py
Transport: stdio (standard MCP local transport)

ForkSC V1.2 · State Cache Systems · Open Source
"""

import json
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Initialize the MCP Server
mcp = FastMCP("ForkSC-Orchestrator")

STATE_FILE = "graph_state.json"


def load_state():
    """Loads the reasoning graph from disk."""
    if not os.path.exists(STATE_FILE):
        initial_state = {
            "protocol_version": "1.2",
            "active_pointer": "root",
            "junctions": {}
        }
        save_state(initial_state)
        return initial_state
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    """Writes the reasoning graph to disk."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


@mcp.tool()
def create_junction(
    junction_id: str,
    type: str,
    stakes: str,
    description: str,
    alternatives_held: list,
    confidence: float = 0.5,
    reversibility: str = "clean",
    operator_id: str = "system"
) -> str:
    """
    Call this tool whenever you reach a decision point, divergence in logic,
    or methodological choice. Every high-stakes assumption must be recorded.

    Valid types: 'definition_point', 'logic_junction', 'inflection_point'.
    Valid stakes: 'low', 'medium', 'high', 'critical'.
    Valid reversibility: 'clean', 'partial', 'expensive', 'irreversible'.
    Confidence: 0.0 to 1.0 — your self-assessed confidence in the chosen path.
    """
    state = load_state()

    if junction_id in state["junctions"]:
        return f"Error: Junction '{junction_id}' already exists."

    if type not in ("definition_point", "logic_junction", "inflection_point"):
        return f"Error: Invalid junction type '{type}'."

    if stakes not in ("low", "medium", "high", "critical"):
        return f"Error: Invalid stakes level '{stakes}'."

    if reversibility not in ("clean", "partial", "expensive", "irreversible"):
        return f"Error: Invalid reversibility '{reversibility}'."

    junction_payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "type": type,
        "stakes": stakes,
        "description": description,
        "alternatives_held": alternatives_held,
        "confidence": max(0.0, min(1.0, confidence)),
        "reversibility": reversibility,
        "operator_id": operator_id,
        "status": "active",
        "downstream": []
    }

    # Link to previous active junction
    previous = state["active_pointer"]
    if previous != "root" and previous in state["junctions"]:
        state["junctions"][previous]["downstream"].append(junction_id)

    state["junctions"][junction_id] = junction_payload
    state["active_pointer"] = junction_id
    save_state(state)

    return f"SUCCESS: Junction '{junction_id}' recorded. Type: {type}. Stakes: {stakes}. Confidence: {confidence}. Graph updated."


@mcp.tool()
def read_reasoning_graph() -> str:
    """
    Call this tool to read the entire reasoning graph and understand your
    current context. Use this to orient yourself before continuing if
    you lose track of the reasoning tree.
    """
    state = load_state()
    summary = {
        "protocol_version": state["protocol_version"],
        "active_pointer": state["active_pointer"],
        "total_junctions": len(state["junctions"]),
        "junctions": state["junctions"]
    }
    return json.dumps(summary, indent=2)


@mcp.tool()
def redirect_from_junction(
    target_junction_id: str,
    new_branch_rationale: str,
    operator_id: str = "human"
) -> str:
    """
    Call this tool when instructed by the user to abandon the current
    reasoning path and redirect from a previous junction. The original
    downstream branch is preserved as a latent, addressable path — not
    deleted. Only downstream reasoning is regenerated. Upstream is preserved.
    """
    state = load_state()

    if target_junction_id not in state["junctions"]:
        return f"Error: Target junction '{target_junction_id}' not found in graph."

    junction = state["junctions"][target_junction_id]

    # Preserve the original downstream branch as latent
    if junction.get("downstream"):
        junction["original_downstream"] = junction["downstream"].copy()
        junction["downstream_status"] = "latent"
        junction["downstream"] = []

    # Record the redirect event
    junction["redirect_event"] = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "rationale": new_branch_rationale,
        "operator_id": operator_id,
        "original_branch": "preserved"
    }

    # Move the active pointer back
    state["active_pointer"] = target_junction_id
    save_state(state)

    return (
        f"SUCCESS: Reasoning redirected. Active pointer reset to '{target_junction_id}'. "
        f"Original downstream preserved as latent branch. "
        f"Proceed with new reasoning from this junction."
    )


@mcp.tool()
def hold_junction(
    junction_id: str,
    reason: str,
    operator_id: str = "human"
) -> str:
    """
    Flag a junction for asynchronous human review without intervening.
    Enables multi-operator collaboration — one operator can hold a junction
    for another operator's review. The reasoning continues but the held
    junction is surfaced for attention.
    """
    state = load_state()

    if junction_id not in state["junctions"]:
        return f"Error: Junction '{junction_id}' not found in graph."

    state["junctions"][junction_id]["hold"] = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "reason": reason,
        "operator_id": operator_id,
        "status": "awaiting_review"
    }

    save_state(state)

    return (
        f"SUCCESS: Junction '{junction_id}' held for review. "
        f"Reason: {reason}. Operator: {operator_id}."
    )


if __name__ == "__main__":
    mcp.run_stdio()
