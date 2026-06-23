import importlib
import logging
import sys
import types
from pathlib import Path


def install_runtime_stubs(monkeypatch):
    hotkey_calls = []
    keyboard = types.SimpleNamespace(
        unhook_all=lambda: hotkey_calls.append(("unhook_all",)),
        add_hotkey=lambda *args, **kwargs: hotkey_calls.append(("add_hotkey", args, kwargs)),
    )
    monkeypatch.setitem(sys.modules, "keyboard", keyboard)

    obs_mod = types.ModuleType("obsws_python")

    class FakeReqClient:
        def __init__(self, *args, **kwargs):
            pass

        def get_stats(self):
            raise ConnectionRefusedError("OBS unavailable in tests")

    class FakeRequestError(Exception):
        code = None

    setattr(obs_mod, "ReqClient", FakeReqClient)
    setattr(obs_mod, "reqs", types.SimpleNamespace(
        OBSSDKError=Exception,
        OBSSDKRequestError=FakeRequestError,
    ))
    monkeypatch.setitem(sys.modules, "obsws_python", obs_mod)

    for name in [
        "app.core",
        "app.hotkeys",
        "app.obs",
    ]:
        sys.modules.pop(name, None)

    return hotkey_calls


def make_app(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    install_runtime_stubs(monkeypatch)
    core = importlib.import_module("app.core")
    return core.MarkerApp(logging.getLogger("test-marker-mate"))


def test_new_marker_file_is_owned_by_core(monkeypatch, tmp_path):
    app = make_app(monkeypatch, tmp_path)
    app.set_marker_directory(str(tmp_path / "markers"))

    path = app.new_marker_file()

    assert path is not None
    assert Path(path).exists()
    assert app.markers.current_path == path


def test_new_marker_file_is_ignored_during_active_session(monkeypatch, tmp_path):
    app = make_app(monkeypatch, tmp_path)
    app.set_marker_directory(str(tmp_path / "markers"))
    first_path = app.new_marker_file()
    app.session_active = True

    assert app.new_marker_file() is None
    assert app.markers.current_path == first_path


def test_start_session_creates_a_fresh_marker_file(monkeypatch, tmp_path):
    app = make_app(monkeypatch, tmp_path)
    app.set_marker_directory(str(tmp_path / "markers"))

    app._start_session()
    first_path = app.markers.current_path
    app.add_marker("note")
    app._end_session()

    app._start_session()
    second_path = app.markers.current_path
    app.add_marker("note")
    app._end_session()

    assert first_path != second_path
    assert Path(first_path).read_text(encoding="utf-8").count("SESSION START") == 1
    assert Path(second_path).read_text(encoding="utf-8").count("SESSION START") == 1


def test_new_file_hotkey_dispatch_calls_core_method(monkeypatch, tmp_path):
    app = make_app(monkeypatch, tmp_path)
    app.set_marker_directory(str(tmp_path / "markers"))

    app.hotkeys._dispatch("new_file")

    assert app.markers.current_path is not None
    assert Path(app.markers.current_path).exists()
