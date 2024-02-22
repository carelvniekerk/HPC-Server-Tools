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
"""Configure the user tools for HPC project."""

import os


def setup_pip():
    """Configure pip for hpc"""
    cmd1 = "pip config set global.trusted-host pypi.repo.test.hhu.de"
    cmd2 = "pip config set global.index-url http://pypi.repo.test.hhu.de/simple/"
    os.system(cmd1)
    os.system(cmd2)


def main():
    """Configure the user tools for HPC project."""
    bashrc_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(bashrc_path, ".bashrc"), "r") as file:
        bashrc = file.readlines()

    setup_complete = False
    for i, line in enumerate(bashrc):
        if line.startswith("export SETUP_COMPLETE="):
            setup_complete = eval(line.split("=")[1].strip().title())
            break

    if setup_complete:
        print("User tools for HPC project already configured.")
    else:
        print("Configuring user tools for HPC project.")
        user_name = input("Enter your user name: ")
        print("Setting up user tools for HPC project...")

        for i, line in enumerate(bashrc):
            if line.startswith("export USER_NAME="):
                bashrc[i] = f"export USER_NAME={user_name}\n"
                break

        if not os.path.isdir(os.path.join("/gpfs/project", user_name, "job_logs")):
            os.makedirs(os.path.join("/gpfs/project", user_name, "job_logs"))

        setup_pip()

        for i, line in enumerate(bashrc):
            if line.startswith("export SETUP_COMPLETE="):
                bashrc[i] = "export SETUP_COMPLETE=True\n"
                break

        with open(os.path.join(bashrc_path, ".bashrc"), "w") as writer:
            writer.writelines(bashrc)

        bashrc_path = f"/home/{user_name}/.bashrc"
        with open(bashrc_path, "r") as file:
            bashrc = file.readlines()

        bashrc.append("\n# User tools for HPC\n")
        bashrc.append(f"source /gpfs/project/{user_name}/.usr_tls/.bashrc\n")

        with open(bashrc_path, "w") as writer:
            writer.writelines(bashrc)

        print("Configuration complete. Please restart your terminal to apply changes.")


if __name__ == "__main__":
    main()
