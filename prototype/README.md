# Prototype

Reference implementation of the ForkSC navigation interface and simulated recomputation engine.

**Status:** In development. See Appendix D of the specification (`/spec/FORKSC.md`) for the build brief and success criteria.

**Tech Stack:** Single-file React artifact, D3.js force-directed graph layout, Tailwind CSS, language model API for simulated recomputation. No backend.

**Target:** A working demonstration that satisfies both success criteria:

- Non-technical users understand that AI reasoning has visible, explorable structure.
- Technical users understand that redirecting from a junction preserves upstream KV-cache state and regenerates only downstream tokens.

Contributions welcome. Build against the junction tag schema at `/schemas/junction_tag.schema.json`.
