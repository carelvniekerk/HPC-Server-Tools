# coding=utf-8
# --------------------------------------------------------------------------------
# Project: Hilbert HPC Server Tools
# Author: Carel van Niekerk
# Year: 2024
# Group: Dialogue Systems and Machine Learning Group
# Institution: Heinrich Heine University Düsseldorf
# --------------------------------------------------------------------------------
#
# This code was generated with the help of AI writing assistants
# including GitHub Copilot, ChatGPT, Bing Chat.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Get the path to the virtual environment of a project."""

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from pathlib import Path


def get_venv_path(path: Path) -> Path:
    """Get the path to the virtual environment of a project."""
    path = path.resolve()

    if (path / ".venv").is_dir():
        return path / ".venv"

    for parent in path.parents:
        if (parent / ".venv").is_dir():
            return parent / ".venv"

    msg = "No .venv found in the path"
    raise FileNotFoundError(msg)


def main() -> None:
    """Get the path to the virtual environment of a project."""
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-p",
        "--path",
        type=Path,
        default=".",
        help="Path to the project",
    )
    path: Path = parser.parse_args().path

    path = get_venv_path(path)

    activation_script_path = path / "bin" / "activate"

    print(activation_script_path)


if __name__ == "__main__":
    main()
