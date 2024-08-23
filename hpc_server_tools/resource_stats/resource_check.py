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

import subprocess
from concurrent.futures import ThreadPoolExecutor

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.table import Table

from hpc_server_tools.configuration import COMPUTE_NODE_GROUPS, LOCAL_QUEUE, USER_NAME

console: Console = Console()


def get_node_status(node_name: str) -> dict[str, str]:
    """Get the status of a node in the HPC cluster."""
    try:
        pbsnodes_return: str = subprocess.run(
            ["pbsnodes", node_name],  # noqa: S607
            shell=True,
            check=True,
            capture_output=True,
        ).stdout.decode("utf-8")
        status: list[list[str]] = [
            line.split(" = ", 1)
            for line in pbsnodes_return.split("\n")
            if line and node_name not in line
        ]
        return {key.strip(): info.strip() for key, info in status}
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error getting status for node {node_name}: {e}[/red]")
        return {}


def get_resources_available(node_status: dict[str, str]) -> dict[str, float]:
    """Get the resources available on a node in the HPC cluster."""
    resources: dict[str, float] = {"ncpus": 0, "ngpus": 0, "mem": 0}
    if "state" not in node_status or node_status["state"] != "free":
        return resources

    for resource in resources:
        resources[resource] = get_avail(node_status, resource)
    return resources


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
    banner: str = """
█░█░█ █▀▀ █░░ █▀▀ █▀█ █▀▄▀█ █▀▀   ▀█▀ █▀█   █░█ █ █░░ █▄▄ █▀▀ █▀█ ▀█▀ █
▀▄▀▄▀ ██▄ █▄▄ █▄▄ █▄█ █░▀░█ ██▄   ░█░ █▄█   █▀█ █ █▄▄ █▄█ ██▄ █▀▄ ░█░ ▄
    """
    console.print(banner, style="bold blue", justify="left")


def aggregate_resources(nodes: list[str]) -> dict[str, float]:
    """Aggregate resources across a list of nodes."""
    with ThreadPoolExecutor() as executor:
        status_list: list[dict[str, str]] = list(executor.map(get_node_status, nodes))
    resources_list: list[dict[str, float]] = [
        get_resources_available(status) for status in status_list
    ]
    if not resources_list:
        return {"ncpus": 0, "ngpus": 0, "mem": 0}
    return {key: sum(node[key] for node in resources_list) for key in resources_list[0]}


def display_resources() -> None:
    """Display the resources available on the HPC cluster."""
    # Display the job status
    console.print(
        subprocess.run(
            f"qstat -a {LOCAL_QUEUE}",
            capture_output=True,
            check=True,
            shell=True,
            text=True,
        ).stdout,
        style="bold blue",
        justify="left",
    )
    console.print(
        subprocess.run(
            f"qstat -u {USER_NAME}",
            capture_output=True,
            check=True,
            shell=True,
            text=True,
        ).stdout,
        style="bold blue",
        justify="left",
    )

    tables: list[Table] = []

    for group_name, nodes in COMPUTE_NODE_GROUPS.items():
        resources: dict[str, float] = aggregate_resources(nodes)
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
                value = f"{value} GB"  # noqa: PLW2901
            table.add_row(resource.upper(), f"[{color}]{value}[/]")
        tables.append(table)

    # Print tables in columns (4 tables per row)
    for i in range(0, len(tables), 4):
        console.print(Columns(tables[i : i + 4]))


if __name__ == "__main__":
    print_hpc_banner()
    display_resources()
