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

from argparse import SUPPRESS, ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
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
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Explicit resource options override the selected template. "
        "Omitted options inherit template values.",
        epilog=f"Without a matching template, defaults are {defaults.num_cpus} CPUs, "
        f"{defaults.memory} GB RAM, {defaults.num_gpus} GPUs and walltime {defaults.walltime}.",
    )
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
        default=SUPPRESS,
        type=HPCQueue,
    )
    parser.add_argument(
        "--ncpus",
        help="Number of CPUs",
        default=SUPPRESS,
        type=int,
    )
    parser.add_argument(
        "--memory",
        help="Amount of memory in GB",
        default=SUPPRESS,
        type=int,
    )
    parser.add_argument(
        "--ngpus",
        help="Number of GPUs",
        default=SUPPRESS,
        type=int,
    )
    parser.add_argument(
        "--accelerator_model",
        help="GPU model",
        default=SUPPRESS,
        type=AcceleratorModel,
    )
    parser.add_argument(
        "--architecture",
        help="CPU Architecture",
        default=SUPPRESS,
        type=Architecture,
    )
    parser.add_argument(
        "--walltime",
        help="Walltime in format hh:mm:ss, eg 08:00:00",
        default=SUPPRESS,
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
    # SUPPRESS preserves whether an option was supplied. Equality to a default
    # cannot tell omission from an intentional override (issue #1).
    base = TEMPLATES.get(cmd_args.template, defaults)
    return VMConfig(
        queue=getattr(cmd_args, "queue", base.queue),
        num_cpus=getattr(cmd_args, "ncpus", base.num_cpus),
        memory=getattr(cmd_args, "memory", base.memory),
        num_gpus=getattr(cmd_args, "ngpus", base.num_gpus),
        accelerator_model=getattr(
            cmd_args, "accelerator_model", base.accelerator_model
        ),
        architecture=getattr(cmd_args, "architecture", base.architecture),
        walltime=getattr(cmd_args, "walltime", base.walltime),
    )
