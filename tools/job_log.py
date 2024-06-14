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
"""Open a log file stream for a job on the HPC cluster"""

import os
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

from rich import box
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from tabulate import tabulate

console = Console()


def get_jobs(username: str) -> list[dict[str, str]]:
    """Get a list of jobs for a user on the HPC cluster"""
    jobs = os.popen(f"qstat -u {username}").read().split("\n")[5:-1]
    jobs = [job.split() for job in jobs]

    jobs = [
        {
            "job_num": idx,
            "jobid": job[0],
            "name": job[3],
            "user": job[2],
            "status": job[9],
        }
        for idx, job in enumerate(jobs)
    ]

    return jobs


if __name__ == "__main__":
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("--jobid", default=None)
    parser.add_argument("--output", action="store_true")
    args = parser.parse_args()

    if args.jobid is None:
        jobs = get_jobs(os.environ.get("USER_NAME"))

        table = Table(title="Select a Job", box=box.SQUARE)
        table.add_column("Job Number", style="cyan")
        table.add_column("Job ID", style="magenta")
        table.add_column("Name", style="green")
        table.add_column("Job Status", style="yellow")

        for job in jobs:
            status_color = "green" if job["status"] == "R" else "black"
            table.add_row(
                str(job["job_num"]),
                job["jobid"],
                job["name"],
                f"[{status_color}]{job['status']}[/{status_color}]",
            )

        console.print(table)

        found = False
        job_id = None
        while not found:
            job_id = Prompt.ask("[bold black]Job number[/bold black]")
            if job_id.isdigit() and int(job_id) < len(jobs):
                found = True
            else:
                console.print("[bold red]Invalid job number[/bold red]")

        args.jobid = jobs[int(job_id)]["jobid"]

    # Get host
    jobid = args.jobid.split(".")[0]
    host = (
        os.popen(
            f"qstat -f {jobid} -n | tail -n 1 | grep -o 'hilbert[0-9]*' | head -n1"
        )
        .read()
        .strip()
    )

    # Construct ssh command
    cmd = "OU" if args.output else "ER"
    cmd = f'ssh -i ~/.ssh/id_int {host} "tail -f /var/spool/pbs/spool/{jobid}.hpc-batch.{cmd}"'

    # Execute command
    os.system(cmd)
