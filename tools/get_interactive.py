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
"""Cleanup logs from the job_logs directory"""

import json
import os
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

TEMPLATES = (
    f"/gpfs/project/{os.environ.get('USER_NAME')}/.usr_tls/tools/session_templates.json"
)
with open(TEMPLATES, "r") as reader:
    TEMPLATES = json.load(reader)


def main():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("--template", help="Job Queue", default="DSML_short")
    parser.add_argument("--queue", help="Job Queue", default="DSML")
    parser.add_argument("--ncpus", help="Number of CPUs", default=1, type=int)
    parser.add_argument("--memory", help="Amount of memory in GB", type=int)
    parser.add_argument("--ngpus", help="Number of GPUs", default=1, type=int)
    parser.add_argument("--accelerator_model", help="GPU model", default=None)
    parser.add_argument("--architecture", help="CPU Architecture", default=None)
    parser.add_argument(
        "--walltime",
        help="Walltime in format hh:mm:ss, eg 08:00:00",
        default="08:00:00",
        type=str,
    )
    args = parser.parse_args()

    if args.template in TEMPLATES:
        args.queue = TEMPLATES[args.template]["queue"] if "queue" in TEMPLATES[args.template] else args.queue
        args.ncpus = TEMPLATES[args.template]["ncpus"] if "ncpus" in TEMPLATES[args.template] else args.ncpus
        args.memory = TEMPLATES[args.template]["memory"] if "memory" in TEMPLATES[args.template] else args.memory
        args.ngpus = TEMPLATES[args.template]["ngpus"] if "ngpus" in TEMPLATES[args.template] else args.ngpus
        args.accelerator_model = TEMPLATES[args.template]["accelerator_model"] if "accelerator_model" in TEMPLATES[args.template] else args.accelerator_model
        args.architecture = TEMPLATES[args.template]["architecture"] if "architecture" in TEMPLATES[args.template] else args.architecture
        args.walltime = TEMPLATES[args.template]["walltime"] if "walltime" in TEMPLATES[args.template] else args.walltime

    command = ["qsub", "-I", "-N", "DevSession", "-A", "DialSys"]

    if args.queue:
        command.append("-q")
        command.append(args.queue)

    if args.ngpus >= 1 and not args.memory:
        args.memory = int(32 * args.ngpus)
    if not args.memory:
        args.memory = 16

    command.append("-l")
    system = f"select=1:ncpus={args.ncpus}:mem={args.memory}gb:ngpus={args.ngpus}"
    system += (
        f":accelerator_model={args.accelerator_model}" if args.accelerator_model else ""
    )
    system += (
        f":arch={args.architecture}" if args.architecture else ""
    )
    command.append(system)

    command.append("-l")
    command.append(f"walltime={args.walltime}")

    command = " ".join(command)

    with open(
        f'/gpfs/project/{os.environ.get("USER_NAME")}/.usr_tls/tools/qi.sh', "w"
    ) as writer:
        writer.write(command)


if __name__ == "__main__":
    main()
