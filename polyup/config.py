"""Configurable defaults for Polygon sync. Override via SyncConfig."""

from dataclasses import dataclass, field


SOLUTION_TAGS: dict[str, str] = {
    "acc": "MA",
    "acc_java": "OK",
    "acc_alt": "OK",
    "brute": "TL",
    "wa": "WA",
}

SOURCE_TYPES: dict[str, str] = {
    ".cpp": "cpp.g++17",
    ".java": "java21",
}

STANDARD_CHECKERS: set[str] = {
    "wcmp", "ncmp", "nyesno", "yesno", "fcmp", "hcmp", "lcmp",
    "rcmp4", "rcmp6", "rcmp9",
}


@dataclass
class SyncConfig:
    time_limit_ms: int = 1000
    memory_limit_mb: int = 256
    input_file: str = "stdin"
    output_file: str = "stdout"
    statement_lang: str = "english"
    commit_message: str = "polyup auto-upload"
    api_delay: float = 0.3
    build_package: bool = True
    verify_package: bool = True
    solution_tags: dict[str, str] = field(default_factory=lambda: dict(SOLUTION_TAGS))
    source_types: dict[str, str] = field(default_factory=lambda: dict(SOURCE_TYPES))
    # login → READ | WRITE | NONE  (applied via problem.setAccess)
    access: dict[str, str] = field(default_factory=dict)
    grant_access: bool = True
