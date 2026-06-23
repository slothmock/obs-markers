import json
from pathlib import Path

from app.config import OBSMarkerConfig


def test_config_loads_existing_dict_config(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    config = OBSMarkerConfig()
    Path(config.config_path).write_text(
        json.dumps({"obs": {"host": "example.test", "port": 4455}}),
        encoding="utf-8",
    )

    config = OBSMarkerConfig()

    assert config["obs"]["host"] == "example.test"
    assert not list(Path(config.config_dir).glob("config.json.corrupt-*"))


def test_corrupt_json_config_is_backed_up_and_reset(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    config = OBSMarkerConfig()
    config_path = Path(config.config_path)
    config_path.write_text('{"obs": ', encoding="utf-8")

    config = OBSMarkerConfig()

    assert dict(config) == {}
    assert not config_path.exists()
    backups = list(Path(config.config_dir).glob("config.json.corrupt-*"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == '{"obs": '


def test_corrupt_json_config_logs_backup_path(tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    config = OBSMarkerConfig()
    config_path = Path(config.config_path)
    config_path.write_text("not json", encoding="utf-8")

    OBSMarkerConfig()

    assert "Invalid config moved to" in caplog.text
    assert "starting with defaults" in caplog.text


def test_non_object_json_config_is_backed_up_and_reset(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    config = OBSMarkerConfig()
    config_path = Path(config.config_path)
    config_path.write_text('["not", "an", "object"]', encoding="utf-8")

    config = OBSMarkerConfig()

    assert dict(config) == {}
    assert not config_path.exists()
    backups = list(Path(config.config_dir).glob("config.json.corrupt-*"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == '["not", "an", "object"]'


def test_ensure_obs_config_recreates_config_after_corrupt_backup(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    config = OBSMarkerConfig()
    config_path = Path(config.config_path)
    config_path.write_text("not json", encoding="utf-8")

    config = OBSMarkerConfig()
    loaded = config.ensure_obs_config()

    assert loaded["obs"] == {
        "host": "localhost",
        "port": 4455,
        "password": None,
    }
    assert config_path.exists()
    assert json.loads(config_path.read_text(encoding="utf-8")) == loaded
    assert len(list(Path(config.config_dir).glob("config.json.corrupt-*"))) == 1
