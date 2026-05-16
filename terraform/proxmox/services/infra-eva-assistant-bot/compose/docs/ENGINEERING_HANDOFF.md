# EVA Assistant Bot — Engineering Handoff

**Last updated:** May 2026  
**Status:** Production — Proxmox homelab, 192.168.1.122  
**Public endpoint:** https://infra-eva.mailerblend.com  

---

## What is EVA?

EVA is a personal Telegram assistant bot that manages reminders, tasks, and content ideas. It uses Claude Haiku (Anthropic) to understand natural language, stores everything in PostgreSQL, and syncs bidirectionally with Focalboard (kanban board UI).

It runs as a set of Docker containers on a self-hosted Proxmox server behind a dynamic home IP. DNS is managed via Cloudflare.

---

## Architecture Overview

```
Telegram User
     │
     ▼ POST /telegram/webhook
┌─────────────────────┐
│     nginx (host)    │ ← reverse proxy, port 443 → 8001
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│    eva-api           │ FastAPI, uvicorn, port 8000 (internal)
│  (main.py +         │
│   api/ routes)      │
└──┬──────────────────┘
   │         │              │
   ▼         ▼              ▼
PostgreSQL  Focalboard   Anthropic API
(eva-postgres) (focalboard)  (Claude Haiku)

┌─────────────────────┐
│  eva-scheduler      │ ← runs run_scheduler.py, polls every 30s
└─────────────────────┘
┌─────────────────────┐
│  eva-sync           │ ← runs sync_service.py, polls every 60s
└─────────────────────┘
┌─────────────────────┐
│  eva-cron-digest    │ ← alpine cron, hits POST /digest/send at 08:00
└─────────────────────┘
```

---

## Folder Structure

```
compose/api/                   ← everything that runs inside the container at /app/
  main.py                      ← FastAPI app factory + router registration ONLY
  
  core/
    config.py                  ← ALL env vars and constants (single source of truth)
  
  utils/
    time_utils.py              ← to_local(), serialize_reminder(), serialize_event()
    text_utils.py              ← normalize_text(), is_list_command(), _parse_snooze(),
                                  extract_pending_task(), build_help_text(), etc.
  
  integrations/
    anthropic_client.py        ← ALL Anthropic HTTP (auth, model, timeout, parsing)
    focalboard_client.py       ← ALL Focalboard HTTP (create/update/delete/get cards)
    telegram_client.py         ← ALL Telegram HTTP (send, getFile, download)
  
  repositories/
    reminder_repository.py     ← ALL SQLAlchemy queries for Reminder model
    message_repository.py      ← ALL SQLAlchemy queries for Message model
    event_repository.py        ← ALL SQLAlchemy queries for Event model
    user_repository.py         ← ALL SQLAlchemy queries for User model
  
  services/
    reminder_handlers.py       ← business logic: ACK, cancel, snooze, edit, note, list
    content_handlers.py        ← business logic: content ideas, undated tasks
  
  api/
    health_routes.py           ← GET /, /health, /ready
    reminder_routes.py         ← GET /reminders, /tasks, POST /commands/parse
    event_routes.py            ← GET/POST /events
    task_routes.py             ← GET/PATCH /tasks/*, link-card, by-card, duplicate
    attachment_routes.py       ← POST/GET/DELETE /tasks/{id}/attachments/*
    digest_routes.py           ← POST /digest/send, GET /digest/preview/{id}
    telegram_routes.py         ← POST /telegram/webhook + _handle_photo_message
    admin_routes.py            ← POST /admin/backfill-dates
  
  ai_parser.py                 ← intent detection, reminder parsing, confirmation,
                                  Q&A, chat reply, daily briefing, priority inference
  scheduler.py                 ← next_occurrence(), build_due_text_ai(), digest logic
  run_scheduler.py             ← main loop (every 30s): fire reminders, retry, reschedule
  sync_service.py              ← EVA ↔ Focalboard bidirectional sync (every 60s)
  
  auth.py                      ← JWT auth for web UI users
  users.py                     ← CRUD for eva_users table
  publishing_channels.py       ← publishing channel management + undated-tasks endpoints
  undated_tasks_reminder.py    ← stale task detection and alerting logic
  memory_service.py            ← user facts extraction and retrieval
  persona_service.py           ← loads Blazer1x.json, builds system prompts
  parser_service.py            ← regex-based reminder parser (fallback to AI)
  telegram_service.py          ← backward-compat wrapper over telegram_client
  db.py                        ← SQLAlchemy engine + SessionLocal
  models.py                    ← all SQLAlchemy models
```

---

## Module Responsibilities

### `core/config.py`
Single source of truth for every environment variable and constant.  
**To add a new env var or Focalboard property ID → only edit this file.**

### `integrations/`
Each client owns 100% of HTTP communication with one external service.  
Rules: no business logic, no DB access, no httpx calls outside these files.

| Client | Owns |
|---|---|
| `anthropic_client.py` | API URL, auth headers, model name, timeout, response extraction |
| `focalboard_client.py` | Board URLs, CSRF headers, card create/update/delete/list |
| `telegram_client.py` | Bot token, sendMessage, getFile, downloadFile |

### `repositories/`
Each repository owns all SQL queries for one model.  
Rules: no HTTP calls, no business logic, no commits (callers commit), receives `db` as argument.

### `services/`
Business logic that orchestrates repositories + integrations + Telegram messaging.  
Rules: no FastAPI imports, no route decorators, no direct HTTP calls to external APIs.

### `api/`
FastAPI router modules — route definitions and request/response handling only.  
Rules: no business logic, no direct DB queries, delegates to services/repositories.

---

## Request Flow — Telegram Webhook

```
Telegram → POST /telegram/webhook
  │
  ├─ Photo? → _handle_photo_message()
  │     └─ tg.get_file() + tg.download_file()  [telegram_client]
  │     └─ fb.create_card()                     [focalboard_client]
  │     └─ POST /tasks/{id}/attachments         [self API call]
  │
  └─ Text message:
        │
        ├─ #contenido tag? → handle_content_idea()   [content_handlers]
        ├─ Bare URL?       → handle_pending_task()   [content_handlers]
        ├─ "listo"/"ok"?   → handle_ack_command()    [reminder_handlers]
        ├─ "cancela el N"? → handle_cancel_by_id()   [reminder_handlers]
        ├─ "lista"?        → handle_list_command()   [reminder_handlers]
        │
        └─ LLM intent detection (detect_intent via anthropic_client)
              │
              ├─ create_reminder → parse_reminder_ai() → save → confirm
              ├─ cancel_reminder → handle_cancel_command()
              ├─ edit_reminder   → handle_edit_reminder()
              ├─ question        → answer_question_ai()
              ├─ pending_task    → handle_pending_task()
              ├─ chat            → chat_reply_ai()
              └─ unknown         → chat_reply_ai() or help_text
```

### Reminder Lifecycle

```
User message
  → parse_reminder_ai() [anthropic_client → Claude tool_use]
  → Reminder saved (status=scheduled, remind_at=future)
  → Focalboard card created by eva-sync [focalboard_client]
  
Every 30s (eva-scheduler):
  → remind_at <= now?
  → build_due_text_ai() [anthropic_client → humanize text]
  → send_message() [telegram_client]
  → status = sent
  
  If persistent (repeat_every_minutes):
    → awaiting_ack = True
    → retry every N minutes until stop_at or "listo"
  
User replies "listo":
  → handle_ack_command() [reminder_handlers]
  → If recurrent: next_occurrence() → status=scheduled, remind_at=next
  → If one-shot:  status=completed, focalboard_synced_at=now
  
EVA sync (every 60s):
  → sync_status_changes(): push completed/cancelled to Focalboard
  → sync_from_focalboard(): pull status/date changes from Focalboard UI
  → sync_recurring_dates(): update Focalboard date prop for recurring reminders
```

### Focalboard Sync Flow

```
eva-sync (sync_service.py, every 60s):
  │
  ├─ sync_new_reminders()
  │   └─ Reminders without focalboard_card_id → fb.create_card()
  │
  ├─ sync_status_changes()
  │   └─ Reminders with status=sent/completed/cancelled/expired
  │   └─ → fb.update_card_properties() (push to Focalboard)
  │
  ├─ sync_from_focalboard()
  │   └─ fb.get_cards_since(last_poll) → cards changed in Focalboard
  │   └─ Status change → update reminder.status + Telegram notification
  │   └─ Date change → update reminder.remind_at
  │   └─ Title change → update reminder.task_text
  │
  └─ sync_recurring_dates()
      └─ Recurring/persistent reminders → update Focalboard date prop
```

**Anti-loop protection:** `focalboard_synced_at` timestamp. If a reminder was modified in EVA less than 5 minutes ago (ACK, cancel, etc.), the sync skips it — preventing Focalboard from overwriting the change before it propagates.

### Scheduler Flow (every 30s)

```
run_scheduler.py → main_loop():
  1. process_reminders()         ← fire due, retry persistent, reschedule recurrent
  2. process_daily_digest()      ← 08:00 → POST /digest/send
  3. process_content_reminders() ← 20:00 → content publication reminders
  4. process_publishing_reminders() ← 09:00 → channel publishing reminders
  5. process_undated_tasks()     ← 09:30 → stale task alerts
  sleep(30s)
```

### Attachment Flow

```
User sends photo to Telegram
  → _handle_photo_message() [telegram_routes.py]
  → tg.get_file(file_id) → file_path
  → tg.download_file(file_path) → bytes
  → fb.create_card() → card_id
  → Reminder created in DB with focalboard_card_id
  → POST /tasks/{reminder_id}/attachments (self call)
  → File saved to /app/uploads/{id}_{uuid}.{ext}
  → task_attachments row created in DB
```

---

## Docker Compose Services

| Container | Image | Purpose | Poll |
|---|---|---|---|
| `eva-postgres` | postgres:16-alpine | Database | — |
| `eva-api` | eva-backend:latest | FastAPI webhook + REST API | — |
| `eva-scheduler` | eva-backend:latest | Fires reminders, retries, reschedules | 30s |
| `eva-sync` | eva-backend:latest | Bidirectional Focalboard sync | 60s |
| `eva-cron-digest` | alpine | Cron → POST /digest/send at 08:00 | daily |
| `focalboard` | mattermost/focalboard | Kanban UI | — |
| `eva-docker-cleanup` | docker:cli | Weekly Docker prune | weekly |

All containers share `eva-network` (bridge). Internal communication uses container names as hostnames (e.g. `http://focalboard:8000`, `http://eva-api:8000`).

---

## Environment Variables

All read in `core/config.py`. Critical ones:

| Variable | Purpose |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API auth |
| `ANTHROPIC_API_KEY` | Claude Haiku API auth |
| `FOCALBOARD_TOKEN` | Focalboard API auth |
| `FOCALBOARD_BOARD_ID` | Tasks board ID |
| `FOCALBOARD_CONTENT_BOARD_ID` | Content ideas board ID |
| `POSTGRES_DB/USER/PASSWORD` | Database credentials |
| `EVA_AI_PARSER` | Enable/disable LLM parser (default: 1) |
| `TIMEZONE` | App timezone (default: Europe/Madrid) |
| `EVA_UI_URL` | UI URL for Telegram notifications (default: https://eva-flow.lovable.app) |
| `SELF_API_URL` | Internal API URL for self-calls (default: http://localhost:8000) |
| `UPLOADS_DIR` | Attachment storage path (default: /app/uploads) |

---

## Focalboard Property IDs

These are hardcoded in `core/config.py`. They are fixed UUIDs assigned when the board was created. **Do not change them** — they map directly to Focalboard's internal schema.

**Tasks board** (`FOCALBOARD_BOARD_ID`):
- `aevastatus00000000000000001` — Status property
- `ann9q8kbmc67mb7p4d8xrmma6rr` — Priority
- `a14y4uzprb1maieayt1ouhca47o` — Date
- `a6bxuk4rgxp7wn6bashiadwaiiy` — Notes/Text
- `asztuket5mjeeongrzooyx5utbo` — URL

**To add a new project tag** (e.g. `#newtag`):
1. Edit `CONTENT_PROYECTO_MAP` in `core/config.py`
2. Tell Lovable UI the new option ID
3. No DB migration needed

---

## Persona System

Loaded from `/app/persona/{username}.json` (e.g. `Blazer1x.json`).  
Controls: tone, language dialect, greeting phrases, personality notes.  
This file is volume-mounted read-only from the host.

**To change EVA's personality** → edit the JSON file on the host, restart `eva-api`.

---

## Debugging by Feature

| Problem | First place to look |
|---|---|
| EVA doesn't respond to Telegram | `docker logs eva-api` — check webhook receipt |
| Wrong intent detected | `ai_parser.py` → `detect_intent()` |
| Reminder not firing | `docker logs eva-scheduler` — check `process_reminders()` |
| Reminder fires at wrong time | `scheduler.py` → `next_occurrence()` |
| Focalboard card not created | `docker logs eva-sync` — check `sync_new_reminders()` |
| Focalboard sync loop bug | `sync_service.py` → `focalboard_synced_at` anti-loop logic |
| Attachment not saved | `api/attachment_routes.py` → `upload_attachment()` |
| Content idea wrong board | `services/content_handlers.py` → `handle_content_idea()` |
| ACK not completing reminder | `services/reminder_handlers.py` → `handle_ack_command()` |
| Snooze not working | `services/reminder_handlers.py` → `_parse_snooze()` |
| Anthropic timeout | `integrations/anthropic_client.py` → `TIMEOUT` constant |
| Focalboard auth error | `integrations/focalboard_client.py` → `_headers()` |
| Wrong property IDs | `core/config.py` → property ID constants |
| DB query slow or wrong | `repositories/{entity}_repository.py` |
| Daily digest not sent | `docker logs eva-cron-digest` + `docker logs eva-api` |
| Undated task alerts not firing | `undated_tasks_reminder.py` → `_should_alert_today()` |
| IP changed, webhook broken | Update Cloudflare DNS + re-run `setWebhook` curl command |

---

## Common Failure Points

### 1. Home IP changes
The server has a dynamic public IP. When it changes, `infra-eva.mailerblend.com` stops resolving correctly and Telegram webhook gets `Connection timed out`.

**Detection:** `getWebhookInfo` shows `last_error_message: "Connection timed out"`  
**Fix:** Update Cloudflare A record + re-register webhook:
```bash
TOKEN=$(grep TELEGRAM_BOT_TOKEN compose/.env | cut -d= -f2)
curl "https://api.telegram.org/bot${TOKEN}/setWebhook?url=https://infra-eva.mailerblend.com/telegram/webhook"
```

### 2. Focalboard sync loop
If `focalboard_synced_at` is stale (e.g. after a crash), `sync_from_focalboard` can overwrite a reminder the user just ACK'd, re-triggering it.

**Detection:** Reminder fires repeatedly after user says "listo"  
**Fix:** Set `focalboard_synced_at = now` when ACKing — already implemented in `reminder_handlers.py`

### 3. Persistent reminder past stop_at
If `stop_at` is from a previous day and `remind_at` was snoozed, the scheduler may expire the reminder immediately on the next cycle.

**Detection:** Reminder expires instantly after snooze  
**Mitigation:** `stop_is_today_or_future` check in `run_scheduler.py`

### 4. Container clock drift
All containers mount `/etc/localtime` and `/etc/timezone` from host. If the host clock drifts, reminders fire at wrong times.

**Fix:** `chrony` or `ntpd` on the Proxmox host.

### 5. Focalboard v7.8.9 healthcheck
Focalboard doesn't have `/ping`. The compose uses `/api/v2/teams` with `X-Requested-With` header instead. `eva-sync` uses `service_started` (not `service_healthy`) to avoid blocking.

---

## Known Architecture Debt

| Area | Issue | Risk |
|---|---|---|
| `sync_service.py` | Still uses `select()` directly (not through repositories) | Low — isolated module |
| `run_scheduler.py` | Direct DB queries not behind repositories | Medium — fragile if models change |
| `scheduler.py` | `build_due_text_ai()` has persona loading inline | Low |
| `publishing_channels.py` | Mixes route definitions with business logic | Low |
| Duplicate content routing | `#contenido` tag check duplicated in `telegram_routes.py` | Low |

---

## Migrations

SQL migrations in `compose/postgres/migrations/`. Applied in order 001→015.  
Currently applied: 001–015.

**To apply a new migration:**
```bash
scp 016-new-feature.sql root@192.168.1.122:/tmp/
ssh root@192.168.1.122 "docker cp /tmp/016-new-feature.sql eva-postgres:/tmp/ && \
  docker exec eva-postgres psql -U eva -d eva -f /tmp/016-new-feature.sql"
```

---

## Deploy Procedure

```bash
# Full deploy (build + rsync + restart)
./services/infra-eva-assistant-bot/deploy-eva-assistant-bot.sh

# Restart without rebuild (config/env change only)
ssh root@192.168.1.122 "cd /opt/infra-eva-assistant-bot && docker compose restart eva-api"

# Force clean rebuild
ssh root@192.168.1.122 "cd /opt/infra-eva-assistant-bot && \
  docker rmi eva-backend:latest --force && \
  docker compose build --no-cache eva-api && \
  docker compose up -d"

# View logs
ssh root@192.168.1.122 "docker logs eva-api --tail=30 2>&1"
ssh root@192.168.1.122 "docker logs eva-scheduler --tail=20 2>&1"
ssh root@192.168.1.122 "docker logs eva-sync --tail=20 2>&1"
```

---

## Smoke Tests

```bash
./services/infra-eva-assistant-bot/tests/smoke_test.sh
# 16 tests covering: health, ready, reminders, tasks, webhook,
# parser, publishing, auth, events, 404 handling
```

Run after every deploy. Exit code 0 = safe to promote.

---

## Future Work / Safe Extension Points

| Feature | Where to add it |
|---|---|
| New Telegram command | `utils/text_utils.py` (detection) + `services/reminder_handlers.py` (logic) |
| New Focalboard board | `core/config.py` (constants) + `integrations/focalboard_client.py` (if new endpoints) |
| New reminder type | `scheduler.py` → `next_occurrence()` + `repositories/reminder_repository.py` |
| New project tag (#X) | `core/config.py` → `CONTENT_PROYECTO_MAP` |
| New publishing channel | `publishing_channels.py` |
| Replace Focalboard | Only touch `integrations/focalboard_client.py` + `sync_service.py` |
| Replace Anthropic model | Only touch `integrations/anthropic_client.py` → `MODEL` constant |
| New UI route | `api/` folder — new file or extend existing |
| New DB table | `models.py` + migration + new `repositories/` file |

---

## Key Architectural Decisions

**Why keep `sync_service.py` separate from `eva-api`?**  
Sync runs in its own container (`eva-sync`) so a sync crash never affects the API. They share the same Docker image but different entrypoints.

**Why `focalboard_synced_at` instead of a queue?**  
Lightweight anti-loop mechanism. A write queue would require Redis or similar. The 5-minute window is sufficient for the 60s poll cycle.

**Why is the webhook handler still long (telegram_routes.py)?**  
The intent decision tree has many branches that need to be evaluated in order. Splitting it further risks introducing bugs at the decision boundaries. The services layer already extracted the business logic — the remaining code is pure routing logic.

**Why `parser_service.py` (regex) alongside `ai_parser.py` (LLM)?**  
Regex parser is the fallback when `EVA_AI_PARSER=0` or when the API is down. Never remove it.

**Why not use Alembic for migrations?**  
Manual SQL migrations are simpler for a single-developer homelab project. The risk of schema drift is low when there's one developer and one environment.