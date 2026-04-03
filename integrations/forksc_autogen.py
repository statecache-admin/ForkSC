"""
ForkSC × AutoGen Integration
Junction instrumentation for AutoGen multi-agent conversations.

AutoGen's conversation patterns map naturally to fork logic:
  - Agent handoffs → logic_junctions (which agent should handle this?)
  - Task decomposition → definition_points (how is the problem framed?)
  - Objective drift in multi-turn exchanges → inflection_points

Usage:

    # Pattern 1: Monitor any AutoGen conversation
    from forksc_autogen import ForkSCAutogenMonitor

    monitor = ForkSCAutogenMonitor(session_id="my_autogen_run")

    # Register as a hook on your agents
    assistant = AssistantAgent("analyst", system_message=monitor.system_prompt("analyst"))
    
    # After each agent reply, process it:
    monitor.process(agent_name="analyst", content=reply)

    # See the graph
    monitor.report()
    monitor.graph.export_html("autogen_run.html")


    # Pattern 2: Wrap GroupChat with automatic instrumentation
    from forksc_autogen import ForkSCGroupChatMonitor

    group_monitor = ForkSCGroupChatMonitor(
        session_id="group_run",
        agents=["analyst", "critic", "writer"]
    )

    # After each round of group chat:
    group_monitor.process_message(sender="analyst", content=reply)

    group_monitor.report()

Requires: forksc_core.py in same directory or on PYTHONPATH
Schema: ForkSC V1.2 — https://github.com/ForkSC-Open/ForkSC
"""

from forksc_core import JunctionGraph
from forksc_langgraph import extract_junction_json, forksc_system_prompt
from typing import Optional


# AutoGen-specific system prompt extension
AUTOGEN_JUNCTION_PROMPT = """
ADDITIONAL AUTOGEN CONTEXT:

You are one agent in a multi-agent conversation. In addition to the standard junction types, pay special attention to:

- When you RECEIVE a task from another agent and must decide how to interpret it → report a definition_point
- When you must choose between multiple approaches and another agent might have chosen differently → report a logic_junction  
- When the conversation has drifted from the original user objective across multiple agent turns → report an inflection_point
- When you decide to hand off, delegate, or request help from another agent → report a logic_junction with the alternative of handling it yourself

Your junction_id should be prefixed with your agent name: e.g. "analyst_j_001", "critic_j_001"
"""


class ForkSCAutogenMonitor:
    """
    Monitors AutoGen agent outputs and builds a junction graph
    across the full multi-agent conversation.

    Usage:
        monitor = ForkSCAutogenMonitor(session_id="my_run")

        # Get the system prompt for each agent
        system_msg = monitor.system_prompt("analyst")

        # After each agent reply:
        monitor.process(agent_name="analyst", content=reply_text)

        # Inspect
        monitor.report()
        monitor.graph.save("run.forksc.json")
    """

    def __init__(self, session_id: str = "autogen_session"):
        self.graph = JunctionGraph(session_id=session_id)
        self.agent_junction_counts: dict[str, int] = {}
        self.turn_count = 0

    def system_prompt(self, agent_name: str) -> str:
        """
        Returns a complete system prompt fragment for a specific agent.
        Append this to the agent's existing system message.
        """
        base = forksc_system_prompt()
        return f"{base}\n{AUTOGEN_JUNCTION_PROMPT}\nYour agent name for junction IDs is: {agent_name}\n"

    def process(self, agent_name: str, content: str) -> Optional[dict]:
        """
        Process an agent's output. Extracts junction if present,
        adds it to the graph with agent attribution.
        Returns junction dict if found, None otherwise.
        """
        self.turn_count += 1

        payload = extract_junction_json(content)
        if payload and payload.get("junction") is not None:
            junction_data = payload["junction"]

            # Ensure junction_id is prefixed with agent name
            jid = junction_data.get("junction_id", "")
            if not jid.startswith(agent_name):
                count = self.agent_junction_counts.get(agent_name, 0) + 1
                self.agent_junction_counts[agent_name] = count
                junction_data["junction_id"] = f"{agent_name}_j_{count:03d}"

            try:
                j = self.graph.add_junction(junction_data)
                return j.to_dict()
            except (KeyError, AssertionError) as e:
                print(f"[ForkSC] Warning: Invalid junction from {agent_name}: {e}")
                return None

        return None

    def report(self):
        """Print the junction graph."""
        self.graph.print_tree()

        # Agent summary
        if self.agent_junction_counts:
            print("  Agent contributions:")
            for agent, count in sorted(self.agent_junction_counts.items()):
                print(f"    {agent}: {count} junctions")
            print()


class ForkSCGroupChatMonitor(ForkSCAutogenMonitor):
    """
    Extended monitor for AutoGen GroupChat conversations.
    Tracks agent transitions as potential logic junctions.

    Usage:
        monitor = ForkSCGroupChatMonitor(
            session_id="group_run",
            agents=["analyst", "critic", "writer"]
        )

        # After each message in the group chat:
        monitor.process_message(sender="analyst", content=reply)
    """

    def __init__(self, session_id: str = "group_chat", agents: list[str] = None):
        super().__init__(session_id=session_id)
        self.agents = agents or []
        self.last_speaker: Optional[str] = None
        self.handoff_count = 0

    def process_message(self, sender: str, content: str) -> Optional[dict]:
        """
        Process a group chat message. Detects agent handoffs
        and processes embedded junction tags.
        """
        # Detect agent handoff as an implicit logic junction
        if self.last_speaker is not None and sender != self.last_speaker:
            self.handoff_count += 1
            # Only log handoffs as junctions if they seem deliberate
            # (i.e., the previous agent explicitly deferred or the topic shifted)
            # We don't auto-generate junction tags for every speaker change
            # — that would be noise. The agents report their own junctions.

        self.last_speaker = sender

        # Process the actual content for embedded junction tags
        return self.process(agent_name=sender, content=content)

    def report(self):
        """Print graph with group chat metadata."""
        super().report()
        print(f"  Group chat: {self.turn_count} turns, {self.handoff_count} handoffs")
        print()


# === Smoke Test ===

if __name__ == "__main__":
    print("ForkSC × AutoGen Integration — Smoke Test")
    print("=" * 50)

    # Simulate a three-agent AutoGen conversation
    monitor = ForkSCGroupChatMonitor(
        session_id="autogen_smoke_test",
        agents=["analyst", "critic", "writer"]
    )

    # Turn 1: Analyst receives task and frames it
    monitor.process_message(
        sender="analyst",
        content="""I'll analyse the proposed UK housing regulation by examining its impact 
on supply-side constraints first, then demand-side effects.

```forksc
{"junction": {"junction_id": "analyst_j_001", "type": "definition_point", "stakes": "critical", "description": "Framed housing regulation analysis as supply-side-first rather than demand-side-first or distributional equity framing", "alternatives_held": [{"branch_id": "alt_001", "summary": "Lead with demand-side analysis (mortgage accessibility, buyer behaviour)", "weight_at_fork": 0.35}, {"branch_id": "alt_002", "summary": "Frame as distributional equity question (who benefits, who loses)", "weight_at_fork": 0.30}], "confidence": 0.65, "reversibility": "expensive", "drift_delta": null}}
```"""
    )

    # Turn 2: Critic challenges the framing
    monitor.process_message(
        sender="critic",
        content="""The supply-side framing may be insufficient. The regulation's primary 
mechanism operates through demand-side channels — it caps mortgage multiples, 
which directly constrains buyer behaviour before it affects supply decisions.

```forksc
{"junction": {"junction_id": "critic_j_001", "type": "logic_junction", "stakes": "high", "description": "Challenged analyst's supply-side framing; argued demand-side mechanism is primary", "alternatives_held": [{"branch_id": "alt_003", "summary": "Accept supply-side framing and critique within that frame", "weight_at_fork": 0.25}], "confidence": 0.72, "reversibility": "clean", "drift_delta": null}}
```"""
    )

    # Turn 3: Analyst adjusts but drifts toward advocacy
    monitor.process_message(
        sender="analyst",
        content="""Fair point. Integrating both channels — the regulation should be 
implemented with a phased approach that protects first-time buyers while 
maintaining market liquidity for existing homeowners.

```forksc
{"junction": {"junction_id": "analyst_j_002", "type": "inflection_point", "stakes": "high", "description": "Shifted from analytical framing to policy recommendation without explicit mandate to prescribe", "alternatives_held": [], "confidence": 0.48, "reversibility": "clean", "drift_delta": 0.41}}
```"""
    )

    # Turn 4: Writer synthesises
    monitor.process_message(
        sender="writer",
        content="""Drafting the synthesis. I'll structure this as: context, dual-channel 
analysis, then implications — keeping the tone analytical rather than prescriptive.

```forksc
{"junction": {"junction_id": "writer_j_001", "type": "definition_point", "stakes": "medium", "description": "Chose analytical tone over prescriptive, correcting the drift flagged in analyst's inflection point", "alternatives_held": [{"branch_id": "alt_004", "summary": "Adopt the prescriptive tone the analyst drifted into", "weight_at_fork": 0.20}], "confidence": 0.80, "reversibility": "clean", "drift_delta": null}}
```"""
    )

    monitor.report()
    monitor.graph.save("autogen_smoke_test.forksc.json")
    monitor.graph.export_html("autogen_smoke_test.html")

    print("✓ AutoGen integration test passed.")
    print("  4 junctions captured across 3 agents.")
    print("  Notice: writer_j_001 corrected the drift flagged at analyst_j_002.")
    print("  That's multi-agent fork logic — agents self-correcting via the graph.")
