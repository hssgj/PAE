from __future__ import annotations

from github_source import fetch_github_file, source_name
from gmail_source import latest_message, list_messages, read_message
from tool_core import Tool, ToolContext, ToolRegistry


def _github_read(
    context: ToolContext,
    arguments: dict[str, object],
) -> dict[str, object]:
    repo = str(arguments["repo"])
    path = str(arguments["path"])
    ref = str(arguments.get("ref", "main"))

    fetched = fetch_github_file(repo, path, ref=ref)
    name = source_name(repo, path, ref=ref)

    status = context.store.upsert_source(
        context.session,
        source_id=name,
        name=name,
        content=fetched.content,
        metadata={
            "source_type": "github",
            "repo": repo,
            "path": path.lstrip("/"),
            "ref": ref,
            "github_blob_sha": fetched.blob_sha,
        },
    )

    return {
        "status": status,
        "source_id": name,
        "repo": repo,
        "path": path.lstrip("/"),
        "ref": ref,
        "github_blob_sha": fetched.blob_sha,
        "content": fetched.content,
    }


def build_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(
        Tool(
            name="github_read",
            description=(
                "Read one UTF-8 text file from a GitHub repository and persist "
                "or refresh it as a session source."
            ),
            argument_schema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Repository in owner/name form.",
                    },
                    "path": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Path to one text file inside the repository.",
                    },
                    "ref": {
                        "type": "string",
                        "minLength": 1,
                        "default": "main",
                        "description": "Branch, tag, or commit ref.",
                    },
                },
                "required": ["repo", "path"],
                "additionalProperties": False,
            },
            executor=_github_read,
        )
    )

    registry.register(
        Tool(
            name="gmail_list_messages",
            description="List 1 to 10 newest messages from the authorized Gmail inbox.",
            argument_schema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 5},
                },
                "additionalProperties": False,
            },
            executor=lambda context, arguments: list_messages(arguments["limit"]),
        )
    )

    registry.register(
        Tool(
            name="gmail_read_message",
            description="Read one Gmail message by its message ID.",
            argument_schema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "minLength": 1},
                },
                "required": ["message_id"],
                "additionalProperties": False,
            },
            executor=lambda context, arguments: read_message(arguments["message_id"]),
        )
    )

    registry.register(
        Tool(
            name="gmail_latest_message",
            description=(
                "Read the subject, sender and Prague-local date/time of the newest "
                "message in the authorized Gmail inbox."
            ),
            argument_schema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            executor=lambda context, arguments: latest_message(),
        )
    )

    return registry
