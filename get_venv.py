# coding=utf-8
# --------------------------------------------------------------------------------
# Project: User tools for HPC
# Author: Carel van Niekerk
# Year: 2024
# Group: Dialogue Systems and Machine Learning Group
# Institution: Heinrich Heine University Düsseldorf
# --------------------------------------------------------------------------------
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
"""Get the path to the virtual environment of a project"""

import os
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

BASHRC_PATH = f"/gpfs/project/{os.environ.get('USER_NAME')}/.usr_tls/.bashrc"


def get_venv_path(path: str) -> str:
    """Get the path to the virtual environment of a project"""

    path = os.path.realpath(path)
    for _ in range(len(path.split("/"))):
        if os.path.exists(os.path.join(path, ".venv")):
            return os.path.join(path, ".venv")
        path = os.path.dirname(path)

    raise FileNotFoundError("No .venv found in the path")


def save_as_current_venv(path: str) -> None:
    """Save the path to the virtual environment as the current virtual environment in the .bashrc file"""
    with open(BASHRC_PATH, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("export CURRENT_VENV="):
            lines[i] = f"export CURRENT_VENV={path}\n"
            break

    with open(BASHRC_PATH, "w") as f:
        f.writelines(lines)


def main():
    """Get the path to the virtual environment of a project"""
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-p", "--path", type=str, default=".", help="Path to the project"
    )
    path = parser.parse_args().path

    path = get_venv_path(path)

    save_as_current_venv(f"{path}/bin/activate")
    print(f"{path}/bin/activate")


if __name__ == "__main__":
    main()
