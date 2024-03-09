def get_package_version() -> str:
    try:
        import importlib.metadata

        _version = importlib.metadata.version("raman_fitting")
    except ImportError:
        _version = "version.not.found"

    _version_text = f"raman_fitting version: {_version}"
    return _version_text
