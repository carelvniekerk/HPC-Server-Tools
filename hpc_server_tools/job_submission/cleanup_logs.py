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
"""Cleanup logs from the job_logs directory."""

from typing import TYPE_CHECKING

from hpc_server_tools.configuration import LOGS_PATH

if TYPE_CHECKING:
    from pathlib import Path


def main() -> None:
    """Cleanup logs from the job_logs directory."""
    # Temp files
    temps: list[Path] = list(LOGS_PATH.glob("_*"))

    # Completed jobs
    job_ids: list[str] = [
        file.name.replace(".OU", "") for file in LOGS_PATH.glob("*.OU")
    ]

    # Files to remove (temp files and completed jobs)
    files = [
        LOGS_PATH / file
        for job in job_ids
        for file in [f"{job}.ER", f"{job}.OU", f"{job}.sh"]
    ] + temps

    # Remove files
    for file in files:
        if file.exists():
            file.unlink()


if __name__ == "__main__":
    main()
