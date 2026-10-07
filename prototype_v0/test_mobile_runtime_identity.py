import mobile_server


def test_runtime_identity_exposes_safe_version_and_tools() -> None:
    info = mobile_server.RUNTIME.runtime_info()
    assert info["status"] == "ready"
    assert info["git_commit"]
    assert info["branch"]
    assert "github_read" in info["tools"]
    assert "github_list" in info["tools"]
    assert "github_search" in info["tools"]
    assert "github_prepare_write" in info["tools"]
    assert "github_apply_write" in info["tools"]
    assert "gmail_search" in info["tools"]
    assert "gmail_read" in info["tools"]
    assert "gmail_create_draft" in info["tools"]
    assert "gmail_send" in info["tools"]
    assert isinstance(info["gmail_configured"], bool)
    assert isinstance(info["github_configured"], bool)
    assert "token" not in info
    assert "secret" not in info
