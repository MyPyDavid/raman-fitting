from pathlib import Path
from types import MappingProxyType
import tomllib


def load_default_model_and_peak_definitions() -> MappingProxyType:
    DEFAULT_MODELS_DIR = Path(__file__).resolve().parent
    default_peak_settings = {}
    for i in DEFAULT_MODELS_DIR.glob("*.toml"):
        default_peak_settings.update(tomllib.loads(i.read_bytes().decode()))
    if not default_peak_settings:
        raise ValueError("default models should not be empty.")

    return MappingProxyType(default_peak_settings)
