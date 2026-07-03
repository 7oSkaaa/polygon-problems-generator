"""Parse problem files — statement, tutorial, checker, generator script."""

import re
from pathlib import Path

from .config import STANDARD_CHECKERS


def parse_statement(tex_path: Path) -> dict[str, str]:
    text = tex_path.read_text()
    result = {"legend": "", "input": "", "output": "", "notes": "", "interaction": ""}

    # Try comment-header format: % ─── Legend ───
    sections = re.split(
        r"^%\s*─+\s*(Title|Legend|Input|Output|Notes|Interaction)\s*─+\s*$",
        text, flags=re.MULTILINE,
    )
    if len(sections) > 1:
        for i in range(1, len(sections) - 1, 2):
            key = sections[i].lower()
            if key == "title":
                continue
            val = re.sub(r"^%.*\n", "", sections[i + 1], flags=re.MULTILINE).strip()
            if key in result:
                result[key] = val
        return result

    # Fallback: \InputFile / \OutputFile / \Note LaTeX commands
    parts = re.split(
        r"^\\(InputFile|OutputFile|Note)\b.*$",
        text, flags=re.MULTILINE,
    )
    if len(parts) > 1:
        _TAG_MAP = {"InputFile": "input", "OutputFile": "output", "Note": "notes"}
        # Everything before the first command is the legend (strip title line)
        legend = re.sub(r"\\textbf\{\\Large\s+.*?\}\s*", "", parts[0]).strip()
        result["legend"] = legend
        for i in range(1, len(parts) - 1, 2):
            key = _TAG_MAP.get(parts[i])
            if key:
                result[key] = parts[i + 1].strip()
        return result

    return result


def parse_tutorial(tex_path: Path) -> str:
    text = tex_path.read_text()
    return re.sub(r"^%.*\n", "", text, flags=re.MULTILINE).strip()


def detect_standard_checker(checker_path: Path) -> str | None:
    text = checker_path.read_text()
    m = re.search(r"standard checker:\s*(\w+)", text, re.IGNORECASE)
    if m and m.group(1) in STANDARD_CHECKERS:
        return m.group(1)
    return None


def extract_freemarker_script(generator_path: Path) -> str | None:
    text = generator_path.read_text()
    m = re.search(
        r"FreeMarker script.*?:\s*\n(.*?)(?:\*/|$)",
        text, re.DOTALL | re.IGNORECASE,
    )
    return m.group(1).strip() if m else None


def detect_problem_name(problem_dir: Path) -> str:
    stmt = problem_dir / "statement" / "statement.tex"
    if stmt.exists():
        m = re.search(r"\\textbf\{\\Large\s+(.*?)\}", stmt.read_text())
        if m:
            return m.group(1)
    return problem_dir.name.replace("_", " ").title()
