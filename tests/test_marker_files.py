from pathlib import Path

from app.marker_files import MarkerFileManager


def test_marker_file_manager_writes_session_and_markers(tmp_path):
    manager = MarkerFileManager()
    manager.set_base_dir(str(tmp_path))

    path = Path(manager.new_file())
    manager.session_start()
    manager.write_marker("00:00:03", "Note")
    manager.session_end("00:00:05")

    assert path.parent == tmp_path
    assert path.name.startswith("markers_")
    assert path.name.endswith(".txt")
    assert path.read_text(encoding="utf-8").splitlines() == [
        path.read_text(encoding="utf-8").splitlines()[0],
        "00:00:03 Note",
        "=== SESSION END | Duration: 00:00:05 ===",
    ]
    assert path.read_text(encoding="utf-8").splitlines()[0].startswith("=== SESSION START ")


def test_marker_file_manager_requires_base_dir_for_new_file():
    manager = MarkerFileManager()

    try:
        manager.new_file()
    except RuntimeError as exc:
        assert str(exc) == "Marker directory not set"
    else:
        raise AssertionError("Expected RuntimeError when marker directory is missing")
