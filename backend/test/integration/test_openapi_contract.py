import json
from pathlib import Path
from typing import Any

import pytest

ALLOWED_HTTP_METHODS = {
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "options",
    "head",
    "trace",
}
REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = REPO_ROOT.parent / "openapi" / "spec.yaml"


def _extract_spec_endpoints(spec_text: str) -> set[tuple[str, str]]:
    """Extract (method, path) endpoints from the OpenAPI YAML paths section.

    This parser intentionally relies on stable indentation used in this repository's
    spec file:
    - path entries are indented by 2 spaces under `paths:`
    - methods are indented by 4 spaces under each path
    """
    endpoints: set[tuple[str, str]] = set()

    in_paths = False
    current_path: str | None = None

    for raw_line in spec_text.splitlines():
        line = raw_line.rstrip("\n")

        if not in_paths:
            if line.strip() == "paths:":
                in_paths = True
            continue

        # End of `paths:` block
        if line and not line.startswith(" "):
            break

        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Path declaration: "  /foo:".
        if line.startswith("  /") and stripped.endswith(":"):
            current_path = stripped[:-1]
            continue

        # Method declaration: "    get:".
        if current_path and line.startswith("    ") and stripped.endswith(":"):
            key = stripped[:-1]
            if key in ALLOWED_HTTP_METHODS:
                endpoints.add((key, current_path))

    return endpoints


def _extract_runtime_endpoints(openapi_json: dict) -> set[tuple[str, str]]:
    endpoints: set[tuple[str, str]] = set()

    for path, operations in openapi_json.get("paths", {}).items():
        if not path.startswith("/api"):
            continue
        if not isinstance(operations, dict):
            continue

        for method in operations:
            method_l = str(method).lower()
            if method_l in ALLOWED_HTTP_METHODS:
                endpoints.add((method_l, path))

    return endpoints


def _load_normalized_spec_endpoints() -> set[tuple[str, str]]:
    spec_text = SPEC_PATH.read_text(encoding="utf-8")
    spec_endpoints = _extract_spec_endpoints(spec_text)

    # spec.yaml servers are rooted at /api, while FastAPI exposes absolute paths.
    return {(method, f"/api{path}") for method, path in spec_endpoints}


def _to_spec_relative_path(runtime_path: str) -> str:
    if runtime_path.startswith("/api/"):
        return runtime_path[4:]
    if runtime_path == "/api":
        return "/"
    return runtime_path


def _extract_json_response_schema(openapi: dict[str, Any], method: str, path: str) -> dict[str, Any] | None:
    operation = openapi.get("paths", {}).get(path, {}).get(method)
    if not isinstance(operation, dict):
        return None

    responses = operation.get("responses", {})
    if not isinstance(responses, dict):
        return None

    preferred_codes = []
    if "200" in responses:
        preferred_codes.append("200")
    preferred_codes.extend(sorted(code for code in responses if str(code).startswith("2") and code != "200"))

    for code in preferred_codes:
        response_obj = responses.get(code)
        if not isinstance(response_obj, dict):
            continue

        content = response_obj.get("content", {})
        if not isinstance(content, dict):
            continue

        media = content.get("application/json")
        if not isinstance(media, dict):
            continue

        schema = media.get("schema")
        if isinstance(schema, dict):
            return schema

    return None


def _resolve_schema(openapi: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    current = schema
    visited_refs: set[str] = set()

    while isinstance(current, dict) and "$ref" in current:
        ref = current.get("$ref")
        if not isinstance(ref, str) or not ref.startswith("#/components/schemas/"):
            break
        if ref in visited_refs:
            break
        visited_refs.add(ref)

        schema_name = ref.split("/")[-1]
        candidate = openapi.get("components", {}).get("schemas", {}).get(schema_name)
        if not isinstance(candidate, dict):
            break
        current = candidate

    return current if isinstance(current, dict) else schema


def _merge_key_trees(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in extra.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _merge_key_trees(merged[key], value)
        elif key in merged and isinstance(merged[key], dict) and value is None:
            continue
        elif key in merged and merged[key] is None and isinstance(value, dict):
            merged[key] = value
        else:
            merged[key] = value
    return merged


def _schema_key_tree(openapi: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any] | None:
    resolved = _resolve_schema(openapi, schema)

    for composition in ("allOf", "oneOf", "anyOf"):
        if composition in resolved and isinstance(resolved[composition], list):
            tree: dict[str, Any] = {}
            found_object = False
            for item in resolved[composition]:
                if not isinstance(item, dict):
                    continue
                item_tree = _schema_key_tree(openapi, item)
                if isinstance(item_tree, dict):
                    tree = _merge_key_trees(tree, item_tree)
                    found_object = True
            return tree if found_object else None

    schema_type = resolved.get("type")

    if schema_type == "array":
        items = resolved.get("items", {})
        if isinstance(items, dict):
            return {"[]": _schema_key_tree(openapi, items)}
        return {"[]": None}

    if schema_type == "object" or "properties" in resolved:
        properties = resolved.get("properties", {})
        normalized_properties: dict[str, Any] = {}
        if isinstance(properties, dict):
            for key in sorted(properties):
                value = properties[key]
                if isinstance(value, dict):
                    normalized_properties[key] = _schema_key_tree(openapi, value)
                else:
                    normalized_properties[key] = None

        additional_properties = resolved.get("additionalProperties")
        if isinstance(additional_properties, dict):
            normalized_properties["*"] = _schema_key_tree(openapi, additional_properties)

        return normalized_properties

    return None


@pytest.fixture(scope="module")
def spec_endpoints() -> set[tuple[str, str]]:
    return _load_normalized_spec_endpoints()


@pytest.fixture(scope="module")
def spec_openapi() -> dict[str, Any]:
    yaml = pytest.importorskip("yaml")
    spec_text = SPEC_PATH.read_text(encoding="utf-8")
    parsed = yaml.safe_load(spec_text)
    assert isinstance(parsed, dict)
    return parsed


@pytest.fixture(scope="module")
def runtime_openapi() -> dict[str, Any]:
    from fastapi.testclient import TestClient

    from .context import app

    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    parsed = json.loads(response.content.decode("utf-8"))
    assert isinstance(parsed, dict)
    return parsed


@pytest.fixture(scope="module")
def runtime_endpoints(runtime_openapi: dict[str, Any]) -> set[tuple[str, str]]:
    return _extract_runtime_endpoints(runtime_openapi)


def _endpoint_id(endpoint: tuple[str, str]) -> str:
    method, path = endpoint
    return f"{method.upper()} {path}"


def _assert_endpoint_format(endpoint: tuple[str, str]) -> None:
    assert isinstance(endpoint, tuple), f"Endpoint must be a tuple, got: {type(endpoint)}"
    assert len(endpoint) == 2, f"Endpoint tuple must have 2 items, got: {endpoint}"

    method, path = endpoint
    assert isinstance(method, str), f"Endpoint method must be a string, got: {type(method)}"
    assert isinstance(path, str), f"Endpoint path must be a string, got: {type(path)}"
    assert method in ALLOWED_HTTP_METHODS, f"Invalid endpoint method: {method}"
    assert method == method.lower(), f"Endpoint method must be lowercase, got: {method}"
    assert path.startswith("/api"), f"Endpoint path must start with '/api', got: {path}"
    assert " " not in path, f"Endpoint path must not contain spaces, got: {path}"


SPEC_ENDPOINT_CASES = sorted(_load_normalized_spec_endpoints())


@pytest.mark.parametrize("spec_endpoint", SPEC_ENDPOINT_CASES, ids=_endpoint_id)
def test_runtime_openapi_includes_spec_endpoint(
    runtime_endpoints: set[tuple[str, str]], spec_endpoint: tuple[str, str]
):
    assert spec_endpoint in runtime_endpoints, (
        f"Endpoint defined in spec.yaml but missing from runtime openapi.json: {spec_endpoint}"
    )


def test_runtime_openapi_has_no_undeclared_endpoints(
    spec_endpoints: set[tuple[str, str]], runtime_endpoints: set[tuple[str, str]]
):
    extra_in_runtime = sorted(runtime_endpoints - spec_endpoints)
    assert not extra_in_runtime, (
        f"Endpoints present in runtime openapi.json but not declared in spec.yaml: {extra_in_runtime}"
    )


def test_extracted_endpoints_have_expected_format(
    spec_endpoints: set[tuple[str, str]], runtime_endpoints: set[tuple[str, str]]
):
    for endpoint in spec_endpoints:
        _assert_endpoint_format(endpoint)

    for endpoint in runtime_endpoints:
        _assert_endpoint_format(endpoint)


@pytest.mark.parametrize("spec_endpoint", SPEC_ENDPOINT_CASES, ids=_endpoint_id)
def test_runtime_openapi_response_format_matches_spec_per_endpoint(
    spec_openapi: dict[str, Any],
    runtime_openapi: dict[str, Any],
    runtime_endpoints: set[tuple[str, str]],
    spec_endpoint: tuple[str, str],
):
    method, runtime_path = spec_endpoint

    if spec_endpoint not in runtime_endpoints:
        pytest.skip("Endpoint missing from runtime OpenAPI; covered by endpoint presence test")

    spec_path = _to_spec_relative_path(runtime_path)
    spec_response_schema = _extract_json_response_schema(spec_openapi, method, spec_path)
    runtime_response_schema = _extract_json_response_schema(runtime_openapi, method, runtime_path)

    if spec_response_schema is None and runtime_response_schema is None:
        pytest.skip("No JSON success response schema declared for this endpoint")

    assert spec_response_schema is not None, (
        f"JSON success response schema missing in spec.yaml for endpoint {method.upper()} {runtime_path}"
    )
    assert runtime_response_schema is not None, (
        f"JSON success response schema missing in runtime openapi.json for endpoint {method.upper()} {runtime_path}"
    )

    expected_key_tree = _schema_key_tree(spec_openapi, spec_response_schema)
    actual_key_tree = _schema_key_tree(runtime_openapi, runtime_response_schema)

    assert actual_key_tree == expected_key_tree, (
        "Response JSON key format mismatch for endpoint "
        f"{method.upper()} {runtime_path}. "
        f"Expected keys: {expected_key_tree}. Got: {actual_key_tree}"
    )
