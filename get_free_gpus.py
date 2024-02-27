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
"""Get the status of the HPC cluster and the resources available on the nodes."""

import os


def get_node_status(node_name: str) -> dict[str, str]:
    """Get the status of a node in the HPC cluster."""
    status = os.popen(f'pbsnodes {node_name}').read()
    status = [line for line in status.split('\n') if line and node_name not in line]
    status = [line.split(' = ', 1) for line in status]
    status = {key.strip(): info.strip() for key, info in status}

    return status


def get_resources_available(node_status: dict[str, str]) -> dict[str, int]:
    """Get the resources available on a node in the HPC cluster."""
    resources = {'ngpus': 0}

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
    # Get the status of the DSML 2080 nodes
    status = [get_node_status(node) for node in ['hilbert313', 'hilbert314']]
    resources = [get_resources_available(stat) for stat in status]
    gtx2080_resources = {key: sum([node[key] for node in resources]) for key in resources[0]}

    print(gtx2080_resources['ngpus'])
