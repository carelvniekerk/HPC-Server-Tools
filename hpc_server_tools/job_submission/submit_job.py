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

import shlex
import subprocess
from argparse import Namespace
from pathlib import Path
from tempfile import NamedTemporaryFile

from hpc_server_tools.configuration import LOGS_PATH, USER_ROOT_DIR
from hpc_server_tools.job_submission.vm_configuration import get_vm_config, parse_args
from hpc_server_tools.python_environments import get_venv_path
from hpc_server_tools.vm_templates import (
    AcceleratorModel,
    Architecture,
    HPCQueue,
    VMConfig,
)


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

    preamble += f"#SBATCH -t {vm_config.walltime}\n"

    preamble += f"#SBATCH --cpus-per-task={vm_config.num_cpus}\n"
    preamble += f"#SBATCH --mem={vm_config.memory}gb\n"

    if vm_config.num_gpus > 0:
        gpu_type = (
            f"{vm_config.accelerator_model.value}"
            if vm_config.accelerator_model != AcceleratorModel.DEFAULT
            else ""
        )
        preamble += f"#SBATCH --gres=gpu:{gpu_type}:{vm_config.num_gpus}\n"

    preamble += f"#SBATCH --output={LOGS_PATH}/%x_%j.out\n"
    preamble += f"#SBATCH --error={LOGS_PATH}/%x_%j.err\n"
    preamble += f"#SBATCH -J {job_name}\n\n"

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


def add_quotes_to_str_argument(argument: str, seperator: str = "=") -> str:
    """Add quotes to string arguments."""
    if " " not in argument:
        return argument

    key, value = argument.split(seperator, 1)
    return f'{key}{seperator}"{value}"'


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
        arguments_list = shlex.split(arguments) if arguments else []
        arguments_list = [add_quotes_to_str_argument(arg) for arg in arguments_list]

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

        base_cmd = f"uv run {relative_path!s}"
        if add_break:
            base_cmd += " \\"

        command[0] = base_cmd

        command = [
            "\n# Move to project folder",
            f"cd {project_poetry_root!s}\n",
            "# Update uv dependencies",
            "uv sync\n",
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


def get_uvrun_commands(path: Path, arguments: str) -> str:
    """Create the prun command."""
    if "--" in arguments:
        arguments_list: list[str] = (
            [arg.split("--")[-1] for arg in arguments.split(" --") if arg]
            if arguments
            else []
        )
        arguments_list = [f"--{arg}" for arg in arguments_list]
    else:
        arguments_list = shlex.split(arguments) if arguments else []
        arguments_list = [add_quotes_to_str_argument(arg) for arg in arguments_list]

    project_root: Path = find_project_root(path)
    relative_path: Path = path.resolve().relative_to(project_root)

    script_name: str = relative_path.name.split("uvrun:", 1)[-1]
    command: list[str] = [f"uv run {script_name}", *arguments_list]
    command = [
        line + " \\" if i + 1 != len(command) else line
        for i, line in enumerate(command)
    ]
    command = ["\t" + line if i != 0 else line for i, line in enumerate(command)]

    command = [
        "\n# Move to project folder",
        f"cd {project_root!s}\n",
        "# Update dependencies",
        "uv sync\n",
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
    args: Namespace = parse_args()
    vm_config: VMConfig = get_vm_config(args)

    # Build job script and save temporary file
    preamble: str = build_preamble(vm_config, args.job_name)

    if ".sh" in args.job_script.name:
        commands: str = get_shell_commands(args.job_script, args.job_script_args)
    elif ".py" in args.job_script.name:
        commands = get_python_commands(args.job_script, args.job_script_args)
    elif "uvrun:" in args.job_script.name:
        commands = get_uvrun_commands(args.job_script, args.job_script_args)

    job_script: str = preamble + "\n" + commands + "\n"

    with NamedTemporaryFile(mode="w", suffix=".sh", delete=True) as temp_file:
        temp_file.write(job_script)
        temp_file.flush()

        # Submit job
        shell_return: str = subprocess.run(
            f"sbatch {temp_file.name}",
            shell=True,
            capture_output=True,
            check=True,
            text=True,
        ).stdout
        job_id: str = next(line for line in shell_return.split("\n") if line)
        job_id = job_id.split("batch job ")[-1]

    job_script_path: Path = LOGS_PATH / f"{job_id}.sh"
    save_bash(job_script, job_script_path)
    print(f"Job {args.job_name} submitted successfully with ID {job_id}.")
