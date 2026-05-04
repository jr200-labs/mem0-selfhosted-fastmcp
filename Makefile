.PHONY: sync run run-http dump-openapi snapshot-openapi check-live

PYTHON ?= uv run python
CLI ?= uv run mem0-selfhosted-fastmcp
OPENAPI_SNAPSHOT ?= generated/openapi.pruned.json

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

check-live:
	$(PYTHON) -c 'from mem0_selfhosted_fastmcp.server import create_server; create_server(); print("server ok")'
