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

import os
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.table import Table
from rich.columns import Columns
from rich import box

console = Console()
QUEUE = "DSML"
USER_NAME = os.environ.get("USER_NAME")

def get_node_status(node_name: str) -> dict:
    """Get the status of a node in the HPC cluster."""
    try:
        status = os.popen(f'pbsnodes {node_name}').read()
        status = [line for line in status.split('\n') if line and node_name not in line]
        status = [line.split(' = ', 1) for line in status]
        return {key.strip(): info.strip() for key, info in status}
    except Exception as e:
        console.print(f"[red]Error getting status for node {node_name}: {e}[/red]")
        return {}

def get_resources_available(node_status: dict) -> dict:
    """Get the resources available on a node in the HPC cluster."""
    resources = {'ncpus': 0, 'ngpus': 0, 'mem': 0}
    if 'state' not in node_status or node_status['state'] != 'free':
        return resources

    for resource in resources:
        resources[resource] = get_avail(node_status, resource)
    return resources

def get_avail(status: dict, resource: str) -> int:
    """Calculate the available amount of a resource."""
    available = int(status.get(f'resources_available.{resource}', '0').replace('mb', '').replace('kb', ''))
    assigned = int(status.get(f'resources_assigned.{resource}', '0').replace('mb', '').replace('kb', ''))

    if 'mb' in status.get(f'resources_available.{resource}', ''):
        available *= 1024
    if 'mb' in status.get(f'resources_assigned.{resource}', ''):
        assigned *= 1024

    available -= assigned

    if 'mb' in status.get(f'resources_available.{resource}', '') or 'kb' in status.get(f'resources_available.{resource}', ''):
        available //= 1048576
    return available

def print_hpc_banner():
    banner = """
█░█░█ █▀▀ █░░ █▀▀ █▀█ █▀▄▀█ █▀▀   ▀█▀ █▀█   █░█ █ █░░ █▄▄ █▀▀ █▀█ ▀█▀ █
▀▄▀▄▀ ██▄ █▄▄ █▄▄ █▄█ █░▀░█ ██▄   ░█░ █▄█   █▀█ █ █▄▄ █▄█ ██▄ █▀▄ ░█░ ▄
    """
    console.print(banner, style="bold blue", justify="left")

def get_node_list(prefix: str, indices: list) -> list:
    """Generate a list of node names based on a prefix and a list of indices."""
    return [f'{prefix}{i}' for i in indices]

def aggregate_resources(nodes: list) -> dict:
    """Aggregate resources across a list of nodes."""
    with ThreadPoolExecutor() as executor:
        status_list = list(executor.map(get_node_status, nodes))
    resources_list = [get_resources_available(status) for status in status_list]
    if not resources_list:
        return {'ncpus': 0, 'ngpus': 0, 'mem': 0}
    return {key: sum(node[key] for node in resources_list) for key in resources_list[0]}

def display_resources():
    # Display the job status
    console.print(os.popen(f"qstat -a {QUEUE}").read(), style="bold blue", justify="left")
    console.print(os.popen(f"qstat -u {USER_NAME}").read(), style="bold blue", justify="left")

    # Define node groups
    node_groups = {
        "GTX2080-8GB": get_node_list('hilbert', [313, 314]),
        "GTX1080TI-12GB": get_node_list('hilbert', [300 + i for i in range(13) if i != 8]),
        "TeslaT4-16GB": get_node_list('hilbert', [120, 121, 122, 123, 124]),
        "A100-40GB": get_node_list('hilbert', [400, 401, 402, 403]),
	"A100-80GB": get_node_list('hilbert', [404, 405, 406]),
        "RTX8000-48GB": get_node_list('hilbert', [330, 331]),
        "RTX6000-24GB": get_node_list('hilbert', [316, 317, 318, 319]),
    }

    tables = []

    for group_name, nodes in node_groups.items():
        resources = aggregate_resources(nodes)
        table = Table(title=f"{group_name} Resources", box=box.SIMPLE_HEAVY, expand=True)
        table.add_column("Resource", justify="center", style="bold")
        table.add_column("Available", justify="center", style="bold")

        for resource, value in resources.items():
            if resource.lower() == "ncpus":
                color = "green" if value > 20 else "yellow" if value > 0 else "red"
            if resource.lower() == "ngpus":
                color = "green" if value > 10 else "yellow" if value > 0 else "red"
            if resource.lower() == "mem":
                color = "green" if value > 320 else "yellow" if value > 0 else "red"
                value = f"{value} GB"
            table.add_row(resource.upper(), f"[{color}]{value}[/]")
        tables.append(table)

    # Print tables in columns (4 tables per row)
    for i in range(0, len(tables), 4):
        console.print(Columns(tables[i:i+4]))

if __name__ == "__main__":
    print_hpc_banner()
    display_resources()
