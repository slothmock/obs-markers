import sys, os
from dataclasses import dataclass

def _get_version():
    try:
        from importlib.metadata import version
        return version("obs-markers")
    except Exception:
        from app.version import __version__
        return __version__

__version__ = _get_version()


@dataclass(frozen=True)
class AppMetadata:
    name: str = "OBS Markers"
    version: str = __version__
    author: str = "Jordan 'sloth' Mock"
    description: str = "Log timestamp markers while recording in OBS."
    repo_url: str = "https://github.com/slothmock/obs-markers"
    license: str = "MIT"
    python: str = sys.version.split()[0]


APP_INFO = AppMetadata()
