# mem0-selfhosted-fastmcp

Thin FastMCP bridge for a self-hosted Mem0 REST API.

It fetches the live OpenAPI spec from a Mem0 server, prunes it to the useful
memory operations, and exposes those endpoints as MCP tools for OpenCode or
other MCP clients.

Implementation note:
- this uses FastMCP's official OpenAPI integration via `FastMCP.from_openapi`
- there is no handwritten MCP protocol layer here; the bridge is generated from
  the live Mem0 OpenAPI spec at startup and then lightly curated (path pruning
  plus friendly MCP tool names)

## Scope

Exposed tools:
- `add_memory`
- `list_memories`
- `search_memories`
- `get_memory`
- `update_memory`
- `delete_memory`
- `delete_all_memories`
- `memory_history`
- `list_entities`
- `delete_entity`

Excluded on purpose:
- auth/login/refresh flows
- setup/bootstrap endpoints
- admin/configure/request-log endpoints

## Environment

Required:
- `MEM0_BASE_URL` (default: `http://mem0-memory:8765`)
- one of:
  - `MEM0_API_KEY` (sent as `X-API-Key`)
  - `MEM0_BEARER_TOKEN` (sent as `Authorization: Bearer ...`)

Optional:
- `FASTMCP_TRANSPORT` (`stdio` by default)
- `HOST` / `PORT` for HTTP transports

## Install

Published package:
- PyPI: https://pypi.org/project/mem0-selfhosted-fastmcp/

Install with `uvx` (recommended for MCP clients):

```bash
uvx mem0-selfhosted-fastmcp --help
```

Install into a Python environment:

```bash
uv pip install mem0-selfhosted-fastmcp
```

or:

```bash
pip install mem0-selfhosted-fastmcp
```

## Usage

Stdio mode for OpenCode-style spawning:

```bash
MEM0_BASE_URL=http://mem0-memory:8765 \
MEM0_API_KEY=... \
uvx mem0-selfhosted-fastmcp
```

Dump the pruned OpenAPI used for generation:

```bash
MEM0_BASE_URL=http://mem0-memory:8765 \
MEM0_API_KEY=... \
uvx mem0-selfhosted-fastmcp --dump-openapi
```

Run as HTTP MCP server:

```bash
MEM0_BASE_URL=http://mem0-memory:8765 \
MEM0_API_KEY=... \
uvx mem0-selfhosted-fastmcp --transport streamable-http --port 8081
```

## Maintenance

Because the bridge loads the live OpenAPI spec at startup, many Mem0 API
changes are picked up automatically without code generation. The places most
likely to need manual updates are:
- path allowlist changes in `server.py`
- operationId -> MCP name mappings when upstream operationIds change
- auth header strategy if Mem0 auth changes

Helpful targets:

```bash
make sync              # install/update dependencies
make dump-openapi      # print the pruned live OpenAPI used by the bridge
make snapshot-openapi  # save the current pruned live OpenAPI to generated/
make check-live        # smoke-test server creation against the live Mem0 API
make run               # stdio mode for OpenCode
make run-http          # streamable-http mode for shared/server use
```

## OpenCode MCP example

```toml
[servers.mem0]
transport = "stdio"
command = "uvx"
args = ["mem0-selfhosted-fastmcp"]
env.MEM0_BASE_URL = "http://mem0-memory:8765"
env.MEM0_API_KEY = "${MEM0_API_KEY}"
```

For a pinned version:

```toml
[servers.mem0]
transport = "stdio"
command = "uvx"
args = ["mem0-selfhosted-fastmcp==0.1.1"]
env.MEM0_BASE_URL = "http://mem0-memory:8765"
env.MEM0_API_KEY = "${MEM0_API_KEY}"
```
