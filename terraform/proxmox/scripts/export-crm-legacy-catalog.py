"""Export the Budibase CouchDB catalogue privately, from the isolated clone."""
import base64
import json
import socket
import subprocess
from urllib.parse import quote
from urllib.request import Request, ProxyHandler, build_opener


def main():
    assert socket.gethostname() == "crm-rehearsal-9619"
    for family in ("-4", "-6"):
        assert not json.loads(subprocess.check_output(["ip", family, "-j", "route", "show", "default"]))
    links = json.loads(subprocess.check_output(["ip", "-j", "link", "show", "dev", "eth0"]))
    assert "LOWER_UP" not in links[0]["flags"]
    couch = json.loads(subprocess.check_output(["docker", "inspect", "budibase-couchdb"]))[0]
    env = dict(item.split("=", 1) for item in couch["Config"]["Env"])
    identity = env["COUCHDB_USER"] + ":" + env["COUCHDB_PASSWORD"]
    auth = "Basic " + base64.b64encode(identity.encode()).decode()
    endpoint = next(net["IPAddress"] for net in couch["NetworkSettings"]["Networks"].values()
                    if net.get("IPAddress"))
    opener = build_opener(ProxyHandler({}))

    def fetch(path):
        request = Request(f"http://{endpoint}:5984{path}", headers={"Authorization": auth})
        with opener.open(request, timeout=25) as response:
            return json.load(response)

    databases = fetch("/_all_dbs")
    assert "global-db" in databases
    data = {name: fetch("/" + quote(name, safe="") + "/_all_docs?include_docs=true&attachments=true")
            for name in databases if not name.startswith("_")}
    assert data["global-db"]["rows"]
    print(json.dumps(data))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit("Catalogue export failed: " + type(error).__name__) from None
