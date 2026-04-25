"""Scanner for .env files."""

import re
from pathlib import Path
from typing import Dict, List, Optional

# .env file patterns
ENV_PATTERNS = [".env", ".env.local", ".env.development", ".env.production", ".env.test", ".env.*"]

# High-risk patterns (AWS keys, private keys, etc.)
HIGH_RISK_PATTERNS = [
    r"AWS_ACCESS_KEY_ID\s*=\s*['\"]?AKIA[0-9A-Z]{16}",
    r"AWS_SECRET_ACCESS_KEY\s*=\s*['\"]?[0-9a-zA-Z/+=]{40}",
    r"PRIVATE_KEY\s*=\s*['\"]?",
    r"API_KEY\s*=\s*['\"]?[a-zA-Z0-9]{20,}",
    r"SECRET\s*=\s*['\"]?[a-zA-Z0-9]{20,}",
]


def scan_directory(directory: Path) -> List[Dict]:
    """
    Scan directory for .env files.

    Args:
        directory: Directory to scan

    Returns:
        List of found .env files with metadata
    """
    results = []

    for pattern in ENV_PATTERNS:
        for env_file in directory.glob(pattern):
            if env_file.is_file():
                info = analyze_env_file(env_file)
                results.append(info)

    return results


def analyze_env_file(filepath: Path) -> Dict:
    """
    Analyze .env file.

    Args:
        filepath: .env file path

    Returns:
        Dict with path, variables, risks, gitignore_status
    """
    try:
        content = filepath.read_text()
        variables = parse_env_variables(content)
        high_risk = detect_high_risk(content)
        in_gitignore = check_gitignore(filepath)

        return {
            "path": str(filepath),
            "name": filepath.name,
            "variables": len(variables),
            "high_risk": high_risk,
            "in_gitignore": in_gitignore,
            "size": filepath.stat().st_size,
        }
    except Exception as e:
        return {
            "path": str(filepath),
            "error": str(e),
        }


def parse_env_variables(content: str) -> List[str]:
    """
    Parse .env file and extract variable names.

    Args:
        content: .env file content

    Returns:
        List of variable names
    """
    variables = []

    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if "=" in line:
            name = line.split("=")[0].strip()
            variables.append(name)

    return variables


def detect_high_risk(content: str) -> List[str]:
    """
    Detect high-risk patterns in content.

    Args:
        content: File content

    Returns:
        List of detected risk types
    """
    risks = []

    for pattern in HIGH_RISK_PATTERNS:
        if re.search(pattern, content):
            risks.append(pattern.split("\\s")[0].replace("['\"]?", ""))

    return risks


def check_gitignore(filepath: Path) -> bool:
    """
    Check if .env file is in .gitignore.

    Args:
        filepath: .env file path

    Returns:
        True if in .gitignore
    """
    # Check parent directory for .gitignore
    gitignore = filepath.parent / ".gitignore"

    if not gitignore.exists():
        # Check git root
        try:
            git_root = find_git_root(filepath.parent)
            if git_root:
                gitignore = git_root / ".gitignore"
        except Exception:
            return False

    if not gitignore.exists():
        return False

    try:
        gitignore_content = gitignore.read_text()
        filename = filepath.name

        for line in gitignore_content.split("\n"):
            line = line.strip()
            if line.startswith("#"):
                continue
            if line == filename or line == ".env" or line == ".env.*":
                return True

        return False
    except Exception:
        return False


def find_git_root(directory: Path) -> Optional[Path]:
    """
    Find git repository root.

    Args:
        directory: Starting directory

    Returns:
        Git root path or None
    """
    current = directory

    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent

    return None