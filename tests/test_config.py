from repopulse.config import load_db_settings


def test_settings_come_from_environment(monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "dbhost")
    monkeypatch.setenv("POSTGRES_PORT", "6543")
    monkeypatch.setenv("POSTGRES_USER", "u")
    monkeypatch.setenv("POSTGRES_PASSWORD", "p")
    monkeypatch.setenv("POSTGRES_DB", "d")

    settings = load_db_settings()

    assert settings.host == "dbhost"
    assert settings.port == 6543
    assert "dbname=d" in settings.dsn
