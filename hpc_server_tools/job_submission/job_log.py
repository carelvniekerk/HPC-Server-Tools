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

import re
import subprocess
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from pathlib import Path

from rich import box
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from hpc_server_tools.configuration import USER_NAME

SQUEUE_FIELD_SEPARATOR = "\x1f"
# Slurm metadata keys start with an uppercase letter. Restricting boundaries to
# that grammar preserves lowercase name=value fragments inside paths.
SCONTROL_FIELD_PATTERN = re.compile(r"(?:^|\s)([A-Z][A-Za-z0-9_]*)=")


def get_jobs(username: str) -> list[dict[str, str | int]]:
    """Get a list of jobs for a user on the HPC cluster."""
    result = subprocess.run(
        [
            "squeue",
            "--user",
            username,
            "--noheader",
            "--array",
            f"--format=%i{SQUEUE_FIELD_SEPARATOR}%.40j{SQUEUE_FIELD_SEPARATOR}%u{SQUEUE_FIELD_SEPARATOR}%t",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    jobs: list[dict[str, str | int]] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        job_id, name, user, status = (
            field.strip() for field in line.split(SQUEUE_FIELD_SEPARATOR, maxsplit=3)
        )
        jobs.append(
            {
                "job_num": len(jobs),
                "jobid": job_id,
                "name": name,
                "user": user,
                "status": status,
            }
        )
    return jobs


def get_jobs_or_exit(username: str, *, console: Console) -> list[dict[str, str | int]]:
    """Query active jobs or report a scheduler-command failure cleanly."""
    try:
        return get_jobs(username)
    except (FileNotFoundError, subprocess.CalledProcessError):
        console.print(
            f"[bold red]Could not query active Slurm jobs for {username}.[/bold red]"
        )
        console.print(
            "The squeue command may be unavailable or the scheduler may be temporarily unreachable."
        )
        raise SystemExit(1) from None


def parse_scontrol_metadata(output: str) -> dict[str, str]:
    """Parse one-line scontrol fields without discarding whitespace in values."""
    record = output.strip()
    matches = list(SCONTROL_FIELD_PATTERN.finditer(record))
    metadata: dict[str, str] = {}
    for index, match in enumerate(matches):
        value_end = (
            matches[index + 1].start() if index + 1 < len(matches) else len(record)
        )
        metadata[match.group(1)] = record[match.end() : value_end].strip()
    return metadata


def get_job_log_path(job_id: str, *, output: bool) -> Path | None:
    """Return the log path registered with Slurm, if the job has one."""
    result = subprocess.run(
        ["scontrol", "show", "job", "-o", job_id],
        check=True,
        capture_output=True,
        text=True,
    )
    field = "StdOut" if output else "StdErr"
    metadata = parse_scontrol_metadata(result.stdout)
    value = metadata.get(field)
    if not value or value in {"(null)", "/dev/null", "N/A"}:
        return None

    path = Path(value)
    if path.is_absolute():
        return path

    work_dir = metadata.get("WorkDir")
    if not work_dir or work_dir in {"(null)", "N/A"}:
        return None
    return Path(work_dir) / path


def get_job_log_path_or_exit(
    job_id: str, *, output: bool, console: Console
) -> Path | None:
    """Resolve a job log path or report a transient Slurm query failure."""
    try:
        return get_job_log_path(job_id, output=output)
    except (FileNotFoundError, subprocess.CalledProcessError):
        console.print(
            f"[bold red]Could not query Slurm log metadata for job {job_id}.[/bold red]"
        )
        console.print(
            "The job may have finished since the table was displayed, or scontrol may be unavailable."
        )
        raise SystemExit(1) from None


def follow_log_or_exit(path: Path, *, console: Console) -> None:
    """Follow a resolved log path or report a local tail failure cleanly."""
    try:
        subprocess.run(["tail", "-F", str(path)], check=True)
    except FileNotFoundError:
        console.print(
            "[bold red]Could not follow the Slurm log: tail is unavailable.[/bold red]"
        )
        raise SystemExit(1) from None
    except subprocess.CalledProcessError:
        console.print(
            f"[bold red]The tail command failed while following {path}.[/bold red]"
        )
        raise SystemExit(1) from None


if __name__ == "__main__":
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    stream_group = parser.add_mutually_exclusive_group()
    stream_group.add_argument(
        "--error",
        "--stderr",
        action="store_true",
        help="Follow the Slurm stderr log instead of the default stdout log",
    )
    stream_group.add_argument(
        "--output",
        "--stdout",
        action="store_true",
        help="Follow the Slurm stdout log (the default; retained for compatibility)",
    )
    args = parser.parse_args()
    console: Console = Console()
    follow_output = args.output or not args.error
    stream_name = "stdout" if follow_output else "stderr"

    jobs: list[dict[str, str | int]] = get_jobs_or_exit(USER_NAME, console=console)

    console.print(
        "[bold]Slurm batch jobs normally expose two live log streams:[/bold]\n"
        "  [cyan]stdout[/cyan]: normal program output (followed by default; optionally use --output)\n"
        "  [cyan]stderr[/cyan]: errors, warnings, and some progress output (use --error)\n"
        "Interactive allocations normally write to their attached terminal or tmux session."
    )
    console.print(f"[bold green]Selected stream: {stream_name}[/bold green]")

    table: Table = Table(
        title=f"Select a Job — following {stream_name}", box=box.SQUARE
    )
    table.add_column("Job Number", style="blue")
    table.add_column("Job ID", style="blue")
    table.add_column("Name", style="blue", min_width=24, max_width=40, no_wrap=True)
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

    if not jobs:
        console.print("[bold yellow]No active jobs found.[/bold yellow]")
        raise SystemExit(0)

    console.print(table)

    found: bool = False
    job_index: str = "0"
    while not found:
        job_index = Prompt.ask("[bold black]Job number[/bold black]")
        if job_index.isdigit() and int(job_index) < len(jobs):
            found = True
        else:
            console.print("[bold red]Invalid job number[/bold red]")

    job_id = str(jobs[int(job_index)]["jobid"])
    path = get_job_log_path_or_exit(job_id, output=follow_output, console=console)
    if path is None:
        console.print(
            f"[bold yellow]Slurm has no attachable {stream_name} log path for job {job_id}.[/bold yellow]"
        )
        console.print(
            "Interactive allocations normally write to their attached terminal or tmux session. "
            "A relative batch-log path also requires Slurm to report its working directory."
        )
        raise SystemExit(1)

    console.print(f"Following {stream_name} for job {job_id}: {path}")
    follow_log_or_exit(path, console=console)
