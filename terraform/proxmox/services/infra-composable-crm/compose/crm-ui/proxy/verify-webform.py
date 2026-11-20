"""Run the synthetic golden intake and read its authenticated snapshot."""
import base64
import datetime
import json
import netrc
import os
import urllib.request

host = "infra-svc01.mailerblend.com"
base = f"https://{host}/_svc/v1/"
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")
payload = {
    "nombre": f"Golden CRM {stamp}",
    "email": f"golden.{stamp}@example.com",
    "company_name": "Golden Synthetic",
    "gdpr_consent": True,
    "utm": {"utm_source": "google", "utm_campaign": "crm-cutover", "gclid": f"TEST-{stamp}"},
    "form": {
        "servicio_relacionado": "Outsourcing IT / CAU",
        "mensaje": "Prueba sintética del corte CRM",
        "urgencia": "Durante este mes",
    },
}
post = urllib.request.Request(
    base + "intake/webform",
    json.dumps(payload).encode(),
    {"Content-Type": "application/json", "X-Ingest-Secret": os.environ["CRM_INGEST_SECRET"]},
)
with urllib.request.urlopen(post, timeout=15) as response:
    assert response.status == 200
    contact_id = json.load(response)["contact_id"]
login, _, password = netrc.netrc(os.environ["CRM_OPERATOR_NETRC"]).authenticators(host)
basic = base64.b64encode(f"{login}:{password}".encode()).decode()
request = urllib.request.Request(
    base + f"contacts/{contact_id}/snapshot", headers={"Authorization": f"Basic {basic}"}
)
with urllib.request.urlopen(request, timeout=15) as response:
    assert response.status == 200
    related = json.load(response)["related"]
assert all(related[key] for key in ("parametros_utm", "formulario_web", "historial", "oportunidades"))
assert {"EVENT::LEAD_CREATED", "EVENT::LEAD_QUALIFIED"}.issubset(
    {event["subject"] for event in related["historial"]}
)
print("Golden PASS: POST y snapshot 200; UTM, formulario, historial y oportunidad")
