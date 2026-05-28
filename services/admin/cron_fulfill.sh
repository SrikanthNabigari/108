#!/usr/bin/env bash
# 108 scheduled fulfillment (API path).
#
# Processes every paid storefront order via the Anthropic API generator.
# HARMLESS until BOTH are true:
#   1) REPORT_API_ENABLED=true is set in .env
#   2) the ANTHROPIC_API_KEY has credit
# Until then each invocation exits cheaply without touching orders.
#
# The Claude Code SUBSCRIPTION path (no API credits) is NOT run here — it needs
# a Claude Code session to fire the section agents. Run `/generate-reports`
# on demand for that.
#
# Installed in crontab every 15 min. Remove with: crontab -e (delete the line).
set -uo pipefail
export PATH="/home/ubuntu/.local/bin:$PATH"
ROOT=/home/ubuntu/projects/swarodaya/SWARODAYA/108-core
cd "$ROOT" || exit 1
LOG="$ROOT/docs/reports/v20_orders/cron.log"
mkdir -p "$(dirname "$LOG")"
echo "=== $(date -u +%FT%TZ) cron_fulfill start ===" >> "$LOG"
uv run python services/admin/generate_v20_order.py --list-paid 2>/dev/null | while IFS=$'\t' read -r oid _rest; do
  [ -n "$oid" ] || continue
  echo "-- order $oid" >> "$LOG"
  uv run python services/admin/generate_v20_order.py "$oid" >> "$LOG" 2>&1 || true
done
echo "=== $(date -u +%FT%TZ) cron_fulfill done ===" >> "$LOG"
