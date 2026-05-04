from mem0_selfhosted_fastmcp import create_server
from mem0_selfhosted_fastmcp.server import _normalize_optional_str


def test_package_exports_create_server() -> None:
    assert callable(create_server)


def test_normalize_optional_str_treats_blank_as_none() -> None:
    assert _normalize_optional_str(None) is None
    assert _normalize_optional_str("") is None
    assert _normalize_optional_str("   ") is None
    assert _normalize_optional_str("  jr200  ") == "jr200"
