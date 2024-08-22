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

from hpc_server_tools.vm_templates.types import (
    AcceleratorModel,
    Architecture,
    HPCQueue,
    VMConfig,
)

__all__ = [
    "DSML_short",
    "DSML",
    "CPU",
    "GTX1080",
    "TESLAT4",
    "RTX6000",
    "RTX8000",
    "A100_40GB",
    "A100_80GB",
]

DSML_short: VMConfig = VMConfig(
    queue=HPCQueue.DSML,
    walltime="4:00:00",
)

DSML: VMConfig = VMConfig(
    queue=HPCQueue.DSML,
)

CPU: VMConfig = VMConfig(
    num_cpus=16,
    memory=64,
    num_gpus=0,
)

GTX1080: VMConfig = VMConfig(
    queue=HPCQueue.CUDA,
    accelerator_model=AcceleratorModel.GTX1080,
)

TESLAT4: VMConfig = VMConfig(
    queue=HPCQueue.CUDA,
    memory=20,
    accelerator_model=AcceleratorModel.TESTLAT4,
)

RTX6000: VMConfig = VMConfig(
    queue=HPCQueue.CUDA,
    memory=32,
    accelerator_model=AcceleratorModel.RTX6000,
)

RTX8000: VMConfig = VMConfig(
    queue=HPCQueue.CUDA,
    memory=52,
    accelerator_model=AcceleratorModel.RTX8000,
)

A100_40GB: VMConfig = VMConfig(
    queue=HPCQueue.CUDA,
    memory=52,
    accelerator_model=AcceleratorModel.A100,
    architecture=Architecture.ZEN2,
)

A100_80GB: VMConfig = VMConfig(
    queue=HPCQueue.CUDA,
    memory=96,
    accelerator_model=AcceleratorModel.A100,
    architecture=Architecture.ZEN3,
)
