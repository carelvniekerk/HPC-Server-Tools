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
"""Check the resources available on the HPC cluster."""

import argparse
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

from hpc_server_tools.configuration import COMPUTE_NODE_GROUPS, USER_NAME
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.table import Table

console: Console = Console()

PROJECT_ACCOUNT: str = "hpc-prf-trust"
SQUEUE_FIELD_SEPARATOR: str = "\x1f"
SQUEUE_FORMAT: str = SQUEUE_FIELD_SEPARATOR.join(
    (
        "%i",
        "%u",
        "%P",
        "%j",
        "%t",
        "%M",
        "%l",
        "%D",
        "%C",
        "%m",
        "%b",
        "%R",
    )
)
SCHEDULABLE_NODE_STATES: frozenset[str] = frozenset({"IDLE", "MIXED"})


def get_node_status(node_name: str) -> dict[str, str]:
    """Get the status of a node in the HPC cluster."""
    try:
        scontrol_return: str = subprocess.run(
            f"scontrol show node {node_name}",
            shell=True,
            check=True,
            capture_output=True,
        ).stdout.decode("utf-8")
        node_info: list[str] = scontrol_return.split("\n")
        memory_info: str = next(
            line for line in node_info if "RealMemory=" in line and "AllocMem=" in line
        )
        real_memory_match: re.Match[str] | None = re.search(
            r"\bRealMemory=(\d+)", memory_info
        )
        allocated_memory_match: re.Match[str] | None = re.search(
            r"\bAllocMem=(\d+)", memory_info
        )
        if real_memory_match is None or allocated_memory_match is None:
            raise ValueError("missing RealMemory or AllocMem")
        real_memory: str = f"{real_memory_match.group(1)}mb"
        allocated_memory: str = f"{allocated_memory_match.group(1)}mb"

        resources_info: str = next(line for line in node_info if "CfgTRES=" in line)
        cpus_available: str = resources_info.split("cpu=", 1)[-1].split(",", 1)[0]
        gpus_available: str = resources_info.split("gpu=", 1)[-1].split(",", 1)[0]

        resources_info = next(line for line in node_info if "AllocTRES=" in line)
        if "cpu=" not in resources_info:
            cpus_allocated: str = "0"
        else:
            cpus_allocated = resources_info.split("cpu=", 1)[-1].split(",", 1)[0]

        if "gpu=" not in resources_info:
            gpus_allocated: str = "0"
        else:
            gpus_allocated = resources_info.split("gpu=", 1)[-1].split(",", 1)[0]

        state_info: str = next((line for line in node_info if "State=" in line), "")
        state: str = (
            state_info.split("State=", 1)[-1].split(" ", 1)[0]
            if state_info
            else "UNKNOWN"
        )

        return {  # noqa: TRY300
            "node_name": node_name,
            "state": state,
            "resources_available.ncpus": cpus_available,
            "resources_available.ngpus": gpus_available,
            "resources_assigned.ncpus": cpus_allocated,
            "resources_assigned.ngpus": gpus_allocated,
            "resources_available.mem": real_memory,
            "resources_assigned.mem": allocated_memory,
        }

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error getting status for node {node_name}: {e}[/red]")
        return {}
    except (StopIteration, ValueError) as e:
        console.print(
            f"[red]Could not parse scheduler status for node {node_name}: {e}[/red]"
        )
        return {}


def get_resources_available(node_status: dict[str, str]) -> dict[str, float]:
    """Get the resources available on a node in the HPC cluster."""
    resources: dict[str, float] = {"ncpus": 0, "ngpus": 0, "mem": 0}
    if not is_node_schedulable(node_status):
        return resources

    for resource in resources:
        resources[resource] = get_avail(node_status, resource)
    return resources


def is_node_schedulable(node_status: dict[str, str]) -> bool:
    """Return whether Slurm can place new work on a node."""
    state: str = node_status.get("state", "UNKNOWN")
    # Fail closed: compound flags such as IDLE+DRAIN and IDLE+INVALID_REG can
    # make an otherwise usable base state unavailable to new work.
    return state in SCHEDULABLE_NODE_STATES


def get_schedulable_memory_gib(node_status: dict[str, str]) -> int:
    """Return Slurm RAM request headroom, rounded down to whole GiB."""
    return int(get_avail(node_status, "mem")) if is_node_schedulable(node_status) else 0


def get_avail(status: dict[str, str], resource: str) -> float:
    """Calculate the available amount of a resource."""
    available: float = int(
        status.get(f"resources_available.{resource}", "0")
        .replace("mb", "")
        .replace("kb", ""),
    )
    assigned: float = int(
        status.get(f"resources_assigned.{resource}", "0")
        .replace("mb", "")
        .replace("kb", ""),
    )

    if "mb" in status.get(f"resources_available.{resource}", ""):
        available *= 1024
    if "mb" in status.get(f"resources_assigned.{resource}", ""):
        assigned *= 1024

    available -= assigned

    if "mb" in status.get(f"resources_available.{resource}", "") or "kb" in status.get(
        f"resources_available.{resource}",
        "",
    ):
        available //= 1048576
    return available


def print_hpc_banner() -> None:
    """Print the HPC banner."""
    banner: str = '''
__      __ ___     _       ___     ___   __  __    ___             _____    ___             _  _     ___     ___    _____   _   _    ___              ___   
\\ \\    / /| __|   | |     / __|   / _ \\ |  \\/  |  | __|     o O O |_   _|  / _ \\     o O O | \\| |   / _ \\   / __|  |_   _| | | | |  /   \\     o O O  |_  )  
 \\ \\/\\/ / | _|    | |__  | (__   | (_) || |\\/| |  | _|     o        | |   | (_) |   o      | .` |  | (_) | | (__     | |   | |_| |  | - |    o        / /   
  \\_/\\_/  |___|   |____|  \\___|   \\___/ |_|__|_|  |___|   TS__[O]  _|_|_   \\___/   TS__[O] |_|\\_|   \\___/   \\___|   _|_|_   \\___/   |_|_|   TS__[O]  /___|  
_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""| {======|_|"""""|_|"""""| {======|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""| {======|_|"""""| 
"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'./o--000'"`-0-0-'"`-0-0-'./o--000'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'./o--000'"`-0-0-' 
'''
    console.print(banner, style="bold blue", justify="left")


def get_node_statuses(nodes: list[str]) -> list[dict[str, str]]:
    """Get scheduler status for a list of nodes concurrently."""
    with ThreadPoolExecutor() as executor:
        return list(executor.map(get_node_status, nodes))


def aggregate_resources(status_list: list[dict[str, str]]) -> dict[str, float]:
    """Aggregate resources across node-status records."""
    resources_list: list[dict[str, float]] = [
        get_resources_available(status) for status in status_list
    ]
    if not resources_list:
        return {"ncpus": 0, "ngpus": 0, "mem": 0}
    return {key: sum(node[key] for node in resources_list) for key in resources_list[0]}


def format_gpu_request(gres_or_tres: str) -> str:
    """Format GPU counts from Slurm GRES or TRES syntax."""
    gpu_requests: list[tuple[str, str]] = []
    for item in gres_or_tres.split(","):
        match = re.fullmatch(
            r"(?:gres/)?gpu(?::([^,:=]+))?[:=](\d+)(?:\([^)]*\))?",
            item.strip(),
        )
        if match is not None:
            gpu_requests.append((match.group(1) or "", match.group(2)))
    if not gpu_requests:
        return "0"
    return ", ".join(
        f"{count} {gpu_type}" if gpu_type else count for gpu_type, count in gpu_requests
    )


def get_empty_jobs_row(*, project_jobs: bool) -> list[str]:
    """Build a placeholder row with its message in the job-name column."""
    row: list[str] = ["-"] * (12 if project_jobs else 11)
    name_column_index: int = 3 if project_jobs else 2
    row[name_column_index] = "No active jobs"
    return row


def parse_squeue_job_fields(line: str) -> list[str]:
    """Split one encoded squeue record without colliding with printable job names."""
    fields: list[str] = line.split(SQUEUE_FIELD_SEPARATOR, 11)
    return fields if len(fields) == 12 else []  # noqa: PLR2004


def display_jobs(*, project_jobs: bool = False) -> None:
    """Display user or project jobs, including requested RAM and GPUs per node."""
    scheduler_filter: list[str] = (
        ["--account", PROJECT_ACCOUNT] if project_jobs else ["--user", USER_NAME]
    )
    result: subprocess.CompletedProcess[str] = subprocess.run(
        [
            "squeue",
            *scheduler_filter,
            "--noheader",
            f"--format={SQUEUE_FORMAT}",
        ],
        capture_output=True,
        check=True,
        text=True,
    )

    table_title: str = (
        f"Jobs for Slurm account {PROJECT_ACCOUNT}"
        if project_jobs
        else f"Jobs for {USER_NAME}"
    )
    table: Table = Table(title=table_title, box=box.SIMPLE_HEAVY)
    table.add_column("Job ID", style="bold")
    if project_jobs:
        table.add_column("User")
    table.add_column("Partition")
    table.add_column("Name")
    table.add_column("State", justify="center")
    table.add_column("Elapsed", justify="right")
    table.add_column("Time limit", justify="right")
    table.add_column("Nodes", justify="right")
    table.add_column("CPUs", justify="right")
    table.add_column("RAM / node", justify="right")
    table.add_column("GPUs / node", justify="right")
    table.add_column("Node / reason")

    for line in result.stdout.splitlines():
        fields: list[str] = parse_squeue_job_fields(line)
        if not fields:
            continue
        (
            job_id,
            user,
            partition,
            name,
            state,
            elapsed,
            time_limit,
            nodes,
            cpus,
            memory,
            tres,
            reason,
        ) = fields
        state_color: str = "green" if state == "R" else "yellow"
        row: list[str] = [
            job_id,
            partition,
            name,
            f"[{state_color}]{state}[/]",
            elapsed,
            time_limit,
            nodes,
            cpus,
            memory,
            format_gpu_request(tres),
            reason,
        ]
        if project_jobs:
            row.insert(1, user)
        table.add_row(*row)

    if not result.stdout.strip():
        table.add_row(*get_empty_jobs_row(project_jobs=project_jobs))
    console.print(table)


def compress_node_names(node_names: list[str]) -> str:
    """Compress consecutively numbered nodes into a Slurm-style host list."""
    parsed_names: list[tuple[str, str]] = []
    for node_name in sorted(node_names):
        match: re.Match[str] | None = re.fullmatch(r"(.*?)(\d+)", node_name)
        if match is None:
            return ", ".join(sorted(node_names))
        parsed_names.append((match.group(1), match.group(2)))

    prefixes: set[str] = {prefix for prefix, _ in parsed_names}
    widths: set[int] = {len(number) for _, number in parsed_names}
    if len(prefixes) != 1 or len(widths) != 1:
        return ", ".join(sorted(node_names))
    if len(parsed_names) == 1:
        return node_names[0]

    prefix: str = parsed_names[0][0]
    width: int = len(parsed_names[0][1])
    numbers: list[int] = sorted(int(number) for _, number in parsed_names)
    ranges: list[tuple[int, int]] = []
    range_start: int = numbers[0]
    range_end: int = numbers[0]
    for number in numbers[1:]:
        if number == range_end + 1:
            range_end = number
            continue
        ranges.append((range_start, range_end))
        range_start = range_end = number
    ranges.append((range_start, range_end))

    parts: list[str] = [
        f"{start:0{width}d}-{end:0{width}d}" if start != end else f"{start:0{width}d}"
        for start, end in ranges
    ]
    return f"{prefix}[{','.join(parts)}]"


def display_gpu_node_summary(
    group_name: str,
    status_list: list[dict[str, str]],
) -> None:
    """Summarize nodes grouped by scheduler state and free GPUs per node."""
    gpu_statuses: list[dict[str, str]] = [
        status
        for status in status_list
        if int(status.get("resources_available.ngpus", "0")) > 0
    ]
    if not gpu_statuses:
        return

    grouped_nodes: dict[tuple[str, int, int], list[dict[str, str]]] = {}
    for status in gpu_statuses:
        total: int = int(status["resources_available.ngpus"])
        allocated: int = int(status["resources_assigned.ngpus"])
        free: int = max(total - allocated, 0) if is_node_schedulable(status) else 0
        state: str = status.get("state", "UNKNOWN")
        grouped_nodes.setdefault((state, free, total), []).append(status)

    table: Table = Table(title=f"{group_name} GPU placement", box=box.SIMPLE_HEAVY)
    table.add_column("Free GPUs / node", justify="right", style="bold")
    table.add_column("State")
    table.add_column("Count", justify="right")
    table.add_column("Total free GPUs", justify="right", style="bold")
    table.add_column("RAM headroom / node", justify="right")
    table.add_column("Nodes")

    sorted_groups: list[tuple[tuple[str, int, int], list[dict[str, str]]]] = sorted(
        grouped_nodes.items(),
        key=lambda item: (-item[0][1], item[0][0], item[0][2]),
    )
    for (state, free, total), statuses in sorted_groups:
        node_names: list[str] = [status["node_name"] for status in statuses]
        memory_headrooms: list[int] = [
            get_schedulable_memory_gib(status) for status in statuses
        ]
        min_memory: int = min(memory_headrooms)
        max_memory: int = max(memory_headrooms)
        memory_range: str = (
            f"{min_memory} GiB"
            if min_memory == max_memory
            else f"{min_memory}–{max_memory} GiB"
        )
        free_color: str = "green" if free == total else "yellow" if free else "red"
        state_color: str = "green" if state in SCHEDULABLE_NODE_STATES else "red"
        table.add_row(
            f"[{free_color}]{free} / {total}[/]",
            f"[{state_color}]{state}[/]",
            str(len(node_names)),
            f"{len(node_names)} × {free} = {len(node_names) * free}",
            memory_range,
            compress_node_names(node_names),
        )

    console.print(table)


def display_gpu_nodes_detailed(
    group_name: str,
    status_list: list[dict[str, str]],
) -> None:
    """Display one row per GPU node for detailed placement inspection."""
    gpu_statuses: list[dict[str, str]] = [
        status
        for status in status_list
        if int(status.get("resources_available.ngpus", "0")) > 0
    ]
    if not gpu_statuses:
        return

    table: Table = Table(title=f"{group_name} GPUs by node", box=box.SIMPLE_HEAVY)
    table.add_column("Node", style="bold")
    table.add_column("State")
    table.add_column("Free", justify="right")
    table.add_column("Allocated", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("RAM headroom", justify="right")

    for status in sorted(gpu_statuses, key=lambda item: item["node_name"]):
        total: int = int(status["resources_available.ngpus"])
        allocated: int = int(status["resources_assigned.ngpus"])
        free: int = max(total - allocated, 0) if is_node_schedulable(status) else 0
        free_color: str = "green" if free == total else "yellow" if free else "red"
        state: str = status.get("state", "UNKNOWN")
        state_color: str = "red" if not is_node_schedulable(status) else "green"
        table.add_row(
            status["node_name"],
            f"[{state_color}]{state}[/]",
            f"[{free_color}]{free}[/]",
            str(allocated),
            str(total),
            f"{get_schedulable_memory_gib(status)} GiB",
        )

    console.print(table)


def display_resources(
    *,
    detailed_gpu_nodes: bool = False,
    project_jobs: bool = False,
) -> None:
    """Display the resources available on the HPC cluster."""
    display_jobs(project_jobs=project_jobs)

    tables: list[Table] = []
    group_statuses: dict[str, list[dict[str, str]]] = {}

    for group_name, nodes in COMPUTE_NODE_GROUPS.items():
        status_list: list[dict[str, str]] = get_node_statuses(nodes)
        group_statuses[group_name] = status_list
        resources: dict[str, float] = aggregate_resources(status_list)
        table: Table = Table(
            title=f"{group_name} Resources",
            box=box.SIMPLE_HEAVY,
            expand=True,
        )
        table.add_column("Resource", justify="center", style="bold")
        table.add_column("Available", justify="center", style="bold")

        for resource, value in resources.items():
            if resource.lower() == "ncpus":
                color: str = "green" if value > 20 else "yellow" if value > 0 else "red"  # noqa: PLR2004
            if resource.lower() == "ngpus":
                color = "green" if value > 10 else "yellow" if value > 0 else "red"  # noqa: PLR2004
            if resource.lower() == "mem":
                color = "green" if value > 320 else "yellow" if value > 0 else "red"  # noqa: PLR2004
                value = f"{value} GB"  # type: ignore[assignment] # noqa: PLW2901
            table.add_row(resource.upper(), f"[{color}]{value}[/]")
        tables.append(table)

    # Print tables in columns (4 tables per row)
    for i in range(0, len(tables), 4):
        console.print(Columns(tables[i : i + 4]))

    for group_name, status_list in group_statuses.items():
        if detailed_gpu_nodes:
            display_gpu_nodes_detailed(group_name, status_list)
        else:
            display_gpu_node_summary(group_name, status_list)


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Show jobs and schedulable cluster resources.",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="show one row per GPU node instead of the compact placement summary",
    )
    parser.add_argument(
        "--project-jobs",
        action="store_true",
        help=f"show all jobs charged to the {PROJECT_ACCOUNT} Slurm account",
    )
    args: argparse.Namespace = parser.parse_args()
    print_hpc_banner()
    display_resources(
        detailed_gpu_nodes=args.detailed,
        project_jobs=args.project_jobs,
    )
