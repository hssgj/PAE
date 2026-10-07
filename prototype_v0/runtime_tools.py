from __future__ import annotations

from github_source import (
    apply_github_write,
    fetch_github_file,
    list_github_path,
    prepare_github_write,
    search_github,
    source_name,
)
from gmail_source import create_draft, read_message, search_messages, send_draft
from tool_core import Tool, ToolContext, ToolError, ToolRegistry


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


def _gmail_search(context: ToolContext, arguments: dict[str, object]) -> dict[str, object]:
    return search_messages(str(arguments["query"]), int(arguments["limit"]))


def _github_list(context: ToolContext, arguments: dict[str, object]) -> dict[str, object]:
    return list_github_path(
        str(arguments["repo"]),
        str(arguments.get("path", "")),
        ref=str(arguments.get("ref", "main")),
        limit=int(arguments.get("limit", 50)),
    )


def _github_search(context: ToolContext, arguments: dict[str, object]) -> dict[str, object]:
    return search_github(
        str(arguments["repo"]),
        str(arguments["query"]),
        ref=str(arguments.get("ref", "main")),
        limit=int(arguments.get("limit", 10)),
    )


def _github_prepare_write(context: ToolContext, arguments: dict[str, object]) -> dict[str, object]:
    result = prepare_github_write(
        str(arguments["repo"]),
        str(arguments["path"]),
        str(arguments["content"]),
        branch=str(arguments.get("branch", "main")),
    )
    context.session.pending_actions["github_write"] = {
        "prepared": result,
        "approved": False,
    }
    context.store.save(context.session)
    return result


def _github_apply_write(context: ToolContext, arguments: dict[str, object]) -> dict[str, object]:
    pending = context.session.pending_actions.get("github_write")
    if not pending:
        raise ToolError("CONFIRMATION_REQUIRED: no GitHub write is pending in this session")
    if pending.get("approved") is not True:
        raise ToolError("CONFIRMATION_REQUIRED: user has not explicitly confirmed this GitHub write")
    prepared = pending.get("prepared")
    if not isinstance(prepared, dict):
        raise ToolError("CONFIRMATION_REQUIRED: pending GitHub write is invalid")
    try:
        result = apply_github_write(prepared)
    except Exception:
        pending["approved"] = False
        context.store.save(context.session)
        raise
    del context.session.pending_actions["github_write"]
    context.store.save(context.session)
    return result


def _gmail_read(context: ToolContext, arguments: dict[str, object]) -> dict[str, object]:
    return read_message(
        message_id=str(arguments.get("message_id", "")),
        thread_id=str(arguments.get("thread_id", "")),
    )


def _gmail_create_draft(context: ToolContext, arguments: dict[str, object]) -> dict[str, object]:
    result = create_draft(
        to=str(arguments["to"]),
        cc=str(arguments.get("cc", "")),
        subject=str(arguments["subject"]),
        body=str(arguments["body"]),
        thread_id=str(arguments.get("thread_id", "")),
        reply_to_message_id=str(arguments.get("reply_to_message_id", "")),
    )
    context.session.pending_actions["gmail_send"] = {
        "draft_id": result["draft_id"],
        "preview": result["preview"],
        "approved": False,
    }
    context.store.save(context.session)
    return result


def _gmail_send(context: ToolContext, arguments: dict[str, object]) -> dict[str, object]:
    draft_id = str(arguments["draft_id"])
    pending = context.session.pending_actions.get("gmail_send")
    if not pending or pending.get("draft_id") != draft_id:
        raise ToolError("CONFIRMATION_REQUIRED: draft is not pending in this session")
    if pending.get("approved") is not True:
        raise ToolError("CONFIRMATION_REQUIRED: user has not explicitly confirmed this draft")
    try:
        result = send_draft(draft_id)
    except Exception:
        pending["approved"] = False
        context.store.save(context.session)
        raise
    del context.session.pending_actions["gmail_send"]
    context.store.save(context.session)
    return result


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
            name="gmail_search",
            description=(
                "Search live Gmail using Gmail search syntax. Returns up to 10 compact "
                "message records with ids, sender, recipients, subject, local date and snippet."
            ),
            argument_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "default": "in:inbox"},
                    "limit": {"type": "integer", "default": 5},
                },
                "additionalProperties": False,
            },
            executor=_gmail_search,
        )
    )

    registry.register(
        Tool(
            name="github_list",
            description="List a bounded GitHub repository directory. Empty path lists the repository root.",
            argument_schema={
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "minLength": 3},
                    "path": {"type": "string", "default": ""},
                    "ref": {"type": "string", "default": "main"},
                    "limit": {"type": "integer", "default": 50},
                },
                "required": ["repo"],
                "additionalProperties": False,
            },
            executor=_github_list,
        )
    )

    registry.register(
        Tool(
            name="github_search",
            description=(
                "Search filenames and text inside exactly one GitHub repository. "
                "Returns bounded matching paths and snippets."
            ),
            argument_schema={
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "minLength": 3},
                    "query": {"type": "string", "minLength": 1},
                    "ref": {"type": "string", "default": "main"},
                    "limit": {"type": "integer", "default": 10},
                },
                "required": ["repo", "query"],
                "additionalProperties": False,
            },
            executor=_github_search,
        )
    )

    registry.register(
        Tool(
            name="github_prepare_write",
            description=(
                "Prepare creation or update of one UTF-8 text file and return a diff. "
                "This does not write to GitHub and requires separate explicit confirmation."
            ),
            argument_schema={
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "minLength": 3},
                    "path": {"type": "string", "minLength": 1},
                    "content": {"type": "string"},
                    "branch": {"type": "string", "default": "main"},
                },
                "required": ["repo", "path", "content"],
                "additionalProperties": False,
            },
            executor=_github_prepare_write,
        )
    )

    registry.register(
        Tool(
            name="github_apply_write",
            description=(
                "Apply the one pending GitHub text-file write. Runtime permits this only "
                "after a separate explicit user confirmation."
            ),
            argument_schema={"type": "object", "properties": {}, "additionalProperties": False},
            executor=_github_apply_write,
        )
    )

    registry.register(
        Tool(
            name="gmail_read",
            description=(
                "Read one live Gmail message or thread as bounded plain text. Supply "
                "exactly one of message_id or thread_id from gmail_search."
            ),
            argument_schema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "default": ""},
                    "thread_id": {"type": "string", "default": ""},
                },
                "additionalProperties": False,
            },
            executor=_gmail_read,
        )
    )

    registry.register(
        Tool(
            name="gmail_create_draft",
            description=(
                "Create a Gmail draft and store it as the one pending send action in this "
                "session. This never sends the message. Show the returned preview and ask "
                "for explicit confirmation."
            ),
            argument_schema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "minLength": 3},
                    "cc": {"type": "string", "default": ""},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                    "thread_id": {"type": "string", "default": ""},
                    "reply_to_message_id": {"type": "string", "default": ""},
                },
                "required": ["to", "subject", "body"],
                "additionalProperties": False,
            },
            executor=_gmail_create_draft,
        )
    )

    registry.register(
        Tool(
            name="gmail_send",
            description=(
                "Send the one pending Gmail draft by draft_id. Runtime rejects this unless "
                "the current user message explicitly confirms sending that pending draft."
            ),
            argument_schema={
                "type": "object",
                "properties": {"draft_id": {"type": "string", "minLength": 1}},
                "required": ["draft_id"],
                "additionalProperties": False,
            },
            executor=_gmail_send,
        )
    )

    return registry
