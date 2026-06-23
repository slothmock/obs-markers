import importlib
import sys


def reload_metadata(monkeypatch, package_version=None, version_error=None):
    import importlib.metadata

    def fake_version(package_name):
        assert package_name == "marker-mate"
        if version_error is not None:
            raise version_error
        return package_version

    monkeypatch.setattr(importlib.metadata, "version", fake_version)
    sys.modules.pop("app.metadata", None)
    return importlib.import_module("app.metadata")


def test_metadata_uses_installed_package_version(monkeypatch):
    metadata = reload_metadata(monkeypatch, package_version="1.2.3")

    assert metadata.__version__ == "1.2.3"
    assert metadata.APP_INFO.version == "1.2.3"


def test_metadata_fallback_is_explicit_unknown_version(monkeypatch):
    metadata = reload_metadata(monkeypatch, version_error=ImportError("no metadata"))

    assert metadata.__version__ == "0.0.0+unknown"
    assert metadata.APP_INFO.version == "0.0.0+unknown"

