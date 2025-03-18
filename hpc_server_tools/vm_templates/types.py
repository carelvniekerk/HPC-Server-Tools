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
"""Types for the Hillbert HPC VM Templates."""

from dataclasses import dataclass
from enum import StrEnum

__all__ = ["AcceleratorModel", "Architecture", "HPCQueue", "VMConfig"]


class HPCQueue(StrEnum):
    """Enumeration of HPC queues."""

    DEFAULT = ""
    CUDA = "CUDA"
    DSML = "DSML"


class AcceleratorModel(StrEnum):
    """Enumeration of accelerator models."""

    DEFAULT = ""
    GTX1080 = "gtx1080ti"
    RTX6000 = "rtx6000"
    RTX8000 = "rtx8000"
    A100 = "a100"
    TESTLAT4 = "teslat4"


class Architecture(StrEnum):
    """Enumeration of architectures."""

    DEFAULT = ""
    ZEN2 = "zen2"
    ZEN3 = "zen3"


@dataclass
class VMConfig:
    """HPC VM Template."""

    queue: HPCQueue = HPCQueue.DEFAULT
    num_cpus: int = 2
    num_gpus: int = 1
    memory: int = 16
    accelerator_model: AcceleratorModel = AcceleratorModel.DEFAULT
    architecture: Architecture = Architecture.DEFAULT
    walltime: str = "8:00:00"
