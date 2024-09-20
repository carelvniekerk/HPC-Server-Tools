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
"""Create a VM configuration for job submission."""

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from pathlib import Path

from hpc_server_tools.vm_templates import (
    INTERACTIVE_DEFAULTS,
    JOB_DEFAULTS,
    TEMPLATES,
    AcceleratorModel,
    Architecture,
    HPCQueue,
    VMConfig,
)


def parse_args(*, is_interactive: bool = False) -> Namespace:
    defaults: VMConfig = INTERACTIVE_DEFAULTS if is_interactive else JOB_DEFAULTS
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    """Parse the command-line arguments."""
    # VM Configuration Arguments
    parser.add_argument(
        "--template",
        help="Machine Template",
        default="DSML_short",
        type=str,
    )
    parser.add_argument(
        "--queue",
        help="Job Queue",
        default=defaults.queue,
        type=HPCQueue,
    )
    parser.add_argument(
        "--ncpus",
        help="Number of CPUs",
        default=defaults.num_cpus,
        type=int,
    )
    parser.add_argument(
        "--memory",
        help="Amount of memory in GB",
        default=defaults.memory,
        type=int,
    )
    parser.add_argument(
        "--ngpus",
        help="Number of GPUs",
        default=defaults.num_gpus,
        type=int,
    )
    parser.add_argument(
        "--accelerator_model",
        help="GPU model",
        default=defaults.accelerator_model,
        type=AcceleratorModel,
    )
    parser.add_argument(
        "--architecture",
        help="CPU Architecture",
        default=defaults.architecture,
        type=Architecture,
    )
    parser.add_argument(
        "--walltime",
        help="Walltime in format hh:mm:ss, eg 08:00:00",
        default=defaults.walltime,
        type=str,
    )

    if not is_interactive:
        parser.add_argument("-n", "--job_name", help="Job Name", default="", type=str)
        parser.add_argument(
            "-s",
            "--job_script",
            help="Path to job script",
            required=True,
            type=Path,
        )
        parser.add_argument(
            "-a",
            "--job_script_args",
            help="Arguments for the job script",
            default="",
            type=str,
        )
        parser.add_argument("--view_error", help="View error log", action="store_true")
        parser.add_argument("--view_log", help="View output log", action="store_true")

    return parser.parse_args()


def get_vm_config(cmd_args: Namespace, *, is_interactive: bool = False) -> VMConfig:
    """Get the VM configuration for job submission."""
    defaults: VMConfig = INTERACTIVE_DEFAULTS if is_interactive else JOB_DEFAULTS
    if cmd_args.template not in TEMPLATES:
        return VMConfig(
            queue=cmd_args.queue,
            num_cpus=cmd_args.ncpus,
            memory=cmd_args.memory,
            num_gpus=cmd_args.ngpus,
            accelerator_model=cmd_args.accelerator_model,
            architecture=cmd_args.architecture,
            walltime=cmd_args.walltime,
        )

    queue: HPCQueue = (
        TEMPLATES[cmd_args.template].queue
        if cmd_args.queue == defaults.queue
        else cmd_args.queue
    )
    num_cpus: int = (
        TEMPLATES[cmd_args.template].num_cpus
        if cmd_args.ncpus == defaults.num_cpus
        else cmd_args.ncpus
    )
    memory: int = (
        TEMPLATES[cmd_args.template].memory
        if cmd_args.memory == defaults.memory
        else cmd_args.memory
    )
    num_gpus: int = (
        TEMPLATES[cmd_args.template].num_gpus
        if cmd_args.ngpus == defaults.num_gpus
        else cmd_args.ngpus
    )
    accelerator_model: AcceleratorModel = (
        TEMPLATES[cmd_args.template].accelerator_model
        if cmd_args.accelerator_model == defaults.accelerator_model
        else cmd_args.accelerator_model
    )
    architecture: Architecture = (
        TEMPLATES[cmd_args.template].architecture
        if cmd_args.architecture == defaults.architecture
        else cmd_args.architecture
    )
    walltime: str = (
        TEMPLATES[cmd_args.template].walltime
        if cmd_args.walltime == defaults.walltime
        else cmd_args.walltime
    )

    return VMConfig(
        queue=queue,
        num_cpus=num_cpus,
        memory=memory,
        num_gpus=num_gpus,
        accelerator_model=accelerator_model,
        architecture=architecture,
        walltime=walltime,
    )
