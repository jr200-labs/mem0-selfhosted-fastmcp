from __future__ import annotations

import argparse
import json
import os
from typing import Any, Final

import httpx
from fastmcp import FastMCP


DEFAULT_BASE_URL = "http://mem0-memory:8765"
OPENAPI_PATH = "/openapi.json"
INCLUDED_PATHS: Final[tuple[str, ...]] = (
    "/memories",
    "/memories/{memory_id}",
    "/memories/{memory_id}/history",
    "/entities",
    "/entities/{entity_type}/{entity_id}",
)

EXCLUDED_PATHS: Final[tuple[str, ...]] = (
    # Overridden manually below because the live server requires entity scoping
    # inside `filters`, even though the OpenAPI advertises top-level entity args.
    "/search",
    # Auth/bootstrap/config/admin endpoints intentionally not exposed to OpenCode.
    "/auth/setup-status",
    "/auth/register",
    "/auth/login",
    "/auth/refresh",
    "/auth/me",
    "/auth/change-password",
    "/auth/onboarding-complete",
    "/api-keys",
    "/api-keys/{key_id}",
    "/requests",
    "/configure",
    "/configure/providers",
    "/generate-instructions",
    "/reset",
)

ALL_CLASSIFIED_PATHS: Final[set[str]] = set(INCLUDED_PATHS) | set(EXCLUDED_PATHS)


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
    spec = dict(spec)
    spec["paths"] = {
        path: value
        for path, value in spec.get("paths", {}).items()
        if path in INCLUDED_PATHS
    }
    return spec


def _load_openapi(base_url: str, headers: dict[str, str]) -> dict[str, Any]:
    response = httpx.get(
        f"{base_url.rstrip('/')}{OPENAPI_PATH}", headers=headers, timeout=30.0
    )
    response.raise_for_status()
    return response.json()


def _normalize_optional_str(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _merge_search_filters(
    *,
    user_id: str | None,
    agent_id: str | None,
    run_id: str | None,
    filters: dict[str, Any] | None,
) -> dict[str, Any] | None:
    merged = dict(filters or {})
    for key, value in (
        ("user_id", _normalize_optional_str(user_id)),
        ("agent_id", _normalize_optional_str(agent_id)),
        ("run_id", _normalize_optional_str(run_id)),
    ):
        if value is None:
            continue
        if key in merged and merged[key] != value:
            raise ValueError(
                f"Conflicting {key} specified in both top-level args and filters"
            )
        merged[key] = value
    return merged or None


def create_server() -> FastMCP:
    base_url = os.getenv("MEM0_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    headers = _build_headers()
    openapi_spec = _pruned_openapi(_load_openapi(base_url, headers))

    client = httpx.AsyncClient(base_url=base_url, headers=headers, timeout=60.0)
    server = FastMCP.from_openapi(
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

    @server.tool(name="search_memories")
    async def search_memories(
        query: str,
        user_id: str | None = None,
        agent_id: str | None = None,
        run_id: str | None = None,
        filters: dict[str, Any] | None = None,
        top_k: int | None = None,
        threshold: float | None = None,
    ) -> Any:
        payload = {
            "query": query,
            "filters": _merge_search_filters(
                user_id=user_id,
                agent_id=agent_id,
                run_id=run_id,
                filters=filters,
            ),
            "top_k": top_k,
            "threshold": threshold,
        }
        payload = {key: value for key, value in payload.items() if value is not None}
        response = await client.post("/search", json=payload)
        response.raise_for_status()
        return response.json()

    return server


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
