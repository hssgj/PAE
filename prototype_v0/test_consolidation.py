"""Regression checks at the boundary between main and the mobile branch."""
import json

from agent_loop import run_agent_turn
from sessions import SessionStore
from test_github_routing import FakeContext, FakeProvider, FakeRegistry, USER_REQUEST


def test_exact_file_task_does_not_approve_pending_write():
    context = FakeContext()
    context.session.pending_actions['github_write'] = {
        'approved': False,
        'prepared': {'repo':'hssgj/PAE','path':'untouched.md','content':'x'},
    }
    registry = FakeRegistry()
    result = run_agent_turn(FakeProvider(['Porovnání hotovo.']), [{'role':'user','content':USER_REQUEST}], registry=registry, context=context)
    assert result == 'Porovnání hotovo.'
    assert len(registry.calls) == 2
    assert context.session.pending_actions['github_write']['approved'] is False


def test_old_session_without_pending_actions_still_loads(tmp_path):
    store = SessionStore(tmp_path)
    session = store.open_or_create('old-session', system_prompt='test')
    data = json.loads(store.path_for(session.session_id).read_text())
    del data['pending_actions']
    store.path_for(session.session_id).write_text(json.dumps(data))
    loaded = store.load(session.session_id)
    assert loaded.pending_actions == {}
