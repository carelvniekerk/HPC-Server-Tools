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
"""Get the status of the nodes in the HPC cluster and the resources available on each node."""

import os
from tabulate import tabulate

QUEUE = "DSML"
USER_NAME = os.environ.get("USER_NAME")


def get_node_status(node_name: str) -> dict[str, str]:
    """Get the status of a node in the HPC cluster."""
    status = os.popen(f'pbsnodes {node_name}').read()
    status = [line for line in status.split('\n') if line and node_name not in line]
    status = [line.split(' = ', 1) for line in status]
    status = {key.strip(): info.strip() for key, info in status}

    return status


def get_resources_available(node_status: dict[str, str]) -> dict[str, int]:
    """Get the resources available on a node in the HPC cluster."""
    resources = {'ncpus': 0, 'ngpus': 0, 'mem': 0}

    # Check if the node is free
    if 'state' not in node_status or node_status['state'] != 'free':
        return resources

    for resource in resources:
        resources[resource] = get_avail(node_status, resource)
    return resources


def get_avail(status: dict[str, int], resource: str) -> int:
    # Get the available and assigned resources
    available = status[f'resources_available.{resource}'] if f'resources_available.{resource}' in status else '0'
    assigned = status[f'resources_assigned.{resource}'] if f'resources_assigned.{resource}' in status else '0'

    # Convert the resources to integers in bytes
    mb_unit = 'mb' in status[f'resources_available.{resource}'] if f'resources_available.{resource}' in status else 0
    available = int(available.replace('mb', '').replace('kb', ''))
    available = available * 1024 if mb_unit else available
    mb_unit = 'mb' in status[f'resources_assigned.{resource}'] if f'resources_assigned.{resource}' in status else 0
    assigned = int(assigned.replace('mb', '').replace('kb', ''))
    available = available * 1024 if mb_unit else available

    available = available - assigned
    # Convert the resources to gigabytes
    if 'mb' in status[f'resources_available.{resource}'] or 'kb' in status[f'resources_available.{resource}']:
        available /= 1048576
    return available


if __name__ == "__main__":
    print(" _    _      _                            _          _   _ _ _ _               _   ")
    print("| |  | |    | |                          | |        | | | (_) | |             | |  ")
    print("| |  | | ___| | ___ ___  _ __ ___   ___  | |_ ___   | |_| |_| | |__   ___ _ __| |_ ")
    print("| |/\| |/ _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \  |  _  | | | '_ \ / _ \ '__| __|")
    print("\  /\  /  __/ | (_| (_) | | | | | |  __/ | || (_) | | | | | | | |_) |  __/ |  | |_ ")
    print(" \/  \/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/  \_| |_/_|_|_.__/ \___|_|   \__|")
    print("")

    # Get the status of the queue and the user jobs
    os.system(f"qstat -a {QUEUE}")
    os.system(f"qstat -u {USER_NAME}")

    # Get the status of the DSML 2080 nodes
    status = [get_node_status(node) for node in ['hilbert313', 'hilbert314']]
    resources = [get_resources_available(stat) for stat in status]
    gtx2080_resources = {key: sum([node[key] for node in resources]) for key in resources[0]}

    headers = ["GTX2080\nCPU's", "\nGPU's", "\nMemory"]
    rows = [gtx2080_resources['ncpus'], gtx2080_resources['ngpus'], f"{int(gtx2080_resources['mem'])} gb"]

    # Get the status of the CUDA 1080ti nodes
    nodes = [f'hilbert{300 + i}' for i in range(13) if i != 8]
    status = [get_node_status(node) for node in nodes]
    resources = [get_resources_available(stat) for stat in status]
    gtx1080ti_resources = {key: sum([node[key] for node in resources]) for key in resources[0]}

    headers += ["    ", "GTX1080TI\nCPU's", "\nGPU's", "\nMemory"]
    rows += ['', gtx1080ti_resources['ncpus'], gtx1080ti_resources['ngpus'], f"{int(gtx1080ti_resources['mem'])} gb"]

    # Get the status of the Tesla T4 nodes
    status = [get_node_status(node) for node in ['hilbert120', 'hilbert121', 'hilbert122', 'hilbert123', 'hilbert124']]
    resources = [get_resources_available(stat) for stat in status]
    teslat4_resources = {key: sum([node[key] for node in resources]) for key in resources[0]}

    headers += ["    ", "TeslaT4\nCPU's", "\nGPU's", "\nMemory"]
    rows += ['', teslat4_resources['ncpus'], teslat4_resources['ngpus'], f"{int(teslat4_resources['mem'])} gb"]

    print(tabulate([rows], headers))

    # Get the status of the A100 nodes
    status = [get_node_status(node) for node in ['hilbert400', 'hilbert401', 'hilbert402', 'hilbert403']]
    resources = [get_resources_available(stat) for stat in status]
    a100_resources = {key: sum([node[key] for node in resources]) for key in resources[0]}

    headers = ["A100\nCPU's", "\nGPU's", "\nMemory"]
    rows = [a100_resources['ncpus'], a100_resources['ngpus'], f"{int(a100_resources['mem'])} gb"]

    # Get the status of the RTX8000 nodes
    status = [get_node_status(node) for node in ['hilbert330', 'hilbert331']]
    resources = [get_resources_available(stat) for stat in status]
    rtx8000_resources = {key: sum([node[key] for node in resources]) for key in resources[0]}

    headers += ["    ", "RTX8000\nCPU's", "\nGPU's", "\nMemory"]
    rows += ['', rtx8000_resources['ncpus'], rtx8000_resources['ngpus'], f"{int(rtx8000_resources['mem'])} gb"]

    # Get the status of the RTX6000 nodes
    status = [get_node_status(node) for node in ['hilbert316', 'hilbert317']]
    resources = [get_resources_available(stat) for stat in status]
    rtx6000_resources = {key: sum([node[key] for node in resources]) for key in resources[0]}

    headers += ["    ", "RTX6000\nCPU's", "\nGPU's", "\nMemory"]
    rows += ['', rtx6000_resources['ncpus'], rtx6000_resources['ngpus'], f"{int(rtx6000_resources['mem'])} gb"]

    print(tabulate([rows], headers))
