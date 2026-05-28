---
name: generate-reports
description: Fulfil all paid 108 storefront orders — generate each report via the section agents, render the PDF, upload to Supabase, mark delivered, and email the customer. Runs on demand and on schedule.
---

# /generate-reports — fulfil all paid orders

Process EVERY paid storefront order end-to-end. For each order: build the chart,
write each section with its specialist agent, stitch, render the PDF, upload it,
mark the order `ready`/`delivered`, and email the customer. Idempotent — skip
orders already `ready`/`delivered`.

All scripts live in `services/admin/`. Run from the repo root. Credentials load
automatically from `.env` + `.env.local`.

## Step 1 — find paid orders

```bash
uv run python services/admin/generate_v20_order.py --list-paid
```

Each line is `order_id<TAB>pack<TAB>name<TAB>email`. If it prints
`(no paid orders)`, report "nothing to fulfil" and stop. Otherwise process each
`order_id` below (do them one order at a time, all sections of an order in
parallel).

## Step 2 — per order: stage the section briefs

```bash
uv run python services/admin/stage_v20_prompts.py <order_id>
```

This writes one `<section>.prompt.txt` per section into
`docs/reports/v20_orders/order_<order_id>/prompts/` and prints the
section → agent mapping.

## Step 3 — per order: run every section agent IN PARALLEL

Spawn one Agent per section in a single message (concurrent). Use the
section → agent map below. Give each agent this task (substitute SECTION + AGENT
+ the absolute prompts dir `…/order_<order_id>/prompts/`):

> You are writing ONE section of a paid 108 Life Reading. Read the complete brief
> at `<dir>/<SECTION>.prompt.txt` (it holds the full chart data + your
> instructions) and follow it exactly. Write ONLY the finished narrative prose —
> no preamble, no meta-commentary, no section title/H2 header — to
> `<dir>/<SECTION>.response.md` using the Write tool. Reply "done: <SECTION> (N words)".

Section → agent (only spawn the sections the stage step actually produced; add-ons
vary by pack):

| section | agent |
|---|---|
| arc_so_far | 108-arc-historian |
| where_you_are_now | 108-current-chapter |
| answering_your_question | 108-question-answerer |
| next_12_months | 108-year-ahead |
| hidden_strengths | 108-yoga-interpreter |
| structural_challenges | 108-dosha-counselor |
| what_to_do_next | 108-action-strategist |
| sade_sati_deep_dive | 108-sade-sati |
| past_5_years | 108-past-decoder |
| next_5_years | 108-five-year-mapper |
| lifetime | 108-lifetime-cartographer |
| career_deep_dive | 108-career-specialist |
| wealth_deep_dive | 108-wealth-architect |
| relationships_deep_dive | 108-relationship-decoder |
| health_deep_dive | 108-health-mapper |
| spiritual_deep_dive | 108-spiritual-path |
| children_deep_dive | 108-children-decoder |
| education_deep_dive | 108-education-mapper |
| foreign_settlement | 108-foreign-pathfinder |
| property_vehicle | 108-property-timing |
| business_launch | 108-business-architect |
| muhurta_calendar | 108-muhurta-finder |
| gem_prescription | 108-gem-prescriber |

## Step 4 — per order: stage the stitcher prompt

```bash
REPORT_BACKEND=claude_code uv run python services/admin/generate_v20_order.py <order_id>
```

It reads all section responses and writes `stitcher.prompt.txt`, then exits with
`STITCHER PENDING`. (If any section response is missing it tells you which — re-run
that agent.)

## Step 5 — per order: run the stitcher agent

Spawn `108-stitcher` with: read `<dir>/stitcher.prompt.txt`, produce the cover
hook + closing CTA + one pull-quote per section in the brief's exact format, and
write it verbatim to `<dir>/stitcher.response.md`.

## Step 6 — per order: assemble, upload, email

```bash
REPORT_BACKEND=claude_code uv run python services/admin/generate_v20_order.py <order_id>
```

Now `stitcher.response.md` exists, so it renders the PDF, uploads to the
`los-reports` bucket, writes `los_reports`, marks the order `delivered`, and
emails the customer. Confirm the final line shows `status: delivered`.

## Step 7 — report

Summarise: orders processed, page counts, delivered vs failed, and any order left
in `generating` (needs a retry).

## Notes
- This is the **Claude Code subscription** path (no Anthropic API credits). When the
  API key is funded, set `REPORT_API_ENABLED=true` and run
  `REPORT_API_ENABLED=true uv run python services/admin/generate_v20_order.py <id>`
  for fully automated single-pass generation (no agents/stitcher staging needed).
- Safe to re-run: delivered orders won't reappear in `--list-paid`.
