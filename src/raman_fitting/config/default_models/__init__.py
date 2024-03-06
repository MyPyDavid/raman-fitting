from pathlib import Path
from types import MappingProxyType
import tomllib


def load_config_from_toml_files() -> MappingProxyType:
    current_parent_dir = Path(__file__).resolve().parent
    default_peak_settings = {}
    for i in current_parent_dir.glob("*.toml"):
        default_peak_settings.update(tomllib.loads(i.read_bytes().decode()))
    if not default_peak_settings:
        raise ValueError("default models should not be empty.")

    return MappingProxyType(default_peak_settings)
