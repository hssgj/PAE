from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


class ToolError(RuntimeError):
    """Base error for tool lookup, validation, or execution failures."""


class ToolValidationError(ToolError):
    """Raised when tool arguments do not match the declared schema."""


@dataclass(frozen=True)
class ToolContext:
    store: Any
    session: Any


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    argument_schema: dict[str, Any]
    executor: Callable[[ToolContext, dict[str, Any]], dict[str, Any]]


def _validate_value(name: str, value: Any, schema: dict[str, Any]) -> Any:
    expected = schema.get("type")

    if expected == "string":
        if not isinstance(value, str):
            raise ToolValidationError(f"{name} must be a string")
        if schema.get("minLength", 0) and len(value) < schema["minLength"]:
            raise ToolValidationError(
                f"{name} must contain at least {schema['minLength']} character(s)"
            )
    elif expected == "integer":
        if isinstance(value, bool) or not isinstance(value, int):
            raise ToolValidationError(f"{name} must be an integer")
    elif expected == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ToolValidationError(f"{name} must be a number")
    elif expected == "boolean":
        if not isinstance(value, bool):
            raise ToolValidationError(f"{name} must be a boolean")
    elif expected not in {None, "object"}:
        raise ToolValidationError(
            f"unsupported schema type {expected!r} for argument {name}"
        )

    if "enum" in schema and value not in schema["enum"]:
        raise ToolValidationError(
            f"{name} must be one of {schema['enum']!r}"
        )

    return value


def validate_arguments(
    schema: dict[str, Any],
    arguments: dict[str, Any],
) -> dict[str, Any]:
    if schema.get("type") != "object":
        raise ToolValidationError("tool argument schema must have type=object")
    if not isinstance(arguments, dict):
        raise ToolValidationError("tool arguments must be a JSON object")

    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    additional_allowed = schema.get("additionalProperties", False)

    missing = sorted(name for name in required if name not in arguments)
    if missing:
        raise ToolValidationError(
            "missing required argument(s): " + ", ".join(missing)
        )

    unknown = sorted(name for name in arguments if name not in properties)
    if unknown and not additional_allowed:
        raise ToolValidationError(
            "unknown argument(s): " + ", ".join(unknown)
        )

    normalized: dict[str, Any] = {}

    for name, property_schema in properties.items():
        if name in arguments:
            value = arguments[name]
        elif "default" in property_schema:
            value = property_schema["default"]
        else:
            continue

        normalized[name] = _validate_value(name, value, property_schema)

    if additional_allowed:
        for name in unknown:
            normalized[name] = arguments[name]

    return normalized


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if not tool.name or tool.name.strip() != tool.name:
            raise ToolError("tool name must be a non-empty trimmed string")
        if tool.name in self._tools:
            raise ToolError(f"tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolError(f"unknown tool: {name}") from exc

    def specs(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "arguments": tool.argument_schema,
            }
            for tool in self._tools.values()
        ]

    def execute(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        context: ToolContext,
    ) -> dict[str, Any]:
        tool = self.get(name)
        validated = validate_arguments(tool.argument_schema, arguments)
        result = tool.executor(context, validated)

        if not isinstance(result, dict):
            raise ToolError(f"tool {name} returned a non-object result")

        return result
