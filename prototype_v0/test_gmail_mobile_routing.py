from agent_loop import ToolCall, _format_required_result, required_tool_call


def test_czech_latest_gmail_request_is_forced_to_tool() -> None:
    messages = [
        {
            "role": "user",
            "content": (
                "Teď se koukni do Gmailu a přečti mi předmět, jméno "
                "odesílatele a čas posledního e-mailu."
            ),
        }
    ]
    assert required_tool_call(messages) == ToolCall(
        name="gmail_latest_message", arguments={}
    )


def test_latest_gmail_result_is_returned_without_model_promise() -> None:
    answer = _format_required_result(
        ToolCall(name="gmail_latest_message", arguments={}),
        {
            "subject": "Test subject",
            "sender_name": "Sender",
            "sender_email": "sender@example.com",
            "date_local": "07. 10. 2026 17:55:00 CEST",
            "message_id": "abc123",
        },
    )
    assert answer == (
        "Předmět: Test subject\n"
        "Odesílatel: Sender <sender@example.com>\n"
        "Čas: 07. 10. 2026 17:55:00 CEST\n"
        "Message ID: abc123"
    )
