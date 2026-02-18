# 🚀 INSTALACIÓN DE ROUTERS NUEVOS

## Archivos a copiar

Copiar estos 4 archivos a:
`services/infra-composable-crm/api/app/routers/v1/`

1. `linkedin_knowledge_base.py`
2. `linkedin_rate_limits.py`
3. `linkedin_activity_log.py`
4. `linkedin_cooldowns.py`

---

## Registrar routers en main.py

Editar `services/infra-composable-crm/api/app/main.py`:

```python
# ── Imports (añadir al bloque existente) ──
from app.routers.v1.linkedin_knowledge_base import router as knowledge_base_router
from app.routers.v1.linkedin_rate_limits import router as rate_limits_router
from app.routers.v1.linkedin_activity_log import router as activity_log_router
from app.routers.v1.linkedin_cooldowns import router as cooldowns_router

# ── Registrar routers (añadir después de los routers existentes) ──
app.include_router(knowledge_base_router)
app.include_router(rate_limits_router)
app.include_router(activity_log_router)
app.include_router(cooldowns_router)
```

---

## Reiniciar API

```bash
cd services/infra-composable-crm
docker-compose restart api

# Verificar logs
docker-compose logs -f api
```

---

## Endpoints disponibles después de instalar

### 📚 Knowledge Base
```
POST   /v1/linkedin-sourcing/knowledge-base
GET    /v1/linkedin-sourcing/knowledge-base
GET    /v1/linkedin-sourcing/knowledge-base/context/{pack}
GET    /v1/linkedin-sourcing/knowledge-base/{entry_id}
PATCH  /v1/linkedin-sourcing/knowledge-base/{entry_id}
DELETE /v1/linkedin-sourcing/knowledge-base/{entry_id}
```

### 🎯 Rate Limits
```
GET   /v1/linkedin-sourcing/rate-limits
GET   /v1/linkedin-sourcing/rate-limits/{limit_type}
PATCH /v1/linkedin-sourcing/rate-limits/{limit_type}
GET   /v1/linkedin-sourcing/rate-limits/current/status
```

### 📊 Activity Log
```
POST   /v1/linkedin-sourcing/activity-log
GET    /v1/linkedin-sourcing/activity-log
GET    /v1/linkedin-sourcing/activity-log/stats/daily
GET    /v1/linkedin-sourcing/activity-log/stats/today
DELETE /v1/linkedin-sourcing/activity-log/cleanup
```

### ⏸️ Cooldowns
```
GET   /v1/linkedin-sourcing/cooldowns/status
POST  /v1/linkedin-sourcing/cooldowns
GET   /v1/linkedin-sourcing/cooldowns
PATCH /v1/linkedin-sourcing/cooldowns/{id}/cancel
GET   /v1/linkedin-sourcing/cooldowns/stats
```

---

## Tests rápidos (desde curl)

### Test 1: Verificar knowledge base poblada
```bash
curl -sS "https://infra-svc01.mailerblend.com/_svc/v1/linkedin-sourcing/knowledge-base?category=SERVICES" \
  -H "X-API-Key: ${CRM_API_KEY}" | python3 -m json.tool
```

Esperado: 3 items (GUARDIAN, MOTOR, FORTALEZA)

### Test 2: Verificar rate limits
```bash
curl -sS "https://infra-svc01.mailerblend.com/_svc/v1/linkedin-sourcing/rate-limits/current/status" \
  -H "X-API-Key: ${CRM_API_KEY}" | python3 -m json.tool
```

Esperado:
```json
{
  "invites": {
    "sent_today": 0,
    "cap": 20,
    "remaining": 20,
    "can_send": true
  },
  "messages": {
    "sent_today": 0,
    "cap": 50,
    "remaining": 50,
    "can_send": true
  },
  "cooldown_active": false
}
```

### Test 3: Log activity
```bash
curl -sS -X POST "https://infra-svc01.mailerblend.com/_svc/v1/linkedin-sourcing/activity-log" \
  -H "X-API-Key: ${CRM_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "activity_type": "INVITE",
    "metadata": {"lead_id": "test", "segment": "Pack1_A"},
    "risk_level": "LOW"
  }' | python3 -m json.tool
```

Esperado: {"id": "uuid", "activity_type": "INVITE", "logged_at": "..."}

### Test 4: Verificar stats de hoy
```bash
curl -sS "https://infra-svc01.mailerblend.com/_svc/v1/linkedin-sourcing/activity-log/stats/today" \
  -H "X-API-Key: ${CRM_API_KEY}" | python3 -m json.tool
```

Esperado: {"stats": {"INVITE": 1, ...}, "total": 1}

### Test 5: Cooldown status
```bash
curl -sS "https://infra-svc01.mailerblend.com/_svc/v1/linkedin-sourcing/cooldowns/status" \
  -H "X-API-Key: ${CRM_API_KEY}" | python3 -m json.tool
```

Esperado: {"cooldown_active": false}

### Test 6: Contexto para IA (pack GUARDIAN)
```bash
curl -sS "https://infra-svc01.mailerblend.com/_svc/v1/linkedin-sourcing/knowledge-base/context/GUARDIAN?categories=SERVICES,ICP_DEFINITION" \
  -H "X-API-Key: ${CRM_API_KEY}" | python3 -m json.tool
```

Esperado: JSON con servicios + ICP del pack GUARDIAN

---

## ✅ Checklist de instalación

- [ ] Copiar 4 archivos .py a routers/v1/
- [ ] Editar main.py (imports + include_router)
- [ ] Reiniciar API
- [ ] Test 1: Knowledge base
- [ ] Test 2: Rate limits status
- [ ] Test 3: Log activity
- [ ] Test 4: Stats hoy
- [ ] Test 5: Cooldown status
- [ ] Test 6: Contexto IA

Si todos los tests pasan → Backend 100% completo ✅
