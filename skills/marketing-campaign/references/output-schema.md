# campaign_plan.json: Final Output Schema

The single structured plan the marketing manager (main Agent) produces by merging the three deliverables — and the only content source for Word rendering.

## Schema

```json
{
  "campaign_name": "",
  "brand": "",
  "objective": "",
  "target_audience": "",
  "insights": [],
  "positioning": "",
  "channels": [],
  "copy_package": {},
  "visual_package": {},
  "budget_table": [],
  "timeline": [],
  "kpis": [],
  "risks": [],
  "next_steps": [],
  "images": {
    "hero": "path/to/hero.png",
    "channel_banner": "path/to/banner.png"
  }
}
```

## Field Reference

| Field | Type | Requirements |
|---|---|---|
| `campaign_name` | string | Campaign name, max 20 characters |
| `brand` | string | Brand name; "Not specified" when unknown |
| `objective` | string | Campaign goal, one sentence |
| `target_audience` | string | Target audience description |
| `insights` | array\<string\> | Key insights, 3-7 items; from research_summary |
| `positioning` | string | Positioning statement, one sentence |
| `channels` | array\<string\> | Channels to run on |
| `copy_package` | object | Copy package: main copy, channel variants, CTA, content calendar |
| `visual_package` | object | Visual package: directions, prompts, asset list |
| `budget_table` | array\<object\> | Budget: item, amount, ratio; ratios must sum to 100% |
| `timeline` | array\<object\> | Timeline: phase, start/end, owning role |
| `kpis` | array\<object\> | KPI: metric, target, how it's measured |
| `risks` | array\<string\> | Risks and mitigations, 2-5 items |
| `next_steps` | array\<string\> | Next actions, actionable |
| `images` | object | Image path map; when no real images are generated yet, keep `{{IMAGE:hero}}`-style placeholder strings |

## Validation

After merging, always run:

```bash
python3 scripts/validate_campaign_plan.py <path to campaign_plan.json>
```

What it checks: required fields present, correct types, `insights`/`channels`/`risks`/`next_steps` non-empty, `budget_table` ratios summing to ~100%, and `images` containing both `hero` and `channel_banner` keys.

When validation fails, fix per the errors — skipping validation and rendering Word directly is forbidden.
