.PHONY: sync run run-http dump-openapi snapshot-openapi snapshot-paths check-live

PYTHON ?= uv run python
CLI ?= uv run mem0-selfhosted-fastmcp
OPENAPI_SNAPSHOT ?= generated/openapi.pruned.json
OPENAPI_PATHS_SNAPSHOT ?= tests/fixtures/mem0_openapi_paths.json

sync:
	uv sync

run:
	$(CLI)

run-http:
	$(CLI) --transport streamable-http --port 8081

dump-openapi:
	$(CLI) --dump-openapi

snapshot-openapi:
	mkdir -p generated
	$(CLI) --dump-openapi > $(OPENAPI_SNAPSHOT)

snapshot-paths:
	mkdir -p $(dir $(OPENAPI_PATHS_SNAPSHOT))
	$(PYTHON) - <<'PY' > $(OPENAPI_PATHS_SNAPSHOT)
import json, os, sys, urllib.request
base = os.environ.get("MEM0_BASE_URL", "http://mem0-memory:8765").rstrip("/")
headers = {}
if os.environ.get("MEM0_API_KEY"):
    headers["X-API-Key"] = os.environ["MEM0_API_KEY"]
elif os.environ.get("MEM0_BEARER_TOKEN"):
    headers["Authorization"] = f"Bearer {os.environ['MEM0_BEARER_TOKEN']}"
req = urllib.request.Request(base + "/openapi.json", headers=headers)
with urllib.request.urlopen(req, timeout=30) as r:
    data = json.load(r)
json.dump(sorted(data["paths"].keys()), sys.stdout, indent=2)
print()
PY

check-live:
	$(PYTHON) -c 'from mem0_selfhosted_fastmcp.server import create_server; create_server(); print("server ok")'
