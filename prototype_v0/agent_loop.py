from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from tool_core import ToolContext, ToolRegistry


MAX_TOOL_CALLS = 3
MAX_PROTOCOL_REPAIRS = 1


class AgentProtocolError(RuntimeError):
    """Raised when the model does not follow the runtime tool protocol."""


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class FinalAnswer:
    content: str


def _strip_single_json_fence(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```") or not stripped.endswith("```"):
        return stripped

    lines = stripped.splitlines()
    if len(lines) < 3:
        return stripped

    first = lines[0].strip().lower()
    if first not in {"```", "```json"}:
        return stripped
    if lines[-1].strip() != "```":
        return stripped

    return "\n".join(lines[1:-1]).strip()


def parse_agent_response(text: str) -> ToolCall | FinalAnswer:
    raw = _strip_single_json_fence(text)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AgentProtocolError(
            "response must be exactly one JSON object"
        ) from exc

    if not isinstance(payload, dict):
        raise AgentProtocolError("protocol response must be a JSON object")

    response_type = payload.get("type")

    if response_type == "tool_call":
        allowed = {"type", "name", "arguments"}
        unknown = set(payload) - allowed
        if unknown:
            raise AgentProtocolError(
                "tool_call contains unknown field(s): "
                + ", ".join(sorted(unknown))
            )

        name = payload.get("name")
        arguments = payload.get("arguments")

        if not isinstance(name, str) or not name.strip():
            raise AgentProtocolError("tool_call.name must be a non-empty string")
        if not isinstance(arguments, dict):
            raise AgentProtocolError("tool_call.arguments must be a JSON object")

        return ToolCall(name=name, arguments=arguments)

    if response_type == "final":
        allowed = {"type", "content"}
        unknown = set(payload) - allowed
        if unknown:
            raise AgentProtocolError(
                "final contains unknown field(s): "
                + ", ".join(sorted(unknown))
            )

        content = payload.get("content")
        if not isinstance(content, str):
            raise AgentProtocolError("final.content must be a string")

        return FinalAnswer(content=content.strip())

    raise AgentProtocolError("type must be either 'tool_call' or 'final'")


def build_tool_protocol_prompt(registry: ToolRegistry) -> str:
    specs = json.dumps(
        registry.specs(),
        ensure_ascii=False,
        indent=2,
    )

    return f"""PAE RUNTIME TOOL PROTOCOL

You can either request exactly one runtime tool call or return the final answer.

AVAILABLE TOOLS
{specs}

ACTIVE PROJECT CONTEXT
- Primary repository: hssgj/PAE
- The authoritative current Discipline OS state is:
  discipline_os/current_state.json
- When the user asks for the current PAE focus, priority, milestone, next action,
  or asks you to check the current GitHub state, ALWAYS use github_read on that
  file before answering. Persisted copies may be stale.
- Do not claim you checked GitHub unless you actually request github_read.

OUTPUT CONTRACT
Return exactly ONE JSON object and nothing else.

To request a tool:
{{"type":"tool_call","name":"github_read","arguments":{{"repo":"hssgj/PAE","path":"discipline_os/current_state.json","ref":"main"}}}}

To answer the user:
{{"type":"final","content":"your answer here"}}

Rules:
- Never wrap the JSON in explanatory prose.
- Use only registered tool names.
- Tool arguments must follow the declared schema.
- If the user's request requires current external/source data, request the tool
  before answering.
- After receiving a TOOL RESULT, use it to answer or request another tool.
- Never invent a tool result.
"""


def _protocol_error_message(error: Exception) -> dict[str, str]:
    return {
        "role": "system",
        "content": (
            "PROTOCOL ERROR\n"
            f"{error}\n"
            "Return exactly one valid JSON object using the PAE RUNTIME TOOL "
            "PROTOCOL. Do not add prose or Markdown."
        ),
    }


def _tool_result_message(
    name: str,
    arguments: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, str]:
    return {
        "role": "system",
        "content": (
            "TOOL RESULT\n"
            f"Tool: {name}\n"
            "Arguments:\n"
            + json.dumps(arguments, ensure_ascii=False, indent=2)
            + "\nResult:\n"
            + json.dumps(result, ensure_ascii=False, indent=2)
            + "\n\nNow return exactly one JSON protocol object. "
            "Use type=final if you can answer the user."
        ),
    }


def _tool_error_message(
    name: str,
    arguments: dict[str, Any],
    error: Exception,
) -> dict[str, str]:
    return {
        "role": "system",
        "content": (
            "TOOL ERROR\n"
            f"Tool: {name}\n"
            "Arguments:\n"
            + json.dumps(arguments, ensure_ascii=False, indent=2)
            + f"\nError: {error}\n"
            "Correct the call if possible, or return a final answer explaining "
            "what could not be retrieved. Return exactly one JSON protocol object."
        ),
    }


def run_agent_turn(
    provider,
    messages: list[dict[str, str]],
    *,
    registry: ToolRegistry,
    context: ToolContext,
) -> str:
    working = list(messages)
    working.insert(
        1,
        {
            "role": "system",
            "content": build_tool_protocol_prompt(registry),
        },
    )

    tool_calls = 0

    while True:
        repairs = 0

        while True:
            raw = provider.chat(working)

            try:
                action = parse_agent_response(raw)
                break
            except AgentProtocolError as exc:
                if repairs >= MAX_PROTOCOL_REPAIRS:
                    raise AgentProtocolError(
                        f"model failed tool protocol after repair: {exc}; "
                        f"last response={raw!r}"
                    ) from exc

                print(f"[protocol repair] {exc}")
                working.append({"role": "assistant", "content": raw})
                working.append(_protocol_error_message(exc))
                repairs += 1

        if isinstance(action, FinalAnswer):
            return action.content

        if tool_calls >= MAX_TOOL_CALLS:
            raise AgentProtocolError(
                f"tool call limit exceeded ({MAX_TOOL_CALLS})"
            )

        tool_calls += 1
        print(
            "[tool] "
            + action.name
            + " "
            + json.dumps(action.arguments, ensure_ascii=False)
        )

        working.append(
            {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "type": "tool_call",
                        "name": action.name,
                        "arguments": action.arguments,
                    },
                    ensure_ascii=False,
                ),
            }
        )

        try:
            result = registry.execute(
                action.name,
                action.arguments,
                context=context,
            )
        except Exception as exc:
            print(f"[tool error] {action.name}: {exc}")
            working.append(
                _tool_error_message(
                    action.name,
                    action.arguments,
                    exc,
                )
            )
            continue

        working.append(
            _tool_result_message(
                action.name,
                action.arguments,
                result,
            )
        )
