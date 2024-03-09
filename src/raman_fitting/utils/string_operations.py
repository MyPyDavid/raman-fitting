def join_prefix_suffix(prefix: str, suffix: str) -> str:
    prefix_ = prefix.rstrip("_")
    suffix_ = suffix.lstrip("_")
    if prefix.endswith(suffix_):
        return prefix_
    return f"{prefix_}_{suffix_}"
