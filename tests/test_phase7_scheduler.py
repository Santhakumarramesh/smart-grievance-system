import backend.app as app_module
from backend.config import Config


def test_scheduler_autostart_disabled_by_default(monkeypatch):
    starts = {"count": 0}

    monkeypatch.setattr(Config, "ENABLE_SCHEDULER", True)
    monkeypatch.setattr(Config, "SCHEDULER_AUTOSTART", False)
    monkeypatch.setattr(Config, "ENABLE_STARTUP_MODEL_LOAD", False)
    monkeypatch.setattr(app_module, "_is_flask_db_command", lambda: False)
    monkeypatch.setattr(
        app_module.scheduler,
        "start",
        lambda: starts.__setitem__("count", starts["count"] + 1),
    )

    app_module.create_app()
    assert starts["count"] == 0
