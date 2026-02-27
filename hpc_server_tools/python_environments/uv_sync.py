# Project: Dotfiles  # noqa: INP001
# Author: Carel van Niekerk
# Year: 2026
# Group: Dialogue Systems and Machine Learning Group
# Institution: Heinrich Heine University Düsseldorf
# --------------------------------------------------------------------------------
#
# This code was generated with the help of AI writing assistants
# including GitHub Copilot, ChatGPT Codex, Claude Code, Gemini.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http: //www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Run uv sync with groups from .uvgroups file."""

import argparse
import subprocess
import sys
from pathlib import Path

# ANSI Color Codes
RESET = "\033[0m"
GRAY = "\033[00;30m"


def parse_uvgroups(path: Path) -> list[str]:
    """Parse the .uvgroups file and return uv sync flags.

    Args:
        path: Path to the .uvgroups file.

    Returns:
        List of flags to append to uv sync command.

    """
    if not path.exists():
        return []

    flags: list[str] = []
    content = path.read_text().strip()

    for line in content.splitlines():
        group = line.strip()
        if not group or group.startswith("#"):
            continue

        if group.lower() == "all":
            return ["--all-groups"]
        if group.lower() == "dev":
            flags.append("--dev")
        else:
            flags.append(f"--group={group}")
    
    flags = ["--all-groups"] if not flags else flags

    return flags


def main() -> int:
    """Run uv sync with parsed groups and optional flags.

    Returns:
        Exit code from uv sync command.

    """
    parser = argparse.ArgumentParser(
        description="Run uv sync with groups from .uvgroups file.",
    )
    parser.add_argument(
        "--upgrade",
        "-U",
        action="store_true",
        help="Upgrade all packages to the latest version.",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh the cache for all packages.",
    )
    args = parser.parse_args()

    # Build the command
    cmd = ["uv", "sync"]

    # Add groups from .uvgroups file
    uvgroups_path = Path.cwd() / ".uvgroups"
    cmd.extend(parse_uvgroups(uvgroups_path))

    # Add optional flags
    if args.upgrade:
        cmd.append("--upgrade")
    if args.refresh:
        cmd.append("--refresh")

    # Run the command
    print(f"{GRAY}Running: {' '.join(cmd)}{RESET}")
    result = subprocess.run(cmd, check=True)  # noqa: S603
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
