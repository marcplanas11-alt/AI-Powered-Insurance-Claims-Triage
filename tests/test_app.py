import sys
from unittest.mock import MagicMock, patch

# Stub out modules before importing app (app calls st.* at module level).
# button must return False so the triage block doesn't execute on import.
_st = MagicMock()
_st.button.return_value = False
sys.modules["streamlit"] = _st
sys.modules["anthropic"] = MagicMock()

import app  # noqa: E402


def _make_client(response_text="result"):
    client = MagicMock()
    message = MagicMock()
    message.content = [MagicMock(text=response_text)]
    client.messages.create.return_value = message
    return client


def test_get_client_passes_api_key():
    with patch("app.anthropic.Anthropic") as mock_anthropic:
        app.get_client("test-key-123")
        mock_anthropic.assert_called_once_with(api_key="test-key-123")


def test_intake_agent_returns_response():
    client = _make_client("## Intake\n- Type: Water damage")
    result = app.intake_agent(client, "Pipe burst in kitchen")
    assert result == "## Intake\n- Type: Water damage"


def test_intake_agent_includes_claim_in_prompt():
    client = _make_client("ok")
    app.intake_agent(client, "unique-claim-xyz")
    prompt = client.messages.create.call_args.kwargs["messages"][0]["content"]
    assert "unique-claim-xyz" in prompt


def test_intake_agent_uses_correct_model():
    client = _make_client("ok")
    app.intake_agent(client, "claim")
    assert client.messages.create.call_args.kwargs["model"] == "claude-sonnet-4-6"


def test_policy_agent_returns_response():
    client = _make_client("## Coverage\n- Covered: No")
    result = app.policy_agent(client, "intake output", "policy wording")
    assert result == "## Coverage\n- Covered: No"


def test_policy_agent_includes_intake_and_policy_in_prompt():
    client = _make_client("ok")
    app.policy_agent(client, "intake-data-abc", "policy-data-xyz")
    prompt = client.messages.create.call_args.kwargs["messages"][0]["content"]
    assert "intake-data-abc" in prompt
    assert "policy-data-xyz" in prompt


def test_decision_agent_returns_response():
    client = _make_client("ESCALATE\nReason: Corrosion exclusion applies")
    result = app.decision_agent(client, "intake output", "policy output")
    assert "ESCALATE" in result


def test_decision_agent_includes_both_outputs_in_prompt():
    client = _make_client("APPROVE")
    app.decision_agent(client, "intake-abc", "policy-xyz")
    prompt = client.messages.create.call_args.kwargs["messages"][0]["content"]
    assert "intake-abc" in prompt
    assert "policy-xyz" in prompt


def test_all_agents_use_max_tokens_400():
    client = _make_client("ok")
    app.intake_agent(client, "claim")
    assert client.messages.create.call_args.kwargs["max_tokens"] == 400

    client = _make_client("ok")
    app.policy_agent(client, "intake", "policy")
    assert client.messages.create.call_args.kwargs["max_tokens"] == 400

    client = _make_client("ok")
    app.decision_agent(client, "intake", "policy")
    assert client.messages.create.call_args.kwargs["max_tokens"] == 400
