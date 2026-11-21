import pytest

import reliable_AI_app as app


# ---------- Fakes (pretend parts used instead of the real Gemini) ----------

class FakeAPIError(Exception):
    """A fake API error that carries a status code like 503."""

    def __init__(self, code, message="fake error"):
        super().__init__(message)
        self.code = code


class FakeResponse:
    def __init__(self, text):
        self.text = text


class FakeClient:
    """Pretends to be the Gemini client and records how it was used."""

    def __init__(self, reply_text):
        self.models = self
        self.reply_text = reply_text
        self.calls = 0
        self.last_contents = None

    def generate_content(self, model, contents):
        self.calls += 1
        self.last_contents = contents
        return FakeResponse(self.reply_text)


@pytest.fixture(autouse=True)
def no_waiting(monkeypatch):
    """Make time.sleep do nothing so retry tests run instantly."""
    monkeypatch.setattr(app.time, "sleep", lambda seconds: None)


# ---------- Tests for validate_message ----------

def test_empty_message_is_rejected():
    with pytest.raises(ValueError):
        app.validate_message("")


def test_spaces_only_message_is_rejected():
    with pytest.raises(ValueError):
        app.validate_message("     ")


def test_none_message_is_rejected():
    with pytest.raises(ValueError):
        app.validate_message(None)


def test_too_long_message_is_rejected():
    with pytest.raises(ValueError):
        app.validate_message("a" * (app.MAX_MESSAGE_LENGTH + 1))


def test_message_at_exact_limit_is_accepted():
    message = "a" * app.MAX_MESSAGE_LENGTH
    assert app.validate_message(message) == message


def test_message_is_stripped():
    assert app.validate_message("  hello  ") == "hello"


# ---------- Tests for call_with_retry ----------

def test_success_on_first_try_calls_once():
    calls = {"count": 0}

    def task():
        calls["count"] += 1
        return "ok"

    assert app.call_with_retry(task) == "ok"
    assert calls["count"] == 1


def test_retries_temporary_error_then_succeeds():
    calls = {"count": 0}

    def task():
        calls["count"] += 1
        if calls["count"] < 3:
            raise FakeAPIError(503)
        return "ok"

    assert app.call_with_retry(task) == "ok"
    assert calls["count"] == 3


def test_gives_up_after_max_attempts():
    calls = {"count": 0}

    def task():
        calls["count"] += 1
        raise FakeAPIError(503)

    with pytest.raises(FakeAPIError):
        app.call_with_retry(task)
    assert calls["count"] == app.MAX_ATTEMPTS


def test_does_not_retry_permanent_error():
    calls = {"count": 0}

    def task():
        calls["count"] += 1
        raise FakeAPIError(404)

    with pytest.raises(FakeAPIError):
        app.call_with_retry(task)
    assert calls["count"] == 1


def test_error_without_code_is_retried():
    calls = {"count": 0}

    def task():
        calls["count"] += 1
        if calls["count"] == 1:
            raise ConnectionError("network down")
        return "ok"

    assert app.call_with_retry(task) == "ok"
    assert calls["count"] == 2


# ---------- Tests for ask_gemini ----------

def test_ask_gemini_returns_the_reply(monkeypatch):
    fake = FakeClient("Hello from the shop!")
    monkeypatch.setattr(app, "get_client", lambda: fake)

    assert app.ask_gemini("Do you deliver?") == "Hello from the shop!"
    assert fake.calls == 1


@pytest.mark.parametrize("empty_reply", [None, "", "   "])
def test_empty_reply_gives_fallback(monkeypatch, empty_reply):
    fake = FakeClient(empty_reply)
    monkeypatch.setattr(app, "get_client", lambda: fake)

    assert app.ask_gemini("Do you deliver?") == app.FALLBACK_REPLY


def test_empty_input_never_calls_the_api(monkeypatch):
    fake = FakeClient("should not be used")
    monkeypatch.setattr(app, "get_client", lambda: fake)

    with pytest.raises(ValueError):
        app.ask_gemini("   ")
    assert fake.calls == 0


def test_prompt_contains_shop_info(monkeypatch):
    fake = FakeClient("ok")
    monkeypatch.setattr(app, "get_client", lambda: fake)

    app.ask_gemini("Do you deliver on Sundays?")
    assert app.SHOP_INFO in fake.last_contents
    assert "Do you deliver on Sundays?" in fake.last_contents


def test_missing_api_key_raises_clear_error(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(RuntimeError):
        app.get_client()