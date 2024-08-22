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
"""Submit a job to the HPC cluster."""

import os
import subprocess
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from pathlib import Path

from hpc_server_tools.poetry import get_venv_path
from hpc_server_tools.vm_templates import (
    A100_40GB,
    A100_80GB,
    CPU,
    DSML,
    GTX1080,
    RTX6000,
    RTX8000,
    TESLAT4,
    AcceleratorModel,
    Architecture,
    DSML_short,
    HPCQueue,
    VMConfig,
)

PROJECTS_ROOT_DIR: Path = Path("/gpfs/project")
USER_ROOT_DIR: Path = PROJECTS_ROOT_DIR / os.environ.get("USER_NAME", "")
LOGS_PATH: Path = USER_ROOT_DIR / "job_logs"

VM_DEFAULTS = VMConfig(
    queue=HPCQueue.DSML,
    walltime="48:00:00",
)
TEMPLATES = {
    "DSML_short": DSML_short,
    "DSML": DSML,
    "CUDA": DSML,
    "CPU": CPU,
    "GTX1080": GTX1080,
    "RTX6000": RTX6000,
    "RTX8000": RTX8000,
    "A100_40GB": A100_40GB,
    "A100_80GB": A100_80GB,
    "TESLAT4": TESLAT4,
}


def find_project_root(current_path: Path | None = None) -> Path:
    """Traverse to find the project root directory where the pyproject.toml is located.

    Args:
    ----
        current_path (Path): The starting path. Default is the current working dir.

    Returns:
    -------
        Path: The path to the project root directory.

    """
    if current_path is None:
        current_path = Path.cwd()
    # Remove the filename if it ends with .py
    if current_path.suffix == ".py":
        current_path = current_path.parent

    current_path = current_path.resolve()
    if (current_path / "pyproject.toml").is_file():
        return current_path

    for parent in current_path.parents:
        if (parent / "pyproject.toml").is_file():
            return parent

    msg = "pyproject.toml not found in the current or any parent directories"
    raise FileNotFoundError(msg)


def build_preamble(vm_config: VMConfig, job_name: str) -> str:
    """Build the preamble for the job script."""
    preamble: str = "#!/bin/bash -li\n"

    preamble += f"#PBS -l walltime={vm_config.walltime}\n"

    machine_configuration: str = (
        f"select=1:ncpus={vm_config.num_cpus}:mem={vm_config.memory}gb"
    )
    machine_configuration += (
        f":ngpus={vm_config.num_gpus}" if vm_config.num_gpus > 0 else ""
    )
    machine_configuration += (
        f":accelerator_model={vm_config.accelerator_model.value}"
        if args.accelerator_model != AcceleratorModel.DEFAULT
        else ""
    )
    machine_configuration += (
        f":arch={vm_config.architecture.value}"
        if vm_config.architecture != Architecture.DEFAULT
        else ""
    )
    preamble += f"#PBS -l {machine_configuration}\n"

    preamble += "#PBS -A 'DialSys'\n"
    preamble += (
        f"#PBS -q '{vm_config.queue.value}'\n"
        if vm_config.queue != HPCQueue.DEFAULT
        else ""
    )
    preamble += f"#PBS -r n\n#PBS -e {LOGS_PATH}\n#PBS -o {LOGS_PATH}\n"
    preamble += f"#PBS -N {job_name}\n\n"

    preamble += "# Load environment\n"
    preamble += "source ~/.bashrc\n"
    preamble += "load_python\nload_cuda"

    return preamble


def get_shell_commands(path: Path, arguments: str = "") -> str:
    """Get the commands from a shell script and add the arguments."""
    script: str = path.read_text()

    arguments_list: list[str] = (
        [arg.split("--")[-1] for arg in arguments.split(" --") if arg]
        if arguments
        else []
    )
    arguments_list = ["=".join(arg.split(" ", 1)) for arg in arguments]

    commands: list[str] = [cmd for cmd in script.split("\n") if "bin/sh" not in cmd]
    if arguments:
        commands = ["# Parameters", *arguments_list, "# Commands", *commands]
    commands = [f"# Executing {path}", *commands]

    return "\n".join(commands)


def get_python_commands(path: Path, arguments: str) -> str:
    """Get the commands from a python script and add the arguments."""
    if "--" in arguments:
        arguments_list: list[str] = (
            [arg.split("--")[-1] for arg in arguments.split(" --") if arg]
            if arguments
            else []
        )
        arguments_list = [f"--{arg}" for arg in arguments_list]
    else:
        arguments_list = (
            [arg for arg in arguments.split(" ") if arg] if arguments else []
        )

    command: list[str] = [f"python3 {path}", *arguments_list]
    command = [
        line + " \\" if i + 1 != len(command) else line
        for i, line in enumerate(command)
    ]
    command = ["\t" + line if i != 0 else line for i, line in enumerate(command)]

    try:
        project_poetry_root: Path = find_project_root(path)

        relative_path: Path = path.resolve().relative_to(project_poetry_root)
        base_cmd: str = command[0]

        add_break: bool = False
        if base_cmd.endswith("\\"):
            add_break = True

        base_cmd = f"poetry run python {relative_path!s}"
        if add_break:
            base_cmd += " \\"

        command[0] = base_cmd

        command = [
            "\n# Move to project folder",
            f"cd {project_poetry_root!s}\n",
            "# Update poetry dependencies",
            "poetry update\n",
            *command,
        ]
    except FileNotFoundError:
        venv_path: Path = get_venv_path(args.job_script)
        venv_activate_script: Path = venv_path / "bin" / "activate"
        activate_venv: list[str] = [
            "# Activate Virtual Environment",
            f"source {venv_activate_script}\n",
        ]

        command = [
            "\n# Move to project folder",
            f"cd {USER_ROOT_DIR}\n",
            *activate_venv,
            *command,
        ]

    return "\n".join(command)


def get_prun_commands(path: Path, arguments: str) -> str:
    """Create the prun command."""
    if "--" in arguments:
        arguments_list: list[str] = (
            [arg.split("--")[-1] for arg in arguments.split(" --") if arg]
            if arguments
            else []
        )
        arguments_list = [f"--{arg}" for arg in arguments_list]
    else:
        arguments_list = (
            [arg for arg in arguments.split(" ") if arg] if arguments else []
        )

    project_poetry_root: Path = find_project_root(path)
    relative_path: Path = path.resolve().relative_to(project_poetry_root)

    script_name: str = relative_path.name.split("prun:", 1)[-1]
    command: list[str] = [f"poetry run {script_name}", *arguments_list]
    command = [
        line + " \\" if i + 1 != len(command) else line
        for i, line in enumerate(command)
    ]
    command = ["\t" + line if i != 0 else line for i, line in enumerate(command)]

    command = [
        "\n# Move to project folder",
        f"cd {project_poetry_root!s}\n",
        "# Update poetry dependencies",
        "poetry update\n",
        *command,
    ]

    return "\n".join(command)


def save_bash(script: str, path: Path | None = None) -> Path:
    """Save the bash script to a file and return the path to the file."""
    if path is None:
        path = LOGS_PATH / "_temp.sh"

    path.write_text(script)

    return path


if __name__ == "__main__":
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
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

    parser.add_argument(
        "--template",
        help="Job Queue",
        default="DSML_short",
        type=str,
    )
    parser.add_argument(
        "--queue",
        help="Job Queue",
        default=VM_DEFAULTS.queue,
        type=HPCQueue,
    )
    parser.add_argument(
        "--ncpus",
        help="Number of CPUs",
        default=VM_DEFAULTS.num_cpus,
        type=int,
    )
    parser.add_argument(
        "--memory",
        help="Amount of memory in GB",
        default=VM_DEFAULTS.memory,
        type=int,
    )
    parser.add_argument(
        "--ngpus",
        help="Number of GPUs",
        default=VM_DEFAULTS.num_gpus,
        type=int,
    )
    parser.add_argument(
        "--accelerator_model",
        help="GPU model",
        default=VM_DEFAULTS.accelerator_model,
        type=AcceleratorModel,
    )
    parser.add_argument(
        "--architecture",
        help="CPU Architecture",
        default=VM_DEFAULTS.architecture,
        type=Architecture,
    )
    parser.add_argument(
        "--walltime",
        help="Walltime in format hh:mm:ss, eg 08:00:00",
        default=VM_DEFAULTS.walltime,
        type=str,
    )

    parser.add_argument("--view_error", help="View error log", action="store_true")
    parser.add_argument("--view_log", help="View output log", action="store_true")
    args = parser.parse_args()

    if args.template in TEMPLATES:
        queue: HPCQueue = (
            TEMPLATES[args.template].queue
            if args.queue == VM_DEFAULTS.queue
            else args.queue
        )
        num_cpus: int = (
            TEMPLATES[args.template].num_cpus
            if args.ncpus == VM_DEFAULTS.num_cpus
            else args.ncpus
        )
        memory: int = (
            TEMPLATES[args.template].memory
            if args.memory == VM_DEFAULTS.memory
            else args.memory
        )
        num_gpus: int = (
            TEMPLATES[args.template].num_gpus
            if args.ngpus == VM_DEFAULTS.num_gpus
            else args.ngpus
        )
        accelerator_model: AcceleratorModel = (
            TEMPLATES[args.template].accelerator_model
            if args.accelerator_model == VM_DEFAULTS.accelerator_model
            else args.accelerator_model
        )
        architecture: Architecture = (
            TEMPLATES[args.template].architecture
            if args.architecture == VM_DEFAULTS.architecture
            else args.architecture
        )
        walltime: str = (
            TEMPLATES[args.template].walltime
            if args.walltime == VM_DEFAULTS.walltime
            else args.walltime
        )

        vm_config: VMConfig = VMConfig(
            queue=queue,
            num_cpus=num_cpus,
            memory=memory,
            num_gpus=num_gpus,
            accelerator_model=accelerator_model,
            architecture=architecture,
            walltime=walltime,
        )
    else:
        vm_config: VMConfig = VMConfig(
            queue=args.queue,
            num_cpus=args.ncpus,
            memory=args.memory,
            num_gpus=args.ngpus,
            accelerator_model=args.accelerator_model,
            architecture=args.architecture,
            walltime=args.walltime,
        )

    # Build job script and save temporary file
    preamble: str = build_preamble(vm_config, args.job_name)

    if ".sh" in args.job_script.name:
        commands: str = get_shell_commands(args.job_script, args.job_script_args)
    elif ".py" in args.job_script.name:
        commands = get_python_commands(args.job_script, args.job_script_args)
    elif "prun:" in args.job_script.name:
        commands = get_prun_commands(args.job_script, args.job_script_args)

    job_script: str = preamble + "\n" + commands + "\n"
    job_path: Path = save_bash(job_script)

    # Submit job
    shell_return: str = subprocess.run(
        f"qsub {job_path}",
        shell=True,
        capture_output=True,
        check=True,
    )  # type: ignore  # noqa: PGH003
    job_id: str = next(line for line in shell_return.split("\n") if line)

    job_script_path: Path = LOGS_PATH / f"{job_id}.sh"
    save_bash(job_script, job_script_path)
    print(f"Job {args.job_name} submitted successfully with ID {job_id}.")
