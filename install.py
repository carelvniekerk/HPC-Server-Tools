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
"""Configure the user tools for HPC project."""

import ast
import subprocess
from pathlib import Path

from hpc_server_tools.configuration import LOGS_PATH


def setup_pip() -> None:
    """Configure pip for hpc."""
    cmd1 = "pip config set global.trusted-host pypi.repo.test.hhu.de"
    cmd2 = "pip config set global.index-url http://pypi.repo.test.hhu.de/simple/"
    subprocess.run(cmd1, shell=True, check=True)
    subprocess.run(cmd2, shell=True, check=True)


def main() -> None:
    """Configure the user tools for HPC project."""
    bash_env_path: Path = Path(__file__).parent / ".bash_env"
    bashenv: list[str] = bash_env_path.read_text().splitlines()

    setup_complete: bool = False
    for line in bashenv:
        if line.startswith("export SETUP_COMPLETE="):
            setup_complete = ast.literal_eval(line.split("=")[1].strip().title())
            break

    if setup_complete:
        print("User tools for HPC project already configured.")
    else:
        print("Configuring user tools for HPC project.")
        user_name = input("Enter your user name: ")
        print("Setting up user tools for HPC project...")

        for i, line in enumerate(bashenv):
            if line.startswith("export USER_NAME="):
                bashenv[i] = f"export USER_NAME={user_name}\n"
                break

        LOGS_PATH.mkdir(parents=True, exist_ok=True)

        setup_pip()

        for i, line in enumerate(bashenv):
            if line.startswith("export SETUP_COMPLETE="):
                bashenv[i] = "export SETUP_COMPLETE=True\n"
                break

        bash_env_path.write_text("\n".join(bashenv))

        print("Configuration complete. Please restart your terminal to apply changes.")


if __name__ == "__main__":
    main()
