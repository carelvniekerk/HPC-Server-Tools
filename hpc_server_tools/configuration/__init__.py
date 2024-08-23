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

__all__ = [
    "USER_NAME",
    "PROJECTS_ROOT_DIR",
    "USER_ROOT_DIR",
    "LOGS_PATH",
    "HPC_TOOLS_PATH",
    "LOCAL_QUEUE",
    "COMPUTE_NODE_GROUPS",
]

if "USER_NAME" not in environ:
    msg = "USER_NAME environment variable not set."
    raise KeyError(msg)

USER_NAME: str = environ["USER_NAME"]
PROJECTS_ROOT_DIR: Path = Path("/gpfs/project")
USER_ROOT_DIR: Path = PROJECTS_ROOT_DIR / USER_NAME
LOGS_PATH: Path = USER_ROOT_DIR / "job_logs"
HPC_TOOLS_PATH: Path = Path(__file__).parent.parent

# Resources
LOCAL_QUEUE: str = "DSML"


# Define node groups
def get_node_list(prefix: str, indices: list[int]) -> list[str]:
    """Generate a list of node names based on a prefix and a list of indices."""
    return [f"{prefix}{i}" for i in indices]


COMPUTE_NODE_GROUPS: dict[str, list[str]] = {
    "GTX2080-8GB": get_node_list("hilbert", [313, 314]),
    "GTX1080TI-12GB": get_node_list("hilbert", [300 + i for i in range(13) if i != 8]),  # noqa: PLR2004
    "TeslaT4-16GB": get_node_list("hilbert", [120, 121, 122, 123, 124]),
    "A100-40GB": get_node_list("hilbert", [400, 401, 402, 403]),
    "A100-80GB": get_node_list("hilbert", [404, 405, 406]),
    "RTX8000-48GB": get_node_list("hilbert", [330, 331]),
    "RTX6000-24GB": get_node_list("hilbert", [316, 317, 318, 319]),
}
