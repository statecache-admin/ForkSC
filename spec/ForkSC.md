# ForkSC: A Human-Agent Reasoning Architecture

**Version 1.2 · March 2026**

*This document is authorless. It is offered as open infrastructure — available to all, owned by none, forkable by anyone.*

*Open source · Authorless · Available to all · Owned by none*

*Companion document: The Sovereign Commons V2.5 — UK Reference Implementation*

---

## Table of Contents

- [Part One — The Problem](#part-one--the-problem)
- [Part Two — The Framework](#part-two--the-framework)
- [Part Three — The Interface](#part-three--the-interface)
- [Part Four — The Economics](#part-four--the-economics)
- [Part Five — Building It](#part-five--building-it)
- [Appendix A — Junction Tag Schema (JSON)](#appendix-a--junction-tag-schema-json)
- [Appendix B — Junction Instrumentation Layer Specification](#appendix-b--junction-instrumentation-layer-specification)
- [Appendix C — Recomputation Engine Specification](#appendix-c--recomputation-engine-specification)
- [Appendix D — Prototype Build Brief](#appendix-d--prototype-build-brief)
- [Appendix E — Publication Strategy](#appendix-e--publication-strategy)
- [Appendix F — Implementation Horizon Map](#appendix-f--implementation-horizon-map)
- [Bridge Note — The Governance of Reasoning](#bridge-note--the-governance-of-reasoning)

---

## Part One — The Problem

The interface between human and machine cognition is flawed and the gap is the theory of synchronistic contribution.

Human cognition contributes navigational judgment — the capacity to know which framing matters, to recognise drift from real intent, to decide which path is worth pursuing when more than one is viable. These acts require values, contextual knowledge, and the kind of tacit understanding that cannot be fully written down in advance. They are not tasks. They are judgments.

Machine cognition contributes traversal — execution across the space between those judgments, pattern recognition at scale, elaboration without fatigue. These acts require neither values nor wisdom. They require well-specified territory and sufficient compute.

Synchronistic contribution is the condition in which each operates where its contribution is non-redundant, at the moment it is needed, without either compensating for the failure of the interface to accommodate the other.

Current agent architecture does not achieve this condition. The interface was not designed to.

Instead it generates redundancy in both directions. The human is pushed into territory that does not belong to them — specifying prompts to anticipate every possible misalignment in advance, reviewing outputs they cannot interrogate, restarting processes they cannot interrupt. These are not contributions. They are compensations. The human's actual capability has nowhere to land.

The machine pays the arithmetic cost of the same failure. When the human cannot intervene at the precise moment and location where intervention is needed, the only available correction is to discard the run and begin again. Every token spent on validated upstream reasoning is wasted. The machine re-traverses ground the human had already accepted.

The result is an architecture that wastes what both bring. Neither is operating at the level of its actual capability. The interface is the constraint.

This is not a capability problem. It will not be resolved by more capable models or more elaborate prompts. It is a design problem — and it has a specific solution.

That solution begins with a question asked at every point in the reasoning process: whose contribution is non-redundant here?

Where the answer is the human — where the decision requires judgment, values, or contextual knowledge the machine does not hold — the interface must make that contribution possible. The human must be able to enter the reasoning at that point, read what is there, and redirect from it without discarding what came before.

Where the answer is the machine — where the work is traversal, elaboration, execution across defined territory — the interface must stand aside. The human should not be in this territory. Their presence here is waste, not contribution.

The economics of this distinction are direct. When the human stops compensating and starts contributing judgment at genuine junctions, the correction cycles that drive token waste disappear. When the machine stops re-traversing validated reasoning and builds forward from preserved checkpoints, the recomputation cost drops to the minimum necessary. The savings are not a feature. They are a measurement of what the broken interface was costing.

The trust argument is equally direct. An agent whose reasoning is navigable is trustworthy not because it has been made more constrained, but because the human can read where it made its choices and redirect from the ones that were wrong. Trust is a property of the interface, not of the agent.

The energy argument follows from the same principle. Redundant computation is redundant energy consumption. An interface designed for synchronistic contribution eliminates the redundancy structurally — without waiting for more efficient hardware or cleaner grids.

Everything that follows in this document is a consequence of taking synchronistic contribution seriously as a design principle. The junction taxonomy defines where human judgment is non-redundant and what form that judgment takes at each type of decision point. The recomputation engine ensures that human intervention does not require discarding prior work. The navigation interface gives the human a surface on which judgment can land at the right moment.

The principle is not a motivation for building ForkSC. It is the specification from which ForkSC is derived.

*The practical implementation of that principle begins with the reasoning graph.*

---

## Part Two — The Framework

The alternative to a reasoning chain is a reasoning graph. The distinction is not cosmetic. It determines everything about what human-agent collaboration can become.

A chain is linear, sequential, and brittle. Each step follows the last. The reasoning has one entry point and one exit. Forks — when they occur — are resolved internally and silently. The path not taken disappears.

A graph has nodes, edges, and preserved alternative paths. It is traversable in multiple directions. Forks are not resolved and discarded — they are held open as addressable junctions. The reasoning has topology. It can be navigated.

Fork logic is the architectural principle that makes reasoning graphs possible. It treats every decision point in agent reasoning as a first-class object — named, typed, tagged, and preserved. Not a log entry. Not a debug trace. A navigable node in a cognitive map that the human can read, interrogate, and redirect.

### The Junction Taxonomy

Not all decision points are equivalent. Fork logic distinguishes three types, each requiring different treatment at the interface level.

#### Definition Points

Where the agent establishes what something is — a commitment to a framing that shapes everything downstream. These are frequently the most consequential junctions and almost always the least visible. A misframed definition point does not produce one wrong output — it produces a cascade of outputs that are coherent with each other and wrong together. Definition points are irreducibly human territory: commitment to a framing requires values, not just logic. They must be surfaced, named, and held open for challenge.

#### Logic Junctions

Where two or more viable reasoning paths genuinely diverge and the agent chose one. The unchosen paths were not wrong, merely less weighted at that moment under those conditions. Logic junctions are human territory because the weighting of paths against each other requires judgment about what matters, not just what is probable. The agent's choice is recorded but not final. Unchosen paths remain latent and reachable.

#### Inflection Points

The subtlest and most dangerous junction type. Not a fork but a bend — a moment where the reasoning does not branch but shifts register, changes weighting, or quietly reframes the objective without announcement. Inflection points are human territory because recognising drift from real intent requires knowing what the real intent was — which only the human who held the intent can verify. Detection requires the agent to monitor coherence between its current reasoning trajectory and its stated objective, flagging moments where the two have measurably diverged.

### The Tag Structure

For fork logic to be navigable rather than merely recorded, tags carry six fields: **Type** (junction category), **Stakes** (downstream contingency), **Alternatives Held** (unchosen paths with brief characterisation), **Confidence** (agent certainty at this junction), **Reversibility** (cost of redirection), and **Drift Delta** (inflection points only — semantic distance from stated objective).

See Appendix A for the formal JSON schema. See `/schemas/junction_tag.schema.json` for the standalone schema file.

### Parsing and Refining

The tag structure enables two fundamentally different kinds of human engagement at a junction — and the distinction maps directly onto the non-redundancy principle.

**Parsing** is retrospective and analytical. The human reads the junction — understands what choice was made, what was at stake, what was discarded. Parsing does not change anything. It builds the human's understanding of the reasoning terrain without colonising machine territory. It answers: *what happened here, and why?*

**Refining** is prospective and generative. The human intervenes at the junction — substitutes a definition, redirects a fork, reanchors a drifted objective — and the agent recomputes the affected downstream reasoning. It answers: *what should happen from here instead?*

The ability to parse without refining is as important as the ability to refine. A human who has parsed enough junctions develops genuine confidence in the agent's judgment at low-stakes junctions and reserves intervention for the ones that actually matter.

### The Reasoning Graph

These components combine into a reasoning graph that is categorically different from a reasoning chain. The graph is the agent's reasoning made spatial — with topology the human can orient within, landmarks that draw navigational attention, preserved paths that can be revisited, and a structure that persists across a session and accumulates as the work develops.

The human's relationship to this graph is not supervision. It is navigation. The agent traverses the terrain and maps it as it goes. The human reads the map, identifies where the route needs adjustment, and redirects from the relevant junction. The agent develops the new route forward. Each contributes where their contribution is non-redundant. Neither compensates for the other.

---

## Part Three — The Interface

The framework is only as good as the surface through which the human engages it. The dashboard is not a readout — it is a cognitive map and control surface simultaneously. The human does not watch the agent from behind glass. They navigate alongside it, with full reach into the reasoning graph at any junction.

### What the Dashboard Shows

The primary view is the reasoning graph rendered as a navigable topology — not a list, not a log, not a sequential transcript. A spatial representation where nodes represent junctions, edges represent logical connections, depth indicates contingency, and breadth indicates alternatives held.

At a glance the human sees:

- **The shape of the reasoning** — where the work is dense and branching, where it is linear and confident, where it has drifted.
- **The live frontier** — where the agent is currently working and what junction it is approaching.
- **The intervention history** — where the human has previously parsed or refined, recorded as a layer on the graph.
- **Quality indicators** — confidence levels, drift deltas, stakes ratings directing attention to where engagement matters most.

### The Control Surface

- **Redirect** — at any logic junction, select an unchosen branch. The agent develops it forward. The original is preserved.
- **Redefine** — at definition points, substitute a different framing. The agent recomputes all contingent downstream reasoning.
- **Reanchor** — at inflection points, restate the original objective. The agent recalibrates its trajectory.
- **Hold** — flag a junction for later engagement without intervening now. Enables asynchronous collaboration.
- **Branch Compare** — request brief parallel development of an unchosen path alongside the chosen one before committing.

### Two Working Modes

The non-redundancy principle operates at different cadences depending on the nature of the task. ForkSC supports two working modes, switchable at any point in a session.

**Twinned working** is structured and synchronous. The agent surfaces junctions, awaits navigation input, and continues. Human judgment is engaged frequently and deliberately. Suits tasks where the stakes of misalignment are high — legal analysis, policy drafting, technical specification. Produces a legible reasoning trail that can be interrogated, explained, and defended.

**Riff working** is fluid and generative. The agent runs further between check-ins. The human trusts the machine's traversal across longer stretches and intervenes only when judgment is genuinely required. Suits creative, exploratory, and generative work where momentum matters more than precision checkpointing.

Both modes are expressions of the same non-redundancy principle operating at different frequencies. Real work requires both.

### What the Interface Is Not

- **Not a transcript viewer.** A transcript is a chain rendered as text. It has the same opacity as the original reasoning, just more slowly revealed.
- **Not a step-approval workflow.** Requiring human sign-off at every agent action is not collaboration — it is slow human execution with an AI assistant.
- **Not a debugging tool.** The audience is not developers inspecting agent behaviour. It is humans directing agent work.
- **Not a black box with a bigger window.** Adding visibility to a chain does not make it a graph. The architecture has to change, not just the display.

---

## Part Four — The Economics

### The True Cost of a Reasoning Chain

A single agent run on a complex multi-stage task consumes tokens at every step of its reasoning process. On tasks requiring three or four iterations to converge on acceptable output — which is common for complex, nuanced, or creative work — the effective token cost of the final deliverable is three or four times the cost of a single run. The human paid for four runs and received one usable output. Every token spent on the failed runs is waste — not partial waste, total waste.

### The ForkSC Cost Structure

Under fork logic the cost structure is categorically different. The first run proceeds normally — the agent traverses the reasoning graph, tags junctions, and produces output. This is the only full run that will be paid for. When the human identifies a misaligned junction and refines at that node, the KV-cache recomputation engine restores the reasoning state to that checkpoint and regenerates only downstream tokens. Everything upstream is preserved and reused.

On a complex task where the misaligned junction is identified midway through the reasoning graph, the recomputation cost may be approximately 50% of a full run. On a task where the junction is near the end, the cost may be 10–20%. The savings are not a feature. They are a measurement of what the broken interface was costing.

### The PAYG Alignment

As the market matures, AI pricing is moving toward genuine pay-per-token granularity. In a PAYG environment, the cost of reasoning chain iteration becomes visible and attributable. Every failed run appears as a line item. An agent platform built on fork logic will demonstrably cost less per quality output unit than one built on reasoning chains. This is not a marginal efficiency claim — it is an invoice-legible structural advantage.

### The Energy Argument

Energy consumption in AI inference is directly proportional to token count. Fewer tokens means less compute. Less compute means less energy. The efficiency gain of fork logic over chain iteration is simultaneously a cost reduction and an energy reduction, by the same factor.

Regulatory frameworks requiring energy accounting for AI workloads are in development in the EU, UK, and US. Fork logic addresses the demand side structurally and immediately — without waiting for more efficient hardware or cleaner grids.

### The Quality-Trust-Delegation Loop

Legible reasoning builds trust. Trust enables delegation. Delegation increases productivity. Productivity increases value per token. The loop is virtuous and self-reinforcing.

It does not operate under the chain model because the chain model has no mechanism for building trust incrementally — each run is opaque, each correction resets the process. ForkSC makes the loop possible because the human's accumulated experience of parsing junctions builds genuine confidence in the agent's judgment over time.

### The Competitive Calculus

Organisations and platforms that build on fork logic architecture will outcompete those that do not across every dimension that becomes more important as AI deployment matures: cost per output unit, energy per output unit, auditability per output unit, trust per output unit. The question is not whether this architecture is better. It is. The question is who builds it, when, and on what terms — open or closed, commons or captured.

---

## Part Five — Building It

The architecture is described. The economics are clear. The interface is specified. Significant components of this architecture can be built now, with existing tools, by small teams working in the open. This is not a moonshot. But neither is it a single, uniform engineering project. Some components are tractable engineering; others sit at the boundary of engineering and open research. This section is explicit about the difference.

### What Already Exists

- **Graph data structures** for representing reasoning topology are well understood. The reasoning graph is a directed acyclic graph with typed nodes and attributed edges.
- **Agent frameworks** with node-based architectures exist in partial form — LangGraph, LlamaIndex, AutoGen. Fork logic extends and redirects these foundations rather than replacing them.
- **KV-cache mechanisms** exist in all major inference frameworks. The ability to preserve and restore KV-cache state at a specified token position is an existing capability in vLLM, TGI, llama.cpp, and similar systems. ForkSC's recomputation engine leverages this directly.
- **Checkpoint and state persistence** mechanisms exist in current agent frameworks. What is absent is the semantic layer that makes checkpoints meaningful junctions rather than arbitrary recovery points.
- **Visualisation tools** for graph structures are mature — D3.js, Cytoscape, and similar libraries can render the reasoning graph as a navigable visual surface.

### What Needs to Be Built

- **The junction instrumentation layer** — semantic middleware that intercepts agent reasoning at decision points, classifies the junction type, constructs the tag object, preserves unchosen branches, and writes the node to the reasoning graph. See Appendix F for implementation classification and timeline.
- **The recomputation engine** — leverages existing KV-cache infrastructure to execute partial reruns from a specified junction checkpoint. See Appendix C for the full specification.
- **The navigation interface** — the dashboard as cognitive map and control surface. A significant interface design and frontend engineering project. A product problem, not a research problem.
- **The drift detection module** — monitors coherence between current reasoning trajectory and stated objective. The most research-intensive component.

### A Note on Implementation Honesty

The components above span a spectrum from tractable engineering to open research. The summary:

- **Engineering (12–18 months):** The reasoning graph standard, the navigation interface, and the core recomputation engine. Skilled engineering and product design required — no fundamental research breakthroughs needed.
- **Engineering-Research Hybrid (12–24 months):** The junction instrumentation layer. The interim approach is agent self-reporting via structured output schemas — implementable now, less reliable than external instrumentation, but provides the data to improve detection over time.
- **Research-Intensive (24+ months):** Reliable automated drift detection and native junction instrumentation. Dependent on interpretability research progress.

This layered timeline means fork logic can be deployed incrementally. The reasoning graph and interface deliver immediate value — legibility, navigation, branch preservation — even before the instrumentation layer reaches full maturity.

### An Open Architecture

Fork logic should be built as open infrastructure. A closed, proprietary implementation contradicts its core proposition: an architecture whose fundamental claim is legibility and accountability cannot be built on opaque proprietary infrastructure.

The proposed stack is four open layers:

- **Layer 1 — The reasoning graph standard.** An open specification for the graph data structure — node types, tag schema, edge attributes, serialisation format.
- **Layer 2 — The junction instrumentation SDK.** Open-source SDK implementing the instrumentation layer for major agent frameworks. Framework-agnostic at the graph layer.
- **Layer 3 — The recomputation engine.** Open-source engine leveraging KV-cache infrastructure to execute partial reruns from specified junction checkpoints.
- **Layer 4 — The navigation interface.** Open-source reference implementation of the dashboard.

### The Spec-First Strategy

The open-source mandate and the speed-to-market imperative are in genuine tension. If a commercial agent platform ships something fork-logic-adjacent as a proprietary feature before the open standard achieves critical mass, the window for establishing that standard narrows significantly.

The resolution is a spec-first strategy. The reasoning graph standard and the junction tag schema are released as open specifications immediately. This is how HTTP, JSON, and GraphQL established themselves: open specification, pragmatic about implementation. The spec belongs to everyone. The implementations compete on quality.

Priority sequence: publish the spec and schema first. Build the reference navigation interface second. Build the recomputation engine third. Develop the instrumentation layer iteratively, starting with agent self-reporting and progressively incorporating external detection as interpretability tooling matures.

### Who Should Build This

- **AI infrastructure developers** working on LangGraph, LlamaIndex, AutoGen — closest to the technical substrate, strongest incentive to differentiate on reasoning quality.
- **Enterprise AI teams** facing real deployment friction — the trust deficit, the iteration cost, the auditability requirement. Early adopters generate the evidence base.
- **Civic technology and open-source governance communities** — needing agent reasoning that is legible, accountable, and collectively navigable.
- **AI safety researchers** working on interpretability. The reasoning graph is an audit trail with semantic structure — more useful for understanding what agents actually do than token-level traces currently available.

### A Note on Timing

The agent platform market is forming now. The architectural choices being made in the next twelve to eighteen months will determine what agent infrastructure looks like for the following decade. Reasoning chains are the current default not because they are the right architecture but because they are the path of least resistance.

The window for establishing fork logic as an alternative standard is open but not indefinitely. This is the moment to publish the spec, build the proof of concept, and let the architecture prove itself.

---

## Appendix A — Junction Tag Schema (JSON)

The following is an abbreviated inline reference. The full schema with all field descriptions, constraints, and examples is available at `/schemas/junction_tag.schema.json`. Schema version: v1.2.

```json
{
  "junction_tag": {
    "junction_id":         { "type": "string" },
    "type":                { "enum": ["definition_point", "logic_junction", "inflection_point"] },
    "stakes":              { "enum": ["low", "medium", "high", "critical"] },
    "alternatives_held":   { "type": "array",
                             "items": {
                               "branch_id":      { "type": "string" },
                               "summary":        { "type": "string", "maxLength": 200 },
                               "weight_at_fork": { "type": "number", "min": 0, "max": 1 }
                             }},
    "confidence":          { "type": "number", "min": 0, "max": 1 },
    "reversibility":       { "enum": ["clean", "partial", "expensive"] },
    "drift_delta":         { "type": "number", "min": 0, "max": 1, "nullable": true },
    "kv_cache_checkpoint": {
                             "token_position":               { "type": "integer" },
                             "context_length_at_checkpoint": { "type": "integer" },
                             "cache_reference":              { "type": "string", "nullable": true }
    },
    "position":            {
                             "node_depth":          { "type": "integer" },
                             "sequence_index":      { "type": "integer" },
                             "parent_junction_id":  { "type": "string", "nullable": true }
    },
    "timestamp":           { "type": "string", "format": "date-time" },
    "human_intervention":  {
                             "operation": { "enum": ["redirect", "redefine", "reanchor",
                                                     "hold", "branch_compare", "parsed_no_action"] },
                             "timestamp":            { "type": "string", "format": "date-time" },
                             "operator_id":          { "type": "string", "nullable": true },
                             "intervention_content": { "type": "string", "nullable": true },
                             "note":                 { "type": "string", "nullable": true }
    }
  }
}
```

---

## Appendix B — Junction Instrumentation Layer Specification

The junction instrumentation layer sits between the base language model and the agent framework. It intercepts reasoning at decision points, classifies the junction, constructs the tag object, and writes the node to the reasoning graph before the agent proceeds.

### Implementation Phases

**Phase 1 — Agent Self-Reporting (available now):** The agent is prompted via structured output schemas to identify and tag its own junctions. The system prompt includes the junction taxonomy and tag schema. At each reasoning step, the agent outputs both its reasoning content and a structured junction tag (or null if no junction is present). Self-reported junctions should be treated as a useful but imperfect signal.

**Phase 2 — Hybrid Detection (12–24 months):** External monitoring supplements agent self-reporting. Cosine similarity between reasoning trajectory embeddings and session objective embeddings flags potential inflection points. Statistical analysis of token-level probability distributions flags moments of high uncertainty. Conflicts between self-reported and externally detected junctions are surfaced to the human for resolution.

**Phase 3 — Native Instrumentation (24+ months):** As mechanistic interpretability tools mature, junction detection moves from statistical inference to direct observation of model internals — activation patterns, attention head configurations, representational drift at the embedding layer.

### Junction Detection Signals

- **Semantic branch signal** — the agent generates or evaluates more than one candidate framing, path, or response before committing.
- **Definition commitment signal** — the agent produces a statement establishing a meaning that will govern downstream reasoning.
- **Coherence drift signal** — cosine similarity between current reasoning vector and session objective vector falls below threshold (default: 0.7).

### Agent Behaviour at Each Type

- **At `definition_point`:** Pause reasoning, write definition to tag's `definition_content` field, assign stakes via dependency scan, surface to dashboard.
- **At `logic_junction`:** Generate one-sentence summary of each evaluated alternative, assign relative weights, write all to `alternatives_held`, proceed on highest-weighted branch.
- **At `inflection_point`:** Compute drift delta, write to tag, flag for human review if delta exceeds threshold (default: 0.3). Agent does not self-correct — it surfaces and continues.

---

## Appendix C — Recomputation Engine Specification

The recomputation engine executes partial reruns of reasoning from a specified junction checkpoint, leveraging KV-cache infrastructure to avoid reprocessing upstream tokens.

### The KV-Cache Mechanism

LLM inference builds a Key-Value (KV) cache as it processes tokens — a running memory of attention keys and values for all tokens seen so far. Every junction tag records a `kv_cache_checkpoint` containing the `token_position` at which the junction occurred.

When a human redirects, redefines, or reanchors at junction J, the engine:

1. Reloads the KV cache to the state it held at `junction_J.kv_cache_checkpoint.token_position`
2. Injects the modified junction content at that checkpoint
3. Resumes generation forward from that point

All tokens upstream of the checkpoint are preserved in the KV cache and are not reprocessed. Only tokens downstream are regenerated. KV-cache persistence is supported in vLLM (prefix caching), TGI, llama.cpp (slot-based caching), and most production inference frameworks.

### How Recomputation Works in an LLM Context

LLM-based reasoning does not behave like a deterministic software build system. Recomputation from junction J means re-running inference from J's token position forward with the modified context. Everything upstream is preserved. Everything downstream is regenerated.

Because LLMs are stochastic, even nodes not logically dependent on the change at J may produce different outputs, as the altered text shifts the statistical context for all subsequent generation. "Targeted recomputation" is more accurately described as "partial rerun from a specified checkpoint" — cheaper than a full rerun, but not as surgically precise as subgraph rebuilding in a deterministic system.

Cost savings: approximately 50% of a full rerun at the midpoint; 10–20% near the end.

### Handling Stochastic Outputs

The engine preserves the original output as `branch_original` and writes recomputed output as `branch_recomputed`. Both are surfaced for human comparison. Where the difference falls below a semantic similarity threshold (default: 0.9 cosine similarity), the engine auto-commits. Where the difference exceeds the threshold, both branches are held open for human selection.

### Branch Preservation

The full original reasoning path from junction J forward is preserved as a latent branch. It remains addressable at any point. No reasoning is deleted. The graph accumulates all explored paths as a navigable record.

---

## Appendix D — Prototype Build Brief

### What the Prototype Does

Demonstrates fork logic on a single constrained reasoning task — a three-stage analytical problem with one junction of each type surfaced during the reasoning pass.

Shows: a rendered reasoning graph with three typed, colour-coded junction nodes; a junction detail panel with full tag object; a parse operation; a redirect operation on the logic junction with original and recomputed outputs displayed side by side.

### What the Prototype Does Not Do

Does not implement live agent reasoning. The reasoning graph is pre-populated with a realistic but static example. Recomputation is simulated via a language model API call with the checkpoint context prepended. Does not implement drift detection, multi-human collaboration, or asynchronous hold operations.

### Tech Stack

Single-file React artifact using a language model API for simulated recomputation. D3.js force-directed layout for reasoning graph. Junction detail panel as side drawer. Branch compare as two-column diff display. Tailwind for styling. No backend — all state in React.

### Success Criteria

**Non-technical users (60 seconds):** Understand that AI thinking has a visible structure they can explore. The insight to convey: *"The AI's reasoning has shape, and I can see it."*

**Technical users (60 seconds):** Understand why redirecting from a junction is architecturally different from re-prompting — that upstream reasoning is preserved in the KV cache, only downstream reasoning is regenerated, and unchosen paths remain addressable. The insight to convey: *"This is not a replay. It is a partial rerun from a KV-cache checkpoint with branch preservation."*

Both criteria must be met.

---

## Appendix E — Publication Strategy

### Minimum Viable Release

A GitHub repository under the **ForkSC-Open** organisation containing: `README.md`, `/spec/FORKSC.md`, `/schemas/junction_tag.schema.json`, `LICENCE`. No website, no launch event, no paper submission required at initial stage. The repo is the release.

### Primary Target Audience

Developers already working on agent frameworks and reasoning infrastructure — specifically contributors to LangGraph, LlamaIndex, AutoGen, and developers building on emerging agent platforms.

### Channel

Hacker News — a Show HN post linking the GitHub repo. Secondary: direct posts on LangGraph and AutoGen GitHub discussion boards framing fork logic as an extension proposal.

### Authorless Publication

Authorless — no individual's name on the specification. The work stands or falls on its merits. That is the right condition for infrastructure meant to belong to everyone.

### The Spec Establishes Prior Art

Publishing the open specification immediately and publicly timestamps the architecture. A specification publicly timestamped, attributed to no commercial entity, and explicitly made available for open implementation is substantially harder to capture than an unpublished idea. It becomes prior art. Publish the spec first.

---

## Appendix F — Implementation Horizon Map

| Component | Classification | Timeline | Approach |
|---|---|---|---|
| Reasoning Graph Standard (Layer 1) | Engineering | 3–6 months | Open specification. Node type definitions, tag schema, edge attributes, serialisation format as versioned JSON Schema. |
| Navigation Interface (Layer 4) | Engineering / Product | 6–12 months | Reference implementation in React + D3.js. Must satisfy both success criteria from Appendix D. |
| Recomputation Engine (Layer 3) | Engineering | 6–18 months | KV-cache checkpoint architecture. Context preservation to junction J via cache reload, regeneration from J forward. |
| Instrumentation — Self-Reporting (Layer 2, Phase 1) | Engineering | 3–6 months | Structured output prompting. Agent tags its own junctions. Implementable now. |
| Instrumentation — Hybrid Detection (Layer 2, Phase 2) | Engineering-Research Hybrid | 12–24 months | Embedding similarity analysis and probability distribution monitoring. |
| Instrumentation — Native Detection (Layer 2, Phase 3) | Research-Intensive | 24+ months | Activation-level junction detection. Target architecture. |
| Drift Detection — Self-Reported | Engineering | 3–6 months | Agent computes own drift delta per reasoning step. |
| Drift Detection — External Monitoring | Research-Intensive | 24+ months | Embedding-level coherence tracking. Dependent on interpretability tooling. |

### The Incremental Deployment Path

- **Immediate (0–6 months):** Publish the graph standard and tag schema. Build self-reporting instrumentation. Build the prototype.
- **Near-term (6–18 months):** Build the navigation interface and recomputation engine.
- **Medium-term (12–24 months):** Hybrid junction detection improves instrumentation quality.
- **Long-term (24+ months):** Native instrumentation and external drift detection.

At every stage, the architecture is usable and valuable.

---

## Bridge Note — The Governance of Reasoning

*The Sovereign Commons* is a document about governance — specifically about how communities can govern themselves with transparency, accountability, and collective agency in the face of complexity that would otherwise concentrate power in the hands of the few who can navigate it.

*ForkSC* is a document about reasoning — specifically about how agent cognition can be made transparent, accountable, and collectively navigable in the face of complexity that would otherwise concentrate interpretive power in the hands of the AI system and its operators.

The structural parallel is not coincidental. It reflects the same principle that runs through both documents: legibility is the precondition of legitimate governance. A community cannot meaningfully govern a process it cannot read. A human cannot meaningfully navigate reasoning they cannot see. Synchronistic contribution — each party operating where their contribution is non-redundant — is as much a governance principle as it is an architectural one.

The bridge between them is this: AI agents operating within sovereign commons communities should be governed by fork logic architecture. Not as a technical preference but as a governance requirement. A community that has built transparent, accountable, participatory governance of its land, credit, and civic life cannot coherently accept opaque, unaccountable, non-participatory AI reasoning in the tools it uses to administer that governance.

This is not a constraint on AI capability. It is a condition of democratic legitimacy. And it is technically achievable — incrementally, beginning now — with the architecture this document describes.

### The Temporal Reality

The Sovereign Commons is deployable today. ForkSC, as fully specified, requires components that are not yet built. The reasoning graph standard and self-reporting instrumentation are implementable now. The navigation interface and recomputation engine are engineering projects achievable within 12–18 months.

This temporal gap sequences the deployment rather than weakening the connection. In the immediate phase, the Commons Engine operates with conventional human-review protocols. As fork logic tooling matures, the Ward transitions its Commons Engine to fork logic architecture, gaining the reasoning transparency that democratic governance requires. The Human Review Mandate remains in force throughout both phases.

The Sovereign Commons and ForkSC are, at their foundation, the same document written at different scales. One governs the commons. The other governs the reasoning that helps the commons govern itself.

---

*ForkSC: A Human-Agent Reasoning Architecture — V1.2*
*March 2026*
*Open source · Authorless · Available to all · Owned by none*
*Companion document: The Sovereign Commons V2.5 — UK Reference Implementation*
