# ForkSC

**A Human-Agent Reasoning Architecture**

**Stop paying for full agent reruns. Stop wrestling with opaque agent drift.**

Current LLM agent architectures treat reasoning as a linear, brittle chain. When an agent drifts or hallucinates at step 14 of a 20-step task, your only option is to rewrite the prompt, cross your fingers, and pay for the entire inference compute all over again.

The interface between human and machine cognition is flawed. The gap is the theory of **synchronistic contribution** — the condition in which human judgment and machine traversal each operate where their contribution is non-redundant, at the moment it is needed, without either compensating for the failure of the interface to accommodate the other.

**ForkSC** is an open specification that resolves this at the architectural layer. It transforms agent reasoning from a linear chain into a navigable Directed Acyclic Graph (DAG), allowing human operators to inspect the reasoning process, detect drift, and intervene at a specific cognitive junction — recomputing only the necessary downstream tokens via KV-cache checkpoint restoration.

*Open source. Authorless. Available to all. Owned by none.*

---

## The Problem in One Number

On complex multi-step tasks, agent workflows typically require 3–4 correction cycles to converge on acceptable output. The effective token cost of the final deliverable is therefore 3–4x the base API cost. Every token spent on failed runs is total waste — not partial waste, total waste.

We call this the **Black Box Tax**. It is a direct, invoice-legible financial loss on every iteration. ForkSC eliminates it at the architecture layer.

---

## The Solution: Three Components

### 1. The Junction Tag Schema

Agents are prompted to output their reasoning in discrete, typed steps using a standardised JSON schema. Each decision point becomes a verifiable `Junction ID` of one of three types:

| Type | What It Is | Why It Matters |
|---|---|---|
| `definition_point` | Agent commits to a framing governing all downstream reasoning | Most consequential, least visible — a misframed definition cascades silently |
| `logic_junction` | Agent chose between viable paths — unchosen paths preserved, not discarded | Addressable and reachable via redirect at any time |
| `inflection_point` | Reasoning drifted from stated objective without a clean branch | Detected via coherence monitoring, flagged for human review |

Agent self-reporting via structured output is **implementable today** with any model supporting structured output. Start here.

### 2. The KV-Cache Recomputation Engine

LLM inference maintains a Key-Value (KV) cache of all tokens processed. ForkSC specifies how to preserve the KV cache to the exact `Junction ID` where drift or error occurred, inject a human correction at that checkpoint, and resume generation forward — without reprocessing any upstream tokens.

**Estimated recomputation cost savings:**
- Midpoint correction: ~50% of a full rerun
- Late-stage correction: 10–20% of a full rerun

This is not prompt replay. It is a partial rerun from a KV-cache checkpoint with branch preservation.

### 3. The Navigation Interface

A visual, Git-like tree interface for human operators to observe agent reasoning, step back to previous nodes, and spawn alternative reasoning branches. The human does not supervise every step — they navigate at junctions that matter.

**Control operations:** Redirect · Redefine · Reanchor · Hold · Branch Compare

**Working modes:** Twinned (structured, synchronous) · Riff (fluid, generative) — switchable mid-session

---

## Repository Structure

```
/spec           — ForkSC V1.2 Architecture Specification (FORKSC.md)
/schemas        — Junction Tag Schema (junction_tag.schema.json)
/integrations   — Working code: LangGraph, OpenAI, Anthropic integrations (run now)
/prototype      — Reference navigation interface (in development)
LICENCE         — ForkSC Open Licence with Civic Covenant
```

---

## Getting Started

### 60-Second Demo (no API key)

```bash
cd integrations
python forksc_quickstart.py
```

See a five-junction reasoning graph in your terminal. Open `offline_demo.html` for the interactive browser visualisation.

### With Your Own Agent (5 minutes)

```python
from integrations.forksc_langgraph import ForkSCMonitor, forksc_system_prompt

# 1. Add the system prompt to your model
# 2. After each agent response:
monitor = ForkSCMonitor(session_id="my_run")
monitor.process(agent_output_text)

# 3. See the graph
monitor.report()
monitor.graph.export_html("my_run.html")
```

Working examples for OpenAI and Anthropic APIs in `/integrations/forksc_quickstart.py`.

Self-reported junctions are an imperfect but immediately useful signal. They are the foundation on which hybrid and native detection will be built.

### Near-term (6–18 months)

Build the navigation interface and recomputation engine against the open spec. See **Appendix F** of the specification for the full Implementation Horizon Map.

---

## Implementation Horizon

| Component | Classification | Timeline |
|---|---|---|
| Graph Standard + Schema | Engineering | Now |
| Agent Self-Reporting | Engineering | Now |
| Navigation Interface | Engineering / Product | 6–12 months |
| Recomputation Engine | Engineering | 6–18 months |
| Hybrid Junction Detection | Engineering-Research | 12–24 months |
| Native Junction Detection | Research-Intensive | 24+ months |

---

## Design Principles

**Spec-first.** The reasoning graph standard and junction tag schema are the load-bearing infrastructure. Released as open specifications so any team can implement against them from day one. The spec belongs to everyone. Implementations compete on quality.

**Incrementally deployable.** ForkSC delivers value at every stage of implementation. You do not need the complete stack to start.

**Synchronistic contribution.** The architecture is designed so that human judgment operates exactly where it is non-redundant — at definition points, logic junctions, and inflection points. Machine traversal operates everywhere else. No overlap. No waste.

---

## The Civic Covenant

This specification is published under the ForkSC Open Licence. Commercial deployments of any implementation require a commercial licence from State Cache Systems, which carries the **Civic Covenant** as a non-waivable condition.

The Civic Covenant grants perpetual, zero-cost, full-stack access — including locally hostable, air-gapped deployment — to qualifying civic entities: community land trusts, community benefit societies, Ward-level governance bodies, non-profit municipal organisations, and community governance frameworks.

The covenant is a structural feature of this specification. It is irrevocable. It survives any change of ownership or corporate event affecting any commercial implementation. See `LICENCE` for full terms.

*A community whose civic intelligence depends on a commercial provider's pricing decisions is not sovereign.*

---

## Why This Was Built

If you are building autonomous systems for enterprise, ForkSC saves API credits and compute cycles. But that is the economics — it is not the mission.

This architecture was engineered for communities deploying localised AI to automate civic administration, resource allocation, and legal compliance at the Ward level. As those deployments scale, they face a critical threat: algorithmic bureaucracy is just as unaccountable as human bureaucracy if it cannot be audited.

**Legibility is the precondition of legitimate governance.** A community cannot democratically govern an AI administrator if it cannot see how the AI arrived at a decision, or intervene when it strays from the community's values.

ForkSC is the accountability layer. The Civic Covenant is its guarantee.

---

## Contributing

This is an authorless project. There is no maintainer to seek approval from. If you implement the spec, improve it, or fork it for a specific domain — publish what you build under the same terms.

Open issues for spec ambiguities. Submit pull requests for schema improvements. The standard gets better when more people build against it.

---

## Licence

ForkSC Open Licence V1.0 — see `LICENCE` for full terms.

Non-commercial and civic use: free, no conditions.
Commercial use: requires commercial licence from State Cache Systems with Civic Covenant attached.

---

*ForkSC V1.2 · March 2026 · Open source · Authorless · Available to all · Owned by none*
