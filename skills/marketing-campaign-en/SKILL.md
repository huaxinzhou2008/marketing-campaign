---
name: marketing-campaign-en
description: End-to-end marketing campaign planning. From a brief, it runs a multi-agent workflow that advances research, copy, and visuals in parallel, routes cross-role dependencies through shared state, passes the marketing manager review loop (bounced back until it passes, max 3 revision rounds), emits a schema-validated structured JSON, and renders a brand-styled Word document. Use when the user asks for a marketing campaign plan, a product launch plan, or a promotion plan. Does not handle single-paragraph copy rewrites or pure typesetting beautification.
---

# Marketing Campaign Multi-Agent Workflow

## Task and Outputs

Turn the user's marketing brief into a deliverable, brand-styled Word campaign plan. Three fixed outputs:

1. `campaign_plan.json`: the schema-validated structured plan — the only allowed content source for Word;
2. The Word plan document: cover, table of contents, branded header/footer, image placeholders, clean tables;
3. Process artifacts: `campaign_state.json` and the collaboration log (for audit and traceability).

## Roles and Tool Mapping

The original architecture targets the OpenAI Agents SDK. When landing it in WorkBuddy, map it as follows — the behavioral contracts stay the same:

| Original role | Owner in this environment | Notes |
|---|---|---|
| Marketing Manager (orchestration + review) | Main Agent | Decomposes the brief, dispatches work, routes dependency requests, reviews and merges; never writes the three deliverables itself |
| Researcher / Writer / Image Designer | Sub-agents (parallel Agent tool calls) | Spawned in parallel in a single message; each writes only its own deliverable file |
| Shared campaign_state | `campaign_state.json` in the working directory | All roles read and write the same file; no passing messages through conversation |
| Collaboration message queue | `messages[]` in state + log file | Every collab_request is persisted |
| MCP Servers (web-search / crm / brand / knowledge / image-gen / docx-export) | Existing tools and skills | WebSearch, knowledge base, ImageGen, tencent-docx, etc. Self-hosted MCP Servers are not required, but keep the boundary of "one Server per capability class, 5-15 tools each" |
| mcp-docx-export | tencent-docx skill | Route through tencent-docs-routing first; template requirements in references/docx-rendering.md |

## Core Invariants (red lines — violating any one is failure)

1. The workflow never lives inside a tool; tools only connect to external capabilities.
2. Parallelism is controlled by the orchestrator; sub-agents never call each other directly, to avoid loops.
3. Bidirectional communication flows only through shared campaign_state and collaboration messages, never through private model chatter.
4. Word can only be rendered from structured JSON; the model never freely typesets it.
5. Revision rounds are hard-capped at 3 (`max_revision_rounds`); when the cap is hit, retrying must stop.
6. Images start as "prompt + asset list"; real generation happens only after user confirmation; until then keep the `{{IMAGE:xxx}}` placeholder.
7. Search, CRM, and publishing tools require user authorization before use.

## Workflow

### Phase 0 · Collect and validate the brief

Check whether the brief includes: product/service, campaign goal, target audience, budget or timeline, and brand guidelines (optional). When any of the first four is missing, ask the user before starting — do not assume. If the user gives only a sentence, ask follow-ups using the structure in assets/brief.example.json.

### Phase 1 · Initialize shared state

Create the working directory and write `campaign_state.json` (schema in references/campaign-state.md), set `status` to `researching` and `revision_round` to 0. Store the original brief in the `brief` field.

### Phase 2 · Launch three sub-agents in parallel

In a single message, call the Agent tool in parallel to spawn three sub-agents, each with a self-contained prompt (goal, input file paths, output file path, output format, prohibitions):

- **Researcher** → `research_summary.md`: industry, competitor, audience, and channel research; every conclusion carries a source or "assumption" tag; may use WebSearch and similar tools.
- **Writer** → `copy_package.md`: positioning, selling points, copy, content calendar, CTA; follows brand guidelines.
- **Image Designer** → `visual_package.md`: visual directions (≥3), asset list, image prompts; must not call image-generation tools — prompts only.

All three write files only (no long text replies); after reading the files, the main Agent registers their result paths in campaign_state.

### Phase 3 · Route dependency requests

Check each sub-agent's `open_questions` and the collab_requests in `messages[]` (e.g. the Writer asking the Image Designer for a hero visual style). The main Agent (Manager) decides: things that can wait for the Researcher's data, wait; things that can't, let the Writer / Designer ship a first version. Write routing decisions into `messages[]` and set `status` to `reviewing`.

### Phase 4 · Review and bounce back

The main Agent checks every item on the review checklist (references/campaign-state.md):

- Fail → set `status` to `revising`, increment `revision_round` by 1, bounce back only the smallest failing subtask to the right role; keep the rest of the work;
- `revision_round` reaches `max_revision_rounds` and still fails → stop retrying, proceed to Phase 5 with known defects, and flag the unresolved items in the final delivery notes;
- Pass → set `status` to `finalizing`.

### Phase 5 · Structured output and validation

Merge the three deliverables into `campaign_plan.json` (schema in references/output-schema.md), then always run:

```bash
python3 scripts/validate_campaign_plan.py <path to campaign_plan.json>
```

When validation fails, fix per the errors — never carry invalid JSON into rendering.

### Phase 6 · Word rendering

Route through tencent-docs-routing first to pick the local document generation path, then use tencent-docx. The only content source is `campaign_plan.json`; template and placeholder requirements are in references/docx-rendering.md. The model does not typeset directly.

### Phase 7 · Land the images

By default, keep the `{{IMAGE:hero}}` and `{{IMAGE:channel_banner}}` placeholders and deliver as-is. When the user explicitly wants real images: show the image prompts and asset list first → user confirms → only then call ImageGen to generate and replace the placeholders.

### Phase 8 · Deliver

Deliver the Word document + `campaign_plan.json`, plus a one-page process note: revision rounds, reasons for bounce-backs, unresolved items, data sources and assumptions.

## Stopping Conditions

- Brief key info is missing and the user hasn't filled it in: stop at Phase 0 and list what's still needed.
- Still failing after 3 revision rounds: stop retrying; either deliver with defects flagged, or ask the user to decide.
- The user changes requirements mid-flight: roll back to the affected phase, reset that part of the state, and never stack old and new state.
- No research tools available: degrade to model knowledge, tag every conclusion "assumption", and disclose it in the delivery notes.

## Adjacent Boundaries (out of scope)

- Single-paragraph copy rewriting, polishing, or headline ideation: this workflow doesn't apply.
- Beautifying the typesetting of an existing plan only: use tencent-docx's beauty_only.
- Non-marketing documents (research reports, papers, contracts, etc.): not this skill.

## Files and When to Read Them

| File | When to read / run |
|---|---|
| references/campaign-state.md | Phase 1 initialization, Phase 3 routing, Phase 4 review |
| references/output-schema.md | Phase 5 merge and output |
| references/docx-rendering.md | Phase 6 rendering |
| scripts/validate_campaign_plan.py | Must run during Phase 5 validation |
| assets/brief.example.json | When the brief is too thin, as the follow-up question structure |

## Risks and Boundaries (from Chapter 9 of the architecture)

- Parallelism does not mean unbounded calls; the max revision rounds are a hard gate.
- Image prompts must be confirmed before generation, to prevent drift and waste.
- Word template styles are locked up front; otherwise typesetting drifts across environments.
- External tools need a permission whitelist, especially search, CRM, and publishing.
