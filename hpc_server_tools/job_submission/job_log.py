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
"""Open a log file stream for a job on the HPC cluster."""

import subprocess
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from pathlib import Path

from rich import box
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from hpc_server_tools.configuration import USER_NAME


def get_jobs(username: str) -> list[dict[str, str | int]]:
    """Get a list of jobs for a user on the HPC cluster."""
    raw_jobs: list[str] = (
        subprocess.run(
            f"squeue --user {username}",
            shell=True,
            check=True,
            capture_output=True,
        )
        .stdout.decode()
        .split("\n")[1:-1]
    )
    raw_jobs_split: list[list[str]] = [job.split() for job in raw_jobs]

    jobs: list[dict[str, str | int]] = [
        {
            "job_num": idx,
            "jobid": job[0],
            "name": job[2],
            "user": job[3],
            "status": job[4],
        }
        for idx, job in enumerate(raw_jobs_split)
    ]

    return jobs


if __name__ == "__main__":
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("--output", action="store_true")
    args = parser.parse_args()
    console: Console = Console()

    jobs: list[dict[str, str | int]] = get_jobs(USER_NAME)

    table: Table = Table(title="Select a Job", box=box.SQUARE)
    table.add_column("Job Number", style="blue")
    table.add_column("Job ID", style="blue")
    table.add_column("Name", style="blue")
    table.add_column("Job Status", style="blue")

    for job in jobs:
        row_style = "green" if job["status"] == "R" else "black"
        table.add_row(
            str(job["job_num"]),
            str(job["jobid"]),
            str(job["name"]),
            str(job["status"]),
            style=row_style,
        )

    console.print(table)

    found: bool = False
    job_index: str = "0"
    while not found:
        job_index = Prompt.ask("[bold black]Job number[/bold black]")
        if job_index.isdigit() and int(job_index) < len(jobs):
            found = True
        else:
            console.print("[bold red]Invalid job number[/bold red]")

    job_id: str = jobs[int(job_index)]["jobid"]  # type: ignore[assignment]

    # Get host
    # job_id = job_id.split(".")[0]
    # host = (
    #     subprocess.run(
    #         f"qstat -f {job_id} -n | tail -n 1 | grep -o 'hilbert[0-9]*' | head -n1",
    #         shell=True,
    #         check=True,
    #         capture_output=True,
    #     )
    #     .stdout.decode()
    #     .strip()
    # )

    # Construct ssh command
    suffix: str = "out" if args.output else "err"
    path: Path = Path(f"/pc2/users/t/{USER_NAME}/job_logs")
    path = next(path.glob(f"*_{job_id}.{suffix}"))
    cmd = f"tail -vf {path}"

    # Execute command
    subprocess.run(cmd, shell=True, check=True)
