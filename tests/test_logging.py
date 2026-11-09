import json
import logging

from astk.logging import configure_logging


def test_configure_logging_emits_json_with_app_name_and_run_id(capsys):
    run_id = configure_logging("demo-service", level="INFO", json_output=True)

    logging.getLogger("demo").info("hello world")

    captured = capsys.readouterr().out.strip().splitlines()
    assert len(captured) == 1
    payload = json.loads(captured[-1])

    assert payload["app"] == "demo-service"
    assert payload["run_id"] == run_id
    assert payload["message"] == "hello world"
    assert payload["level"] == "INFO"


def test_configure_logging_plain_text_mode(capsys):
    run_id = configure_logging("demo-service", level="DEBUG", json_output=False)

    logging.getLogger("demo").debug("plain line")

    out = capsys.readouterr().out
    assert f"demo-service:{run_id}" in out
    assert "plain line" in out


def test_configure_logging_returns_new_run_id_each_call():
    first = configure_logging("svc")
    second = configure_logging("svc")
    assert first != second


def test_json_output_includes_exc_info_for_logged_exceptions(capsys):
    configure_logging("demo-service", json_output=True)

    try:
        raise ValueError("boom")
    except ValueError:
        logging.getLogger("demo").exception("failed")

    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])

    assert payload["message"] == "failed"
    assert "ValueError: boom" in payload["exc_info"]


def test_json_output_omits_exc_info_when_no_exception(capsys):
    configure_logging("demo-service", json_output=True)

    logging.getLogger("demo").info("fine")

    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert "exc_info" not in payload
