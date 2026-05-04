from __future__ import annotations

import json
from pathlib import Path

from mem0_selfhosted_fastmcp.server import (
    ALL_CLASSIFIED_PATHS,
    EXCLUDED_PATHS,
    INCLUDED_PATHS,
)


def test_all_upstream_paths_are_classified() -> None:
    fixture = Path(__file__).parent / "fixtures" / "mem0_openapi_paths.json"
    upstream_paths = set(json.loads(fixture.read_text()))
    assert upstream_paths == ALL_CLASSIFIED_PATHS


def test_included_and_excluded_paths_do_not_overlap() -> None:
    assert set(INCLUDED_PATHS).isdisjoint(EXCLUDED_PATHS)
