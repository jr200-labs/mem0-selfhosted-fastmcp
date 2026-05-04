from __future__ import annotations

import argparse
import json
import os
from typing import Any

import httpx
from fastmcp import FastMCP


DEFAULT_BASE_URL = "http://mem0-memory:8765"
OPENAPI_PATH = "/openapi.json"


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def _build_headers() -> dict[str, str]:
    if api_key := os.getenv("MEM0_API_KEY", "").strip():
        return {"X-API-Key": api_key}
    if bearer := os.getenv("MEM0_BEARER_TOKEN", "").strip():
        return {"Authorization": f"Bearer {bearer}"}
    raise RuntimeError("Set MEM0_API_KEY or MEM0_BEARER_TOKEN")


def _pruned_openapi(spec: dict[str, Any]) -> dict[str, Any]:
    allowed_paths = {
        "/memories",
        "/memories/{memory_id}",
        "/memories/{memory_id}/history",
        "/search",
        "/entities",
        "/entities/{entity_type}/{entity_id}",
    }
    spec = dict(spec)
    spec["paths"] = {
        path: value
        for path, value in spec.get("paths", {}).items()
        if path in allowed_paths
    }
    return spec


def _load_openapi(base_url: str, headers: dict[str, str]) -> dict[str, Any]:
    response = httpx.get(
        f"{base_url.rstrip('/')}{OPENAPI_PATH}", headers=headers, timeout=30.0
    )
    response.raise_for_status()
    return response.json()


def create_server() -> FastMCP:
    base_url = os.getenv("MEM0_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    headers = _build_headers()
    openapi_spec = _pruned_openapi(_load_openapi(base_url, headers))

    client = httpx.AsyncClient(base_url=base_url, headers=headers, timeout=60.0)
    return FastMCP.from_openapi(
        openapi_spec=openapi_spec,
        client=client,
        name="mem0-selfhosted-fastmcp",
        mcp_names={
            "add_memory_memories_post": "add_memory",
            "get_all_memories_memories_get": "list_memories",
            "delete_all_memories_memories_delete": "delete_all_memories",
            "get_memory_memories__memory_id__get": "get_memory",
            "update_memory_memories__memory_id__put": "update_memory",
            "delete_memory_memories__memory_id__delete": "delete_memory",
            "memory_history_memories__memory_id__history_get": "memory_history",
            "search_memories_search_post": "search_memories",
            "list_entities_entities_get": "list_entities",
            "delete_entity_entities__entity_type___entity_id__delete": "delete_entity",
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="FastMCP bridge for self-hosted Mem0")
    parser.add_argument(
        "--transport",
        default=os.getenv("FASTMCP_TRANSPORT", "stdio"),
        choices=["stdio", "streamable-http", "http", "sse"],
    )
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8081")))
    parser.add_argument(
        "--dump-openapi",
        action="store_true",
        help="Print the pruned OpenAPI spec and exit",
    )
    args = parser.parse_args()

    if args.dump_openapi:
        base_url = os.getenv("MEM0_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
        headers = _build_headers()
        print(json.dumps(_pruned_openapi(_load_openapi(base_url, headers)), indent=2))
        return

    server = create_server()
    if args.transport == "stdio":
        server.run(transport="stdio")
    else:
        server.run(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
