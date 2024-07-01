# coding=utf-8
# --------------------------------------------------------------------------------
# Project: User tools for HPC
# Author: Carel van Niekerk
# Year: 2024
# Group: Dialogue Systems and Machine Learning Group
# Institution: Heinrich Heine University Düsseldorf
# --------------------------------------------------------------------------------
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
"""Submit a job to the HPC cluster"""

import json
import os
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from pathlib import Path

LOGS_PATH = f"/gpfs/project/{os.environ.get('USER_NAME')}/job_logs/"
ROOT = f"/gpfs/project/{os.environ.get('USER_NAME')}"

TEMPLATES = (
    f"/gpfs/project/{os.environ.get('USER_NAME')}/.usr_tls/tools/session_templates.json"
)
with open(TEMPLATES, "r") as reader:
    TEMPLATES = json.load(reader)

DEFAULTS = {
    "queue": "DSML",
    "ncpus": 2,
    "memory": None,
    "ngpus": 1,
    "accelerator_model": None,
    "architecture": None,
    "walltime": "48:00:00",
}


def get_venv_path(path: str) -> str:
    """Get the path to the virtual environment of a project"""

    path = os.path.realpath(path)
    for _ in range(len(path.split("/"))):
        if os.path.exists(os.path.join(path, ".venv")):
            return os.path.join(path, ".venv")
        path = os.path.dirname(path)

    raise FileNotFoundError("No .venv found in the path")


def build_preamble(args: Namespace) -> str:
    """Build the preamble for the job script"""
    preamble = "#!/bin/bash -li\n"
    preamble += f"#PBS -l walltime={args.walltime}\n"
    system = f"select=1:ncpus={args.ncpus}:mem={args.memory}gb"
    system += f":ngpus={args.ngpus}" if args.ngpus > 0 else ""
    system += (
        f":accelerator_model={args.accelerator_model}" if args.accelerator_model else ""
    )
    system += f":arch={args.architecture}" if args.architecture else ""
    preamble += f"#PBS -l {system}\n"
    preamble += "#PBS -A 'DialSys'\n"
    preamble += f"#PBS -q '{args.queue}'\n" if args.queue else ""
    preamble += f"#PBS -r n\n#PBS -e {LOGS_PATH}\n#PBS -o {LOGS_PATH}\n"
    preamble += f"#PBS -N {args.job_name}\n\n"

    preamble += "# Load environment\n"
    preamble += "source ~/.bashrc\n"
    preamble += "load_python\nload_cuda"
    # preamble += f"module load Python/3.11.4 CUDA/11.7.1\nmodule load Python/3.11.4"
    # preamble += "\nexport TRANSFORMERS_OFFLINE=1\nexport HF_DATASETS_OFFLINE=1\nexport HF_EVALUATE_OFFLINE=1"

    return preamble


def get_shell_commands(path: str, arguments: str = None) -> str:
    """Get the commands from a shell script and add the arguments to the top of the script"""
    reader = open(path, "r")
    script = reader.read()
    reader.close()

    arguments = (
        [arg.split("--")[-1] for arg in arguments.split(" --") if arg]
        if arguments
        else []
    )
    arguments = ["=".join(arg.split(" ", 1)) for arg in arguments]

    commands = [cmd for cmd in script.split("\n") if "bin/sh" not in cmd]
    if arguments:
        commands = ["# Parameters"] + arguments + ["# Commands"] + commands
    commands = [f"# Executing {path}"] + commands

    return "\n".join(commands)


def get_python_commands(path: str, arguments: str) -> str:
    """Get the commands from a python script and add the arguments to the python command"""
    if "--" in arguments:
        arguments_list: list = (
            [arg.split("--")[-1] for arg in arguments.split(" --") if arg]
            if arguments
            else []
        )
        arguments_list = [f"--{arg}" for arg in arguments_list]
    else:
        arguments_list: list = (
            [arg for arg in arguments.split(" ") if arg] if arguments else []
        )

    command = [f"python3 {path}"] + arguments_list
    command = [
        line + " \\" if i + 1 != len(command) else line
        for i, line in enumerate(command)
    ]
    command = ["\t" + line if i != 0 else line for i, line in enumerate(command)]

    venv_path = get_venv_path(args.job_script)
    venv_path = os.path.join(venv_path, "bin/activate")
    activate_venv = ["\n# Activate Virtual Environment", f"source {venv_path}\n"]

    command = activate_venv + ["# Move to project folder", f"cd {ROOT}\n"] + command

    return "\n".join(command)


def save_bash(script: str, path: str = None) -> str:
    """Save the bash script to a file and return the path to the file"""
    if not path:
        path = os.path.join(LOGS_PATH, "_temp.sh")

    writer = open(path, "w")
    writer.write(script)
    writer.close()

    return path


if __name__ == "__main__":
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--job_name", help="Job Name", default="", type=str)
    parser.add_argument(
        "-s", "--job_script", help="Path to job script", required=True, type=Path
    )
    parser.add_argument(
        "-a",
        "--job_script_args",
        help="Arguments for the job script",
        default="",
        type=str,
    )

    parser.add_argument("--template", help="Job Queue", default="DSML_short")
    parser.add_argument("--queue", help="Job Queue", default=DEFAULTS.get("queue"))
    parser.add_argument(
        "--ncpus", help="Number of CPUs", default=DEFAULTS.get("ncpus"), type=int
    )
    parser.add_argument(
        "--memory",
        help="Amount of memory in GB",
        default=DEFAULTS.get("memory"),
        type=int,
    )
    parser.add_argument(
        "--ngpus", help="Number of GPUs", default=DEFAULTS.get("ngpus"), type=int
    )
    parser.add_argument(
        "--accelerator_model",
        help="GPU model",
        default=DEFAULTS.get("accelerator_model"),
    )
    parser.add_argument(
        "--architecture", help="CPU Architecture", default=DEFAULTS.get("architecture")
    )
    parser.add_argument(
        "--walltime",
        help="Walltime in format hh:mm:ss, eg 08:00:00",
        default=DEFAULTS.get("walltime"),
        type=str,
    )

    parser.add_argument("--torchrun", help="Use torchrun", action="store_true")

    parser.add_argument("--view_error", help="View error log", action="store_true")
    parser.add_argument("--view_log", help="View output log", action="store_true")
    args = parser.parse_args()

    if args.template in TEMPLATES:
        args.queue = (
            TEMPLATES[args.template].get("queue", DEFAULTS.get("queue"))
            if args.queue == DEFAULTS.get("queue")
            else args.queue
        )
        args.ncpus = (
            TEMPLATES[args.template].get("ncpus", DEFAULTS.get("ncpus"))
            if args.ncpus == DEFAULTS.get("ncpus")
            else args.ncpus
        )
        args.memory = (
            TEMPLATES[args.template].get("memory", DEFAULTS.get("memory"))
            if args.memory == DEFAULTS.get("memory")
            else args.memory
        )
        args.ngpus = (
            TEMPLATES[args.template].get("ngpus", DEFAULTS.get("ngpus"))
            if args.ngpus == DEFAULTS.get("ngpus")
            else args.ngpus
        )
        args.accelerator_model = (
            TEMPLATES[args.template].get(
                "accelerator_model", DEFAULTS.get("accelerator_model")
            )
            if args.accelerator_model == DEFAULTS.get("accelerator_model")
            else args.accelerator_model
        )
        args.architecture = (
            TEMPLATES[args.template].get("architecture", DEFAULTS.get("architecture"))
            if args.architecture == DEFAULTS.get("architecture")
            else args.architecture
        )
        args.walltime = (
            TEMPLATES[args.template].get("walltime", DEFAULTS.get("walltime"))
            if args.walltime == DEFAULTS.get("walltime")
            else args.walltime
        )

    # Build job script and save temporary file
    preamble = build_preamble(args)

    if ".sh" in args.job_script.name:
        commands = get_shell_commands(args.job_script, args.job_script_args)
    elif ".py" in args.job_script.name:
        commands = get_python_commands(args.job_script, args.job_script_args)
        if args.torchrun:
            commands = commands.replace(
                "python3",
                f"torchrun --standalone --nnodes=1 --nproc_per_node {args.ngpus}",
            )
            commands += f" \\\n\t--n_gpu {args.ngpus}"

    job_script = preamble + "\n" + commands + "\n"
    job_path = save_bash(job_script)

    # Submit job
    out = os.popen(f"qsub {job_path}").read()
    job_id = [l for l in out.split("\n") if l][0]

    save_bash(job_script, os.path.join(LOGS_PATH, f"{job_id}.sh"))
