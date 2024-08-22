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
"""Templates for the Hillbert HPC VMs."""

from hpc_server_tools.vm_templates.templates import (
    A100_40GB,
    A100_80GB,
    CPU,
    DEFAULT,
    DSML,
    GTX1080,
    RTX6000,
    RTX8000,
    TESLAT4,
    DSML_short,
)
from hpc_server_tools.vm_templates.types import (
    AcceleratorModel,
    Architecture,
    HPCQueue,
    VMConfig,
)

__all__ = [
    "DEFAULT",
    "DSML_short",
    "DSML",
    "CPU",
    "GTX1080",
    "TESLAT4",
    "RTX6000",
    "RTX8000",
    "A100_40GB",
    "A100_80GB",
    "AcceleratorModel",
    "Architecture",
    "HPCQueue",
    "VMTemplate",
]
