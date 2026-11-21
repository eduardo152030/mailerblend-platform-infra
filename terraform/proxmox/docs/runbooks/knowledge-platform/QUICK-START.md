# Knowledge Platform — Agent Quick Start

Outline Community is the wiki. Draw.io is the browser editor, and PlantUML renders text diagrams. Read the [deployment manifest](platform.json) and [integration guide](../KNOWLEDGE-PLATFORM-AI-INTEGRATION.md).

1. Reach CT109 through the LAN or an approved private route. Current Outline origin is `https://infra-doc.mailerblend.com`. See the [operator runbook](../KNOWLEDGE-PLATFORM.md). Render access through the CT635 tunnel is typically `http://127.0.0.1:18080`.
2. Ask the workspace administrator for the scoped agent key through the approved secret manager. Set `OUTLINE_API_TOKEN`, `OUTLINE_URL` and `PLANTUML_URL` in the client environment. Keep standard TLS certificate verification enabled.
3. Search, then read the existing page by its UUID.

```bash
curl --fail-with-body --silent --show-error "$OUTLINE_URL/api/documents.search" \
  -H "Authorization: Bearer $OUTLINE_API_TOKEN" -H 'Content-Type: application/json' \
  --data '{"query":"CT618"}'
python3 docs/runbooks/knowledge-platform/outline-example.py read "$DOC_ID"
```

4. Create only after checking the project collection for an existing page. For updates, use a unique patch and the returned revision. For diagrams, use the managed marker pair and publish by UUID. See the [tested examples](../KNOWLEDGE-PLATFORM-AI-INTEGRATION.md).
5. Read back the result. On 401 verify the key and private route. On 403 verify collection permissions and endpoint scopes. On 409 read the latest revision and review the patch. On a POST timeout reconcile the result before retrying.
6. For MCP use `/mcp`, bearer auth and Streamable HTTP. The validated key was read-only. Use `tools/list` after initializing and use REST for writes.

Production inspection is read-only unless separately authorized. Follow the [LXC documentation workflow](../LXC-DOCUMENTATION-PROCESS.md), record observed evidence, and keep credentials and private data out of documents.
