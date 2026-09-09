#!/usr/bin/env bash
# Source this file from the Noctua2 HPC Server Tools scripts/aliases.
# Keep this portable to Bash and Zsh; sourcing must never submit a job.

qi-help() {
    cat <<'EOF'
Noctua2 interactive GPU allocations

Usage:
  qi                         Start the saved interactive allocation in qi.sh
  qi --help                  Show this help without submitting an allocation
  qi-gpu <1|2|4> [options]    Request A100s on one production node
  qi-2-gpu [options]          Shortcut for qi-gpu 2
  qi-4-gpu [options]          Shortcut for qi-gpu 4
  qi-setup --help             Advanced persistent plain-qi configuration

Options for qi-gpu (also accept --option=value):
  --mem SIZE                 Total host RAM per node, NOT per GPU or GPU VRAM.
                             Positive integer with optional K/M/G/T suffix;
                             no suffix means MiB. Example: --mem 128G.
  --time HH:MM:SS            Positive wall-time limit. Default: 08:00:00 (8 hours).
  -h, --help                 Show help without requesting resources.

Unchanged defaults:
  partition=gpu, nodes=1, tasks=1, CPUs=2, RAM=52G per GPU, time=8 hours
  Default total RAM: 1 GPU=52G, 2 GPUs=104G, 4 GPUs=208G.
  Overrides affect this invocation only; they do not rewrite plain qi's qi.sh.

Examples:
  qi-gpu 1 --mem 128G
  qi-gpu 1 --mem 128G --time 01:00:00
  qi-2-gpu --mem 160G

Run qs to inspect GPU placement and RAM headroom first. More RAM may mean a longer wait.
Start inside tmux on the login node for reconnectability. The helper runs
srun --pty ... bash --login: a terminal-connected login shell on the compute node.
Exit that shell to release the allocation; detaching tmux does not release it.
EOF
}

qi-gpu() {
    if [[ $# -eq 0 ]]; then
        echo "Usage: qi-gpu <1|2|4> [--mem SIZE] [--time HH:MM:SS]" >&2
        return 2
    fi
    case "$1" in
        -h|--help|help) qi-help; return ;;
    esac
    local num_gpus="$1"
    shift
    case "$num_gpus" in
        1|2|4) ;;
        *) echo "Error: choose 1, 2, or 4 A100 GPUs on one Noctua2 node." >&2; return 2 ;;
    esac

    local memory="$((52 * num_gpus))G" walltime="08:00:00"
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --mem|--time)
                if [[ $# -lt 2 ]]; then
                    echo "Error: $1 needs a value. See qi-gpu --help." >&2
                    return 2
                fi
                if [[ "$1" = --mem ]]; then memory="$2"; else walltime="$2"; fi
                shift 2
                ;;
            --mem=*) memory="${1#*=}"; shift ;;
            --time=*) walltime="${1#*=}"; shift ;;
            -h|--help|help) qi-help; return ;;
            *) echo "Error: unsupported argument '$1'. See qi-gpu --help." >&2; return 2 ;;
        esac
    done

    local memory_pattern='^[1-9][0-9]*[KMGTkmgt]?$'
    local time_pattern='^[0-9]{1,4}:[0-5][0-9]:[0-5][0-9]$'
    local zero_time_pattern='^0+:00:00$'
    if ! [[ "$memory" =~ $memory_pattern ]]; then
        echo "Error: --mem needs a positive integer, optionally suffixed K/M/G/T (e.g. 128G)." >&2
        return 2
    fi
    if ! [[ "$walltime" =~ $time_pattern ]] || [[ "$walltime" =~ $zero_time_pattern ]]; then
        echo "Error: --time needs a positive HH:MM:SS duration (e.g. 08:00:00)." >&2
        return 2
    fi

    echo "Requesting Noctua2 interactive allocation:"
    echo "  job=DevSession-${num_gpus}GPU partition=gpu nodes=1 tasks=1"
    echo "  GPUs=${num_gpus} x A100 CPUs=2 RAM=${memory} walltime=${walltime}"
    echo "  shell=bash --login (exit the shell to release the allocation)"
    srun --pty \
        --job-name="DevSession-${num_gpus}GPU" \
        --partition=gpu --nodes=1 --ntasks=1 --cpus-per-task=2 \
        --mem="$memory" --gres="gpu:a100:${num_gpus}" --time="$walltime" \
        bash --login
}
