import sys, os
from dataclasses import dataclass

def _get_version() -> str:
    if getattr(sys, "frozen", False):
        return os.environ.get("OBS_MARKERS_VERSION", "0.0.0")

    try:
        from importlib.metadata import version
        return version("obs-markers")
    except Exception:
        return "0.0.0+unknown"

__version__ = _get_version()




@dataclass(frozen=True)
class AppMetadata:
    name: str = "OBS Markers"
    version: str = __version__
    author: str = "slothmock"
    description: str = "Log timestamp markers while recording in OBS."
    repo_url: str = "https://github.com/slothmock/obs-markers"
    license: str = "MIT"
    python: str = sys.version.split()[0]


APP_INFO = AppMetadata()
