from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any

from tool_core import ToolContext, ToolRegistry


MAX_TOOL_CALLS = 3
MAX_PROTOCOL_REPAIRS = 1
DISCIPLINE_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])(discipline_os/[A-Za-z0-9_./-]+\.(?:json|md|txt))(?![A-Za-z0-9_.-])",
    re.IGNORECASE,
)


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
        # Plain text is a valid final answer. Only JSON-looking output is treated
        # as a broken tool-protocol attempt.
        if raw.lstrip().startswith("{"):
            raise AgentProtocolError(
                "malformed JSON tool/final response"
            ) from exc
        return FinalAnswer(content=raw.strip())

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



def build_session_facts_prompt(context: ToolContext) -> str:
    message_count = len(context.session.messages)
    source_count = len(context.session.sources)

    return (
        "SESSION RUNTIME FACTS\n"
        f"Session id: {context.session.session_id}\n"
        f"Persisted chat messages currently loaded: {message_count}\n"
        f"Persisted sources currently loaded: {source_count}\n"
        "The user/assistant messages supplied to this turn are persistent session "
        "history. If the persisted chat message count is greater than 1, do not "
        "claim that this is the first message or that prior chat history is absent."
    )


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_]+", _normalize_text(text))


def _approx_any(tokens: list[str], targets: set[str], cutoff: float = 0.78) -> bool:
    for token in tokens:
        for target in targets:
            if token == target:
                return True
            if len(token) >= 4 and SequenceMatcher(None, token, target).ratio() >= cutoff:
                return True
    return False


def _last_user_text(messages: list[dict[str, str]]) -> str:
    for message in reversed(messages):
        if message.get("role") == "user":
            return message.get("content", "")
    return ""


def required_tool_call(messages: list[dict[str, str]]) -> ToolCall | None:
    """Return a deterministic minimum tool call when source freshness is mandatory."""
    user_text = _last_user_text(messages)
    if not user_text:
        return None

    explicit_path = DISCIPLINE_PATH_RE.search(user_text)
    if explicit_path:
        return ToolCall(
            name="github_read",
            arguments={
                "repo": "hssgj/PAE",
                "path": explicit_path.group(1),
                "ref": "main",
            },
        )

    tokens = _tokens(user_text)

    freshness_terms = {
        "current",
        "curent",
        "fresh",
        "aktualni",
        "aktual",
        "autoritativni",
        "authoritative",
        "latest",
        "ted",
        "tedka",
    }
    state_terms = {
        "focus",
        "foks",
        "state",
        "stav",
        "priority",
        "priorita",
        "milestone",
        "next",
        "action",
        "akce",
        "dalsi",
    }

    mentions_freshness = _approx_any(tokens, freshness_terms)
    mentions_state = _approx_any(tokens, state_terms)

    if mentions_freshness and mentions_state:
        return ToolCall(
            name="github_read",
            arguments={
                "repo": "hssgj/PAE",
                "path": "discipline_os/current_state.json",
                "ref": "main",
            },
        )

    return None


def _same_required_call(candidate: ToolCall, required: ToolCall) -> bool:
    if candidate.name != required.name:
        return False

    for key, value in required.arguments.items():
        if candidate.arguments.get(key) != value:
            return False

    return True


def user_forbids_tools(messages: list[dict[str, str]]) -> bool:
    """Detect explicit history-only/no-GitHub instructions for this turn."""
    user_text = _last_user_text(messages)
    tokens = _tokens(user_text)
    normalized = _normalize_text(user_text)

    mentions_github = _approx_any(tokens, {"github", "githbu", "git"})
    mentions_tool = _approx_any(tokens, {"tool", "nastroj"})

    if "bez" in tokens and (mentions_github or mentions_tool):
        return True
    if "without" in tokens and (mentions_github or mentions_tool):
        return True
    if "no" in tokens and mentions_tool:
        return True
    if "nepouzivej" in normalized and (mentions_github or mentions_tool):
        return True
    if "dont use" in normalized and (mentions_github or mentions_tool):
        return True

    return False


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
            + "\n\nUse the tool result to answer the user normally in plain text, "
            "or request another tool with one JSON tool_call object."
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
            "Use this error to answer the user normally in plain text, or correct "
            "the call with one JSON tool_call object if another attempt is justified."
        ),
    }




def _append_tool_attempt(
    working: list[dict[str, str]],
    action: ToolCall,
    *,
    registry: ToolRegistry,
    context: ToolContext,
) -> bool:
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
        return False

    working.append(
        _tool_result_message(
            action.name,
            action.arguments,
            result,
        )
    )
    return True


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
    working.insert(
        2,
        {
            "role": "system",
            "content": build_session_facts_prompt(context),
        },
    )
    working.insert(
        3,
        {
            "role": "system",
            "content": (
                "HISTORY RULES\n"
                "When the user asks what they said, named, defined, or meant earlier, "
                "search the persisted user/assistant history supplied in this request. "
                "Use exact earlier user wording when available. Never substitute the "
                "session id, a source path, or a guessed value for a requested literal. "
                "If the literal is absent, say it is unknown."
            ),
        },
    )

    required = required_tool_call(messages)
    forbid_optional_tools = required is None and user_forbids_tools(messages)
    tool_calls = 0

    # If the runtime can deterministically prove a fresh/source read is required,
    # execute it before asking the model. The model does not get to bypass it.
    if required is not None:
        print(
            "[tool guard] required "
            + required.name
            + " "
            + json.dumps(required.arguments, ensure_ascii=False)
        )
        tool_calls += 1
        _append_tool_attempt(
            working,
            required,
            registry=registry,
            context=context,
        )

    forbidden_attempts = 0

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

        if forbid_optional_tools:
            forbidden_attempts += 1
            print(
                "[tool guard] tool rejected; user requested history-only/no-tool answer: "
                + action.name
            )
            if forbidden_attempts > 1:
                raise AgentProtocolError(
                    "model repeatedly requested a tool despite explicit no-tool instruction"
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
            working.append(
                {
                    "role": "system",
                    "content": (
                        "TOOL CALL REJECTED BY RUNTIME\n"
                        "The user explicitly requested a history-only/no-tool answer. "
                        "Do not call GitHub or any tool for this turn. Search the supplied "
                        "persisted chat history and answer from it. If the requested fact "
                        "is not present there, say UNKNOWN."
                    ),
                }
            )
            continue

        if tool_calls >= MAX_TOOL_CALLS:
            raise AgentProtocolError(
                f"tool call limit exceeded ({MAX_TOOL_CALLS})"
            )

        tool_calls += 1
        _append_tool_attempt(
            working,
            action,
            registry=registry,
            context=context,
        )
