# marketing-campaign

[中文版](README.md) | **English**

End-to-end marketing campaign planning Skill: from a brief, a multi-agent architecture drives research, copy, and visuals in parallel; after marketing-manager review (with bounce-backs) it emits structured JSON and renders a brand-templated Word document.

## Versions

This repo ships two language versions of the same skill — equivalent content, installed independently:

| Version | Skill name | Directory | Trigger language |
|---|---|---|---|
| English | `marketing-campaign-en` | `skills/marketing-campaign-en/` | English requests |
| Chinese | `marketing-campaign-zh` | `skills/marketing-campaign-zh/` | Chinese requests |

Installing both is safe — the skill names differ (`-en` / `-zh`), so each request language matches its own version.

## Install

```bash
# Install both versions (default)
npx -y skills add huaxinzhou2008/marketing-campaign -g --all

# English only
npx -y skills add huaxinzhou2008/marketing-campaign -g -s marketing-campaign-en

# Chinese only
npx -y skills add huaxinzhou2008/marketing-campaign -g -s marketing-campaign-zh
```

## What problem it solves

- Sequential campaign generation where research, copy, and visuals wait on each other, with no quality gate;
- Workflow logic coupled to tools, so swapping a tool means rewriting the flow;
- Models typesetting Word directly, so styles drift across environments;
- Image generation without a confirmation step, so prompts go off-target and quota is wasted.

## How it works

| Phase | Action |
|---|---|
| Phase 0 | Collect and validate the brief; ask before doing when key info is missing |
| Phase 1 | Initialize the shared `campaign_state.json` |
| Phase 2 | Launch Researcher / Writer / Image Designer sub-agents in parallel |
| Phase 3 | Route dependency requests (collab_request) |
| Phase 4 | Marketing manager review; failing work is bounced back, capped at 3 revision rounds |
| Phase 5 | Merge into `campaign_plan.json` and run schema validation |
| Phase 6 | Render Word from the brand template |
| Phase 7 | Images start as prompts and asset lists; generate only after confirmation |
| Phase 8 | Deliver Word + JSON + process notes |

Core invariants: the workflow never lives inside a tool; parallelism is controlled by the orchestrator; bidirectional communication flows only through shared state; Word can only be rendered from structured JSON; revision rounds are hard-capped at 3.

## Usage

After installing, start like this:

> Use $marketing-campaign-en to turn my marketing brief into a deliverable Word campaign plan.

A brief must include at least: product/service, campaign goal, target audience, and budget or timeline; brand guidelines are optional. For structure, see `skills/marketing-campaign-en/assets/brief.example.json`.

## Repository structure

```text
skills/
├── marketing-campaign-en/          English version
│   ├── SKILL.md                    Main entry: workflow, red lines, stopping conditions
│   ├── agents/openai.yaml          UI metadata
│   ├── references/
│   │   ├── campaign-state.md       Shared state, collaboration messages, state machine, review checklist
│   │   ├── output-schema.md        campaign_plan.json field spec
│   │   └── docx-rendering.md       Word template and rendering flow
│   ├── scripts/
│   │   └── validate_campaign_plan.py  Mandatory schema validator before rendering
│   └── assets/
│       └── brief.example.json      Reference structure for brief follow-up questions
└── marketing-campaign-zh/          Chinese version (equivalent content)
    ├── SKILL.md                    Main entry: workflow, red lines, stopping conditions
    ├── agents/openai.yaml          UI metadata
    ├── references/
    │   ├── campaign-state.md       Shared state, collaboration messages, state machine, review checklist
    │   ├── output-schema.md        campaign_plan.json field spec
    │   └── docx-rendering.md       Word template and rendering flow
    ├── scripts/
    │   └── validate_campaign_plan.py  Mandatory schema validator before rendering
    └── assets/
        └── brief.example.json      Reference structure for brief follow-up questions
```

## Runtime requirements

- A client that supports Agent Skills (e.g. WorkBuddy)
- Python 3 (to run `scripts/validate_campaign_plan.py`)

## Boundaries

Not handled: single-paragraph copy rewriting and polishing, pure typesetting beautification of existing plans, non-marketing documents (research reports, papers, contracts, etc.).

## Privacy and permissions

- This repo publishes only the files needed to run the Skill — no local eval samples, expected answers, or run logs;
- Search, CRM, and publishing tools require user authorization before use;
- Image prompts and asset lists must be confirmed by the user before any image is generated.
