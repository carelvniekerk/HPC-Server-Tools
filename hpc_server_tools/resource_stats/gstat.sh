# coding=utf-8
#--------------------------------------------------------------------------------
# Project: Hilbert HPC Server Tools
# Author: Carel van Niekerk
# Year: 2024
# Group: Dialogue Systems and Machine Learning Group
# Institution: Heinrich Heine University Düsseldorf
#--------------------------------------------------------------------------------
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
# Node statistics tools

# Function to get a comma-separated list of GPU indices from CUDA_VISIBLE_DEVICES
get_gpu_indices() {
    # Step 1: Get the list of all UUIDs
    local all_uuids=$(nvidia-smi -L | awk -F '[()]' '{print $2}')

    # Step 2: Get the list of UUIDs from CUDA_VISIBLE_DEVICES
    local visible_uuids=$CUDA_VISIBLE_DEVICES

    # Step 3: Create a comma-separated list of indices based on CUDA_VISIBLE_DEVICES
    local gpu_indices=""
    local index=0

    for uuid in $(echo $all_uuids | tr ' ' '\n'); do
        # Skip 'UUID:' tokens
        if [[ $uuid == "UUID:" ]]; then
            continue
        fi

        # Check if the UUID is in the CUDA_VISIBLE_DEVICES list
        if [[ ",${visible_uuids}," == *",$uuid,"* ]]; then
            if [ -z "$gpu_indices" ]; then
                gpu_indices="$index"
            else
                gpu_indices="$gpu_indices $index"
            fi
        fi
        index=$((index + 1))
    done

    # Output the result
    echo $gpu_indices
}

# Function to show status of available GPUs
gs() {
    local gpu_indices=""
    local python_interpreter="/gpfs/project/${USER_NAME}/.usr_tls/.venv/bin/python"
    local gstat_script="/gpfs/project/${USER_NAME}/.usr_tls/hpc_server_tools/resource_stats/gstat.py"
    if [ -n "$CUDA_VISIBLE_DEVICES" ]; then
        gpu_indices=$(get_gpu_indices)
        $python_interpreter $gstat_script --id "$(get_gpu_indices)"
    else
        $python_interpreter $gstat_script
    fi
}
