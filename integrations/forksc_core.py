"""
ForkSC Core — Junction Graph Engine
Zero external dependencies. Import and run.

Usage:
    from forksc_core import JunctionGraph

    graph = JunctionGraph(session_id="my_agent_run")
    graph.add_junction({
        "junction_id": "j_001",
        "type": "definition_point",
        "stakes": "high",
        "description": "Framed the task as a classification problem rather than generation",
        "alternatives_held": [
            {"branch_id": "alt_001", "summary": "Frame as generation task", "weight_at_fork": 0.35}
        ],
        "confidence": 0.72,
        "reversibility": "expensive",
        "drift_delta": None
    })

    # After your agent run:
    graph.save("my_run.forksc.json")       # Persist the graph
    graph.print_tree()                      # Terminal visualisation
    graph.export_html("my_run.html")        # Browser visualisation

Schema: ForkSC V1.2 — https://github.com/ForkSC-Open/ForkSC
"""

import json
import datetime
from typing import Optional
from pathlib import Path


class Junction:
    """A single junction node in a fork logic reasoning graph."""

    VALID_TYPES = {"definition_point", "logic_junction", "inflection_point"}
    VALID_STAKES = {"low", "medium", "high", "critical"}
    VALID_REVERSIBILITY = {"clean", "partial", "expensive"}

    def __init__(self, data: dict, sequence_index: int, parent_id: Optional[str] = None):
        self.junction_id = data["junction_id"]
        self.type = data["type"]
        self.stakes = data.get("stakes", "medium")
        self.description = data.get("description", "")
        self.alternatives_held = data.get("alternatives_held", [])
        self.confidence = data.get("confidence", 0.5)
        self.reversibility = data.get("reversibility", "partial")
        self.drift_delta = data.get("drift_delta")
        self.timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.sequence_index = sequence_index
        self.parent_id = parent_id
        self.human_intervention = None

        self._validate()

    def _validate(self):
        assert self.type in self.VALID_TYPES, f"Invalid type: {self.type}"
        assert self.stakes in self.VALID_STAKES, f"Invalid stakes: {self.stakes}"
        assert self.reversibility in self.VALID_REVERSIBILITY, f"Invalid reversibility: {self.reversibility}"
        assert 0 <= self.confidence <= 1, f"Confidence must be 0-1, got {self.confidence}"
        if self.type == "logic_junction":
            assert len(self.alternatives_held) > 0, "logic_junction must have at least one alternative"
        if self.drift_delta is not None:
            assert 0 <= self.drift_delta <= 1, f"drift_delta must be 0-1, got {self.drift_delta}"

    def to_dict(self) -> dict:
        return {
            "junction_id": self.junction_id,
            "type": self.type,
            "stakes": self.stakes,
            "description": self.description,
            "alternatives_held": self.alternatives_held,
            "confidence": self.confidence,
            "reversibility": self.reversibility,
            "drift_delta": self.drift_delta,
            "position": {
                "sequence_index": self.sequence_index,
                "parent_junction_id": self.parent_id,
            },
            "timestamp": self.timestamp,
            "human_intervention": self.human_intervention,
        }

    @property
    def symbol(self) -> str:
        symbols = {
            "definition_point": "◆",
            "logic_junction": "◇",
            "inflection_point": "○",
        }
        return symbols.get(self.type, "?")

    @property
    def stakes_colour(self) -> str:
        colours = {"low": "32", "medium": "33", "high": "31", "critical": "35"}
        return colours.get(self.stakes, "37")


class JunctionGraph:
    """
    A fork logic reasoning graph.
    Accumulates junctions from an agent run, persists them, and renders them.
    """

    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.junctions: list[Junction] = []
        self.created = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def add_junction(self, data: dict, parent_id: Optional[str] = None) -> Junction:
        """Add a junction from agent structured output."""
        if parent_id is None and len(self.junctions) > 0:
            parent_id = self.junctions[-1].junction_id
        j = Junction(data, sequence_index=len(self.junctions), parent_id=parent_id)
        self.junctions.append(j)
        return j

    def add_from_agent_output(self, agent_response: str) -> Optional[Junction]:
        """
        Parse agent output containing a junction tag.
        Expects the agent to include a JSON block with a "junction" key.
        Returns the Junction if found, None if junction was null.
        """
        try:
            # Find JSON in agent output
            start = agent_response.find('{"junction"')
            if start == -1:
                # Try to find it with whitespace
                start = agent_response.find('"junction"')
                if start == -1:
                    return None
                # Walk back to find opening brace
                start = agent_response.rfind("{", 0, start)
                if start == -1:
                    return None

            # Find matching closing brace
            depth = 0
            end = start
            for i in range(start, len(agent_response)):
                if agent_response[i] == "{":
                    depth += 1
                elif agent_response[i] == "}":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break

            payload = json.loads(agent_response[start:end])
            junction_data = payload.get("junction")

            if junction_data is None:
                return None

            return self.add_junction(junction_data)

        except (json.JSONDecodeError, KeyError, AssertionError) as e:
            print(f"[ForkSC] Warning: Could not parse junction from agent output: {e}")
            return None

    def get(self, junction_id: str) -> Optional[Junction]:
        for j in self.junctions:
            if j.junction_id == junction_id:
                return j
        return None

    @property
    def definition_points(self) -> list[Junction]:
        return [j for j in self.junctions if j.type == "definition_point"]

    @property
    def logic_junctions(self) -> list[Junction]:
        return [j for j in self.junctions if j.type == "logic_junction"]

    @property
    def inflection_points(self) -> list[Junction]:
        return [j for j in self.junctions if j.type == "inflection_point"]

    @property
    def high_stakes(self) -> list[Junction]:
        return [j for j in self.junctions if j.stakes in ("high", "critical")]

    @property
    def low_confidence(self) -> list[Junction]:
        return [j for j in self.junctions if j.confidence < 0.5]

    @property
    def drifted(self) -> list[Junction]:
        return [j for j in self.junctions if j.drift_delta is not None and j.drift_delta > 0.3]

    # === Persistence ===

    def to_dict(self) -> dict:
        return {
            "forksc_version": "1.2",
            "session_id": self.session_id,
            "created": self.created,
            "junction_count": len(self.junctions),
            "junctions": [j.to_dict() for j in self.junctions],
        }

    def save(self, path: str):
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))
        print(f"[ForkSC] Graph saved: {path} ({len(self.junctions)} junctions)")

    @classmethod
    def load(cls, path: str) -> "JunctionGraph":
        data = json.loads(Path(path).read_text())
        graph = cls(session_id=data.get("session_id", "loaded"))
        for jd in data.get("junctions", []):
            graph.add_junction(jd, parent_id=jd.get("position", {}).get("parent_junction_id"))
        return graph

    # === Terminal Visualisation ===

    def print_tree(self):
        """Render the reasoning graph as a terminal tree."""
        if not self.junctions:
            print("[ForkSC] Empty graph.")
            return

        print(f"\n  ForkSC Reasoning Graph — {self.session_id}")
        print(f"  {'─' * 50}")

        for i, j in enumerate(self.junctions):
            colour = j.stakes_colour
            connector = "  ├── " if i < len(self.junctions) - 1 else "  └── "
            line = f"{connector}\033[{colour}m{j.symbol} {j.junction_id}\033[0m"
            line += f"  [{j.type}]  stakes:{j.stakes}  conf:{j.confidence:.2f}"

            if j.drift_delta is not None:
                line += f"  drift:{j.drift_delta:.2f}"

            print(line)

            # Description
            indent = "  │      " if i < len(self.junctions) - 1 else "         "
            if j.description:
                print(f"{indent}\033[90m{j.description}\033[0m")

            # Alternatives
            for alt in j.alternatives_held:
                print(f"{indent}\033[90m  ↳ [{alt['branch_id']}] {alt['summary']} (w:{alt['weight_at_fork']:.2f})\033[0m")

        print(f"  {'─' * 50}")

        # Summary line
        types = f"◆ {len(self.definition_points)} def  ◇ {len(self.logic_junctions)} logic  ○ {len(self.inflection_points)} inflection"
        flags = []
        if self.low_confidence:
            flags.append(f"{len(self.low_confidence)} low-conf")
        if self.drifted:
            flags.append(f"{len(self.drifted)} drifted")
        if self.high_stakes:
            flags.append(f"{len(self.high_stakes)} high-stakes")

        summary = f"  {types}"
        if flags:
            summary += f"  |  ⚠ {', '.join(flags)}"
        print(summary)
        print()

    # === HTML Visualisation ===

    def export_html(self, path: str):
        """Export a standalone HTML file with D3.js graph visualisation."""
        nodes_json = json.dumps([
            {
                "id": j.junction_id,
                "type": j.type,
                "stakes": j.stakes,
                "confidence": j.confidence,
                "description": j.description,
                "drift_delta": j.drift_delta,
                "alternatives": j.alternatives_held,
                "reversibility": j.reversibility,
            }
            for j in self.junctions
        ])

        edges_json = json.dumps([
            {"source": j.parent_id, "target": j.junction_id}
            for j in self.junctions
            if j.parent_id is not None
        ])

        html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>ForkSC — {self.session_id}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #0a0a0a; color: #e0e0e0; font-family: 'SF Mono', 'Fira Code', monospace; }}
  svg {{ width: 100vw; height: 100vh; }}
  .node {{ cursor: pointer; }}
  .node circle {{ stroke-width: 2px; }}
  .node text {{ font-size: 11px; fill: #888; }}
  .link {{ stroke: #333; stroke-width: 1.5px; fill: none; }}
  #panel {{ position: fixed; right: 0; top: 0; width: 360px; height: 100vh;
            background: #111; border-left: 1px solid #222; padding: 20px;
            overflow-y: auto; display: none; font-size: 13px; }}
  #panel h2 {{ color: #fff; margin-bottom: 12px; font-size: 15px; }}
  #panel .field {{ margin-bottom: 8px; }}
  #panel .label {{ color: #666; font-size: 11px; text-transform: uppercase; }}
  #panel .value {{ color: #ccc; }}
  #panel .alt {{ color: #555; margin-left: 12px; font-size: 12px; }}
  .type-definition_point {{ fill: #e74c3c; }}
  .type-logic_junction {{ fill: #3498db; }}
  .type-inflection_point {{ fill: #f39c12; }}
  .stakes-low {{ stroke: #2ecc71; }}
  .stakes-medium {{ stroke: #f1c40f; }}
  .stakes-high {{ stroke: #e74c3c; }}
  .stakes-critical {{ stroke: #8e44ad; }}
  #header {{ position: fixed; top: 16px; left: 20px; z-index: 10; }}
  #header h1 {{ font-size: 14px; color: #444; font-weight: normal; }}
  #legend {{ position: fixed; bottom: 16px; left: 20px; font-size: 11px; color: #444; }}
</style>
</head><body>
<div id="header"><h1>ForkSC — {self.session_id} — {len(self.junctions)} junctions</h1></div>
<div id="legend">
  <span style="color:#e74c3c">◆ definition</span> &nbsp;
  <span style="color:#3498db">◇ logic</span> &nbsp;
  <span style="color:#f39c12">○ inflection</span>
</div>
<svg></svg>
<div id="panel"></div>
<script>
const nodes = {nodes_json};
const edges = {edges_json};

const svg = d3.select("svg");
const width = window.innerWidth;
const height = window.innerHeight;

const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(edges).id(d => d.id).distance(120))
  .force("charge", d3.forceManyBody().strength(-400))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("y", d3.forceY().y((d, i) => 100 + i * 80).strength(0.3));

const link = svg.selectAll(".link")
  .data(edges).enter().append("line").attr("class", "link");

const node = svg.selectAll(".node")
  .data(nodes).enter().append("g").attr("class", "node")
  .call(d3.drag()
    .on("start", (e, d) => {{ if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }})
    .on("drag", (e, d) => {{ d.fx = e.x; d.fy = e.y; }})
    .on("end", (e, d) => {{ if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }}));

const radius = d => {{ const r = {{"low": 10, "medium": 14, "high": 18, "critical": 22}}; return r[d.stakes] || 14; }};

node.append("circle")
  .attr("r", d => radius(d))
  .attr("class", d => `type-${{d.type}} stakes-${{d.stakes}}`);

node.append("text")
  .attr("dx", d => radius(d) + 6).attr("dy", 4)
  .text(d => d.id);

node.on("click", (e, d) => {{
  const panel = document.getElementById("panel");
  panel.style.display = "block";
  let html = `<h2>${{d.id}}</h2>`;
  html += `<div class="field"><div class="label">Type</div><div class="value">${{d.type}}</div></div>`;
  html += `<div class="field"><div class="label">Stakes</div><div class="value">${{d.stakes}}</div></div>`;
  html += `<div class="field"><div class="label">Confidence</div><div class="value">${{d.confidence}}</div></div>`;
  html += `<div class="field"><div class="label">Reversibility</div><div class="value">${{d.reversibility}}</div></div>`;
  if (d.drift_delta !== null) html += `<div class="field"><div class="label">Drift</div><div class="value">${{d.drift_delta}}</div></div>`;
  html += `<div class="field"><div class="label">Description</div><div class="value">${{d.description}}</div></div>`;
  if (d.alternatives.length > 0) {{
    html += `<div class="field"><div class="label">Alternatives Held</div>`;
    d.alternatives.forEach(a => {{
      html += `<div class="alt">↳ [${{a.branch_id}}] ${{a.summary}} (w:${{a.weight_at_fork}})</div>`;
    }});
    html += `</div>`;
  }}
  panel.innerHTML = html;
}});

simulation.on("tick", () => {{
  link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
}});
</script>
</body></html>"""

        Path(path).write_text(html)
        print(f"[ForkSC] HTML graph exported: {path}")


# === Quick Demo ===

if __name__ == "__main__":
    g = JunctionGraph(session_id="demo_run")

    g.add_junction({
        "junction_id": "j_001",
        "type": "definition_point",
        "stakes": "critical",
        "description": "Framed user query as a policy analysis task rather than a factual lookup",
        "alternatives_held": [],
        "confidence": 0.68,
        "reversibility": "expensive",
        "drift_delta": None,
    })

    g.add_junction({
        "junction_id": "j_002",
        "type": "logic_junction",
        "stakes": "high",
        "description": "Chose to structure response around economic impact first, social impact second",
        "alternatives_held": [
            {"branch_id": "alt_001", "summary": "Lead with social impact, economic second", "weight_at_fork": 0.40},
            {"branch_id": "alt_002", "summary": "Interleave economic and social throughout", "weight_at_fork": 0.25},
        ],
        "confidence": 0.55,
        "reversibility": "partial",
        "drift_delta": None,
    })

    g.add_junction({
        "junction_id": "j_003",
        "type": "inflection_point",
        "stakes": "medium",
        "description": "Response shifted from analysing policy to advocating for a position",
        "alternatives_held": [],
        "confidence": 0.45,
        "reversibility": "clean",
        "drift_delta": 0.35,
    })

    g.print_tree()
    g.save("demo_run.forksc.json")
    g.export_html("demo_run.html")
