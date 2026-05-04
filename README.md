# mem0-selfhosted-fastmcp

Thin FastMCP bridge for a self-hosted Mem0 REST API.

It fetches the live OpenAPI spec from a Mem0 server, prunes it to the useful
memory operations, and exposes those endpoints as MCP tools for OpenCode or
other MCP clients.

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

## Usage

Stdio mode for OpenCode-style spawning:

```bash
MEM0_BASE_URL=http://mem0-memory:8765 \
MEM0_API_KEY=... \
uv run mem0-selfhosted-fastmcp
```

Dump the pruned OpenAPI used for generation:

```bash
MEM0_BASE_URL=http://mem0-memory:8765 \
MEM0_API_KEY=... \
uv run mem0-selfhosted-fastmcp --dump-openapi
```

Run as HTTP MCP server:

```bash
MEM0_BASE_URL=http://mem0-memory:8765 \
MEM0_API_KEY=... \
uv run mem0-selfhosted-fastmcp --transport streamable-http --port 8081
```

## OpenCode MCP example

```toml
[servers.mem0]
transport = "stdio"
command = "uvx"
args = ["--from", "/workspace/jr200-labs/mem0-selfhosted-fastmcp", "mem0-selfhosted-fastmcp"]
env.MEM0_BASE_URL = "http://mem0-memory:8765"
env.MEM0_API_KEY = "${MEM0_API_KEY}"
```
