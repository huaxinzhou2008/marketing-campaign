# campaign_state: Shared State, Collaboration Messages, and Review Checklist

All roles exchange information through `campaign_state.json` in the working directory. No role may bypass this file to call another role directly.

## 1. State Schema

```json
{
  "status": "researching | writing | designing | reviewing | revising | finalizing",
  "brief": {},
  "research_summary": null,
  "copy_package": null,
  "visual_package": null,
  "open_questions": [],
  "revision_round": 0,
  "max_revision_rounds": 3,
  "messages": []
}
```

| Field | Rules |
|---|---|
| `status` | The single source of truth for the state machine; only the main Agent (Manager) may change it |
| `brief` | The user's original requirement; frozen once Phase 0 finalizes it |
| `research_summary` / `copy_package` / `visual_package` | Paths or content summaries of the three deliverables; each sub-agent writes only its own field |
| `open_questions` | Pending dependency questions; after the Manager routes one, clear it and write it into `messages[]` |
| `revision_round` / `max_revision_rounds` | Revision counter and hard cap of 3; the Manager owns both |
| `messages` | Append-only collaboration message log |

## 2. State Machine

```
researching ──┬──> writing ──┐
              ├──> designing ─┤
              │               ├──> reviewing ──pass──> finalizing
              └───────────────┘        │
                                       └──fail──> revising ──> reviewing (revision_round + 1)
```

- `revising` bounces back only the smallest failing subtask; work from roles that isn't bounced back is kept.
- Once `revision_round` reaches `max_revision_rounds`, entering `revising` again is forbidden — go to `finalizing` with defects flagged instead.

## 3. Collaboration Messages (collab_request)

```json
{
  "from": "writer",
  "to": "image_designer",
  "type": "request",
  "content": "Please provide 3 visual directions based on the 'high-value home projector' positioning.",
  "status": "pending"
}
```

- `type`: request / response / decision.
- `status`: pending → routed → resolved; advanced by the Manager.
- Every routing decision is logged (timestamp, from, to, rationale) for audit and retry.

## 4. Minimum Requirements for the Three Deliverables

**Researcher → `research_summary.md`**
- Four sections: market trends, competitor moves, audience insights, channel data;
- Every conclusion carries a source (URL / tool / knowledge base) or is explicitly tagged "assumption";
- Output `open_questions`: questions needing other roles or the user to confirm.

**Writer → `copy_package.md`**
- Positioning statement, core selling points (≤5), main copy, channel variants, content calendar, CTA;
- Follows brand guidelines (tone, forbidden words, voice);
- Flags which selling points depend on the Researcher's conclusions.

**Image Designer → `visual_package.md`**
- ≥3 visual directions, each with: direction name, style description, applicable channels, image prompts (one in English, one in Chinese);
- Asset list (Logo / product shots / real-life photos needed from the user);
- Calling image-generation tools at this stage is forbidden.

## 5. Review Checklist (Manager ticks every item)

Research line:
- [ ] Every conclusion has a source or "assumption" tag
- [ ] Competitors covered: ≥3
- [ ] Directly relevant to the campaign goal in the brief

Copy line:
- [ ] The positioning can be stated in one sentence
- [ ] Selling points are backed by research conclusions or explicit assumptions
- [ ] The CTA is concrete and actionable
- [ ] The tone matches brand guidelines

Visual line:
- [ ] ≥3 directions, none duplicated
- [ ] Prompts are executable (subject, style, composition, aspect ratio all present)
- [ ] Visual directions match the copy positioning

Overall:
- [ ] Budget, timeline, and KPIs are mutually consistent
- [ ] No un-routed collab_request remains

Any failed item → bounce back to the right role; update `campaign_state.json` before retrying.
