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
"""HPC Server Tools environment variables."""

from os import environ
from pathlib import Path

__all__ = ["PROJECTS_ROOT_DIR", "USER_ROOT_DIR", "LOGS_PATH"]

if "USER_NAME" not in environ:
    msg = "USER_NAME environment variable not set."
    raise KeyError(msg)

PROJECTS_ROOT_DIR: Path = Path("/gpfs/project")
USER_ROOT_DIR: Path = PROJECTS_ROOT_DIR / environ.get("USER_NAME", "")
LOGS_PATH: Path = USER_ROOT_DIR / "job_logs"
HPC_TOOLS_PATH: Path = Path(__file__).parent.parent
