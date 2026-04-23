import sys
from unittest.mock import MagicMock, patch

# Stub out modules before importing app (app calls st.* at module level).
# button must return False so the triage block doesn't execute on import.
_st = MagicMock()
_st.button.return_value = False
sys.modules["streamlit"] = _st
sys.modules["anthropic"] = MagicMock()
sys.modules["pypdf"] = MagicMock()

import app  # noqa: E402


def _make_client(response_text="result"):
    client = MagicMock()
    message = MagicMock()
    message.content = [MagicMock(text=response_text)]
    client.messages.create.return_value = message
    return client


# --- get_client ---

def test_get_client_passes_api_key():
    with patch("app.anthropic.Anthropic") as mock_anthropic:
        app.get_client("test-key-123")
        mock_anthropic.assert_called_once_with(api_key="test-key-123")


# --- intake_agent ---

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


# --- policy_agent ---

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


# --- decision_agent ---

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


def test_all_agents_use_max_tokens_700():
    client = _make_client("ok")
    app.intake_agent(client, "claim")
    assert client.messages.create.call_args.kwargs["max_tokens"] == 700

    client = _make_client("ok")
    app.policy_agent(client, "intake", "policy")
    assert client.messages.create.call_args.kwargs["max_tokens"] == 700

    client = _make_client("ok")
    app.decision_agent(client, "intake", "policy")
    assert client.messages.create.call_args.kwargs["max_tokens"] == 700


# --- extract_text_from_txt ---

def test_extract_text_from_txt():
    mock_file = MagicMock()
    mock_file.read.return_value = b"Hello claim text"
    result = app.extract_text_from_txt(mock_file)
    assert result == "Hello claim text"


# --- extract_text_from_pdf ---

def test_extract_text_from_pdf():
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Page one text"
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]

    with patch("app.PdfReader", return_value=mock_reader):
        mock_file = MagicMock()
        result = app.extract_text_from_pdf(mock_file)

    assert result == "Page one text"


def test_extract_text_from_pdf_skips_empty_pages():
    pages = [MagicMock(), MagicMock()]
    pages[0].extract_text.return_value = "Page one"
    pages[1].extract_text.return_value = None
    mock_reader = MagicMock()
    mock_reader.pages = pages

    with patch("app.PdfReader", return_value=mock_reader):
        result = app.extract_text_from_pdf(MagicMock())

    assert result == "Page one"


# --- load_input ---

def test_load_input_returns_sample_when_use_sample_true():
    app.use_sample = True
    result = app.load_input(None, "", "sample text")
    assert result == "sample text"
    app.use_sample = False


def test_load_input_returns_manual_text_when_provided():
    app.use_sample = False
    result = app.load_input(None, "  pasted text  ", "sample")
    assert result == "pasted text"


def test_load_input_returns_empty_when_no_file_and_no_text():
    app.use_sample = False
    result = app.load_input(None, "", "sample")
    assert result == ""


def test_load_input_reads_txt_file():
    app.use_sample = False
    mock_file = MagicMock()
    mock_file.name = "claim.txt"
    mock_file.read.return_value = b"file content"
    result = app.load_input(mock_file, "", "sample")
    assert result == "file content"


def test_load_input_reads_pdf_file():
    app.use_sample = False
    mock_file = MagicMock()
    mock_file.name = "claim.pdf"

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "pdf content"
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]

    with patch("app.PdfReader", return_value=mock_reader):
        result = app.load_input(mock_file, "", "sample")

    assert result == "pdf content"
