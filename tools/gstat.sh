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
    if [ -n "$CUDA_VISIBLE_DEVICES" ]; then
        gpu_indices=$(get_gpu_indices)
        python3 /gpfs/project/${USER_NAME}/.usr_tls/tools/gstat.py --id "$(get_gpu_indices)"
    else
        python3 /gpfs/project/${USER_NAME}/.usr_tls/tools/gstat.py
    fi
}
