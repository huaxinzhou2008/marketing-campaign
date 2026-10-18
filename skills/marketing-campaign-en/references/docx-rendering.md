# Word Rendering: Template Requirements and Flow

Word must be rendered from structured JSON through a template — the model never typesets directly. In this environment that's done with the tencent-docx skill (route through tencent-docs-routing first).

## Rendering Flow

```
campaign_plan.json
  ↓ tencent-docs-routing picks the local document generation path
  ↓ tencent-docx generates (content source limited to campaign_plan.json)
  ↓ Fill cover, table of contents, body, tables, image placeholders, header/footer
  ↓ Output <campaign_name>.docx
```

## Template Requirements (confirm before generating, or confirm with the user)

- **Cover**: campaign name, brand, date;
- **Branded header**: Logo + brand name;
- **Branded footer**: confidentiality marking + page number;
- **Table of contents**: use Word's native Heading styles; the user refreshes with F9 after opening; page numbers are never hard-coded;
- **Image placeholders**: `{{IMAGE:hero}}`, `{{IMAGE:channel_banner}}` — kept as placeholder text until generation is confirmed;
- **Table styles**: budget, timeline, and KPI tables — three tables with styles locked up front to avoid typesetting drift across environments.

## Technical Notes (corresponds to Chapter 6 of the architecture)

- Template rendering with python-docx or docxtpl; in this environment, always go through tencent-docx while keeping the same principle;
- Header/footer are written via section.header / section.footer;
- Image placeholders are replaced by walking paragraphs and runs;
- The model only outputs JSON and never touches Word directly.

## Common Failures and Handling

| Failure | Handling |
|---|---|
| JSON validation failed | Return to Phase 5 and fix; do not enter rendering |
| User has no brand guidelines | Degrade header/footer to campaign name + page number; note it in the delivery notes |
| User wants PDF or another format | Still produce the docx first, then convert to the requested format |
| Images not yet confirmed | Keep placeholder text; do not call image-generation tools |
