.PHONY: help doctor sb-check report-api report-cc report-cc-parallel render \
        web-dev web-build web-deploy web-preview \
        agents-upgrade test lint format clean

# Default target
help:
	@echo "108 — Life's Operating System · Make targets"
	@echo
	@echo "── Environment ──────────────────────────────────"
	@echo "  make doctor             Check all env vars and connectivity"
	@echo "  make sb-check           Verify Supabase connection + tables"
	@echo
	@echo "── Report generation ───────────────────────────"
	@echo "  make report-api         Generate via Anthropic API SDK"
	@echo "                          (needs ANTHROPIC_API_KEY)"
	@echo "  make report-cc          Generate via Claude Code subscription"
	@echo "                          (uses staged prompts + Agent tool)"
	@echo "  make report-cc-parallel Fire all section agents in parallel"
	@echo "  make render PDF=path.pdf MD=path.md"
	@echo "                          Render an existing markdown to PDF"
	@echo
	@echo "── Frontend (Next.js → Vercel) ─────────────────"
	@echo "  make web-dev            Local dev server (apps/web)"
	@echo "  make web-build          Production build"
	@echo "  make web-deploy         Deploy to 108-los.vercel.app"
	@echo "  make web-preview        Vercel preview deploy"
	@echo
	@echo "── Maintenance ─────────────────────────────────"
	@echo "  make agents-upgrade     Re-confirm all section agents on Sonnet 4.6"
	@echo "                          and stitcher on Opus 4.7"
	@echo "  make test               uv run pytest"
	@echo "  make lint               uv run ruff check ."
	@echo "  make format             uv run ruff format ."
	@echo "  make clean              Remove __pycache__ and node_modules"

# ── Environment ──
doctor:
	@echo "── Backend env ──"
	@set -a; [ -f .env.local ] && . ./.env.local; set +a; \
	  for v in SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY ANTHROPIC_API_KEY \
	           RAZORPAY_KEY_ID PAYU_MERCHANT_KEY CASHFREE_APP_ID \
	           SMTP_HOST SMTP_USER GOOGLE_PLACES_API_KEY; do \
	    val="$$(eval echo \$$$$v)"; \
	    if [ -z "$$val" ]; then printf "  %-32s ❌ unset\n" "$$v"; \
	    else printf "  %-32s ✅ set\n" "$$v"; fi; \
	  done
	@echo
	@echo "── Python ──"
	@uv run python --version
	@echo
	@echo "── Supabase ──"
	@$(MAKE) -s sb-check || true

sb-check:
	@set -a; . ./.env.local; set +a; \
	curl -s -o /dev/null -w "  Supabase REST → HTTP %{http_code}\n" \
	  -H "apikey: $$SUPABASE_SERVICE_ROLE_KEY" \
	  -H "Authorization: Bearer $$SUPABASE_SERVICE_ROLE_KEY" \
	  "$$SUPABASE_URL/rest/v1/los_orders?select=id&limit=1"

# ── Report generation ──
# REPORT_NARRATIVE_BACKEND = api | claude_code
report-api:
	@echo "→ Anthropic API SDK mode"
	REPORT_NARRATIVE_BACKEND=api uv run python services/admin/process_reports.py

report-cc:
	@echo "→ Claude Code subscription mode (sequential)"
	REPORT_NARRATIVE_BACKEND=claude_code uv run python services/admin/process_reports.py

report-cc-parallel:
	@echo "→ Claude Code subscription mode (parallel via Agent tool)"
	REPORT_NARRATIVE_BACKEND=claude_code REPORT_PARALLEL=1 \
	  uv run python services/admin/process_reports.py

render:
	@if [ -z "$(MD)" ] || [ -z "$(PDF)" ]; then \
	  echo "usage: make render MD=path/to.md PDF=path/to.pdf"; exit 1; \
	fi
	uv run python -c "from packages.report.src.render import render_report_pdf; \
	  render_report_pdf('$(MD)', '$(PDF)')"

# ── Frontend ──
web-dev:
	cd apps/web && npm install --silent && npm run dev

web-build:
	cd apps/web && npm install --silent && npm run build

web-deploy:
	cd apps/web && npx vercel --prod --yes

web-preview:
	cd apps/web && npx vercel --yes

# ── Maintenance ──
agents-upgrade:
	@echo "Upgrading section agents → claude-sonnet-4-6"
	@for f in .claude/agents/108-*.md; do \
	  if [ "$$(basename $$f)" != "108-stitcher.md" ]; then \
	    sed -i.bak 's|^model:.*|model: claude-sonnet-4-6|' "$$f" && rm -f "$$f.bak"; \
	  fi; \
	done
	@echo "Upgrading stitcher → claude-opus-4-7"
	@sed -i.bak 's|^model:.*|model: claude-opus-4-7|' .claude/agents/108-stitcher.md && rm -f .claude/agents/108-stitcher.md.bak
	@echo "✓ done"

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name node_modules -prune -exec rm -rf {} +
	find . -type d -name .next -prune -exec rm -rf {} +
	find . -type d -name .turbo -prune -exec rm -rf {} +
