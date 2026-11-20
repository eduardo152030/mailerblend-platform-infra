"""Observe CRMAPI for five minutes. Reject any related FIRING alert."""
import json
import sys
import time
import urllib.parse
import urllib.request

URL = "http://192.168.1.110:9090/api/v1/query"
DOMAIN = "infra-svc01.mailerblend.com"


def related(labels):
    return (
        labels.get("service") == "infra-composable-crm"
        or labels.get("ct_id") == "618"
        or DOMAIN in labels.get("instance", "")
        or labels.get("instance", "").startswith("192.168.1.118:")
    )


def main():
    started = float(sys.argv[1])
    deadline = time.monotonic() + 300
    while True:
        elapsed = max(1, int(time.time() - started) + 1)
        query = 'present_over_time(ALERTS{alertstate="firing"}[' + str(elapsed) + 's])'
        with urllib.request.urlopen(URL + "?" + urllib.parse.urlencode({"query": query}), timeout=8) as response:
            result = json.load(response)
        if result.get("status") != "success":
            raise SystemExit("Prometheus query failed")
        firing = [item["metric"].get("alertname") for item in result["data"]["result"] if related(item["metric"])]
        if firing:
            raise SystemExit("CRM-related FIRING alerts: " + ", ".join(sorted(set(firing))))
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            print("Five minutes of stabilization verified without CRM-related FIRING alerts.")
            return
        time.sleep(min(10, remaining))


if __name__ == "__main__":
    main()
