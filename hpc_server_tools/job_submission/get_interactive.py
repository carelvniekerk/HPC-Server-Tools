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
"""Set up an interactive session on the HPC cluster."""

from typing import TYPE_CHECKING

from hpc_server_tools.configuration import HPC_TOOLS_PATH
from hpc_server_tools.job_submission.vm_configuration import get_vm_config, parse_args
from hpc_server_tools.vm_templates import (
    AcceleratorModel,
    Architecture,
    HPCQueue,
    VMConfig,
)

if TYPE_CHECKING:
    from argparse import Namespace
    from pathlib import Path


def main() -> None:
    """Set up an interactive session on the HPC cluster."""
    args: Namespace = parse_args(is_interactive=True)
    vm_config: VMConfig = get_vm_config(args, is_interactive=True)

    command: list[str] = ["qsub", "-I", "-N", "DevSession", "-A", "DialSys"]

    if vm_config.queue != HPCQueue.DEFAULT:
        command.append("-q")
        command.append(vm_config.queue.value)

    command.append("-l")
    machine_configuration: str = f"select=1:ncpus={vm_config.num_cpus}"
    machine_configuration += f":mem={vm_config.memory}gb:ngpus={vm_config.num_gpus}"
    machine_configuration += (
        f":accelerator_model={vm_config.accelerator_model}"
        if vm_config.accelerator_model != AcceleratorModel.DEFAULT
        else ""
    )
    machine_configuration += (
        f":arch={vm_config.architecture}"
        if vm_config.architecture != Architecture.DEFAULT
        else ""
    )
    command.append(machine_configuration)

    command.append("-l")
    command.append(f"walltime={vm_config.walltime}")

    qi_command_path: Path = HPC_TOOLS_PATH / "job_submission/qi.sh"
    qi_command_path.write_text(" ".join(command))


if __name__ == "__main__":
    main()
