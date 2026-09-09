#!/usr/bin/env bash
# Dependency-free argument tests. srun is always a stub: no allocation is made.
# Usage: bash (or zsh) tests/test_interactive_gpu.sh [helper-path]
set -eu
# shellcheck source=hpc_server_tools/job_submission/interactive_gpu.sh
source "${1:-hpc_server_tools/job_submission/interactive_gpu.sh}"
# Called by qi-gpu in the sourced helper, never the real scheduler.
# shellcheck disable=SC2329
srun() { printf 'SRUN_ARG=%s\n' "$@"; }
checks=0

assert_contains() {
    case "$output" in
        *"$1"*) ;;
        *) printf 'Missing expected output: %s\n%s\n' "$1" "$output" >&2; exit 1 ;;
    esac
}

for gpu in 1 2 4; do
    output=$(qi-gpu "$gpu")
    assert_contains "SRUN_ARG=--gres=gpu:a100:$gpu"
    assert_contains "SRUN_ARG=--mem=$((52 * gpu))G"
    assert_contains 'SRUN_ARG=--time=08:00:00'
    assert_contains 'SRUN_ARG=--pty'
    assert_contains 'SRUN_ARG=--cpus-per-task=2'
    assert_contains 'SRUN_ARG=bash'
    assert_contains 'SRUN_ARG=--login'
    checks=$((checks + 1))
done

for size in 128G 160g 131072 131072M 1T 1024K; do
    output=$(qi-gpu 1 --mem "$size")
    assert_contains "SRUN_ARG=--mem=$size"
    assert_contains 'SRUN_ARG=--time=08:00:00'
    checks=$((checks + 1))
done
output=$(qi-gpu 2 --time=01:02:03 --mem=160G)
assert_contains 'SRUN_ARG=--mem=160G'
assert_contains 'SRUN_ARG=--time=01:02:03'
output=$(qi-gpu 1 --time 24:00:00 --mem 128G)
assert_contains 'SRUN_ARG=--time=24:00:00'
checks=$((checks + 2))

expect_invalid() {
    if output=$(qi-gpu "$@" 2>&1); then
        printf 'Unexpected success for: %s\n' "$*" >&2
        exit 1
    else
        result=$?
        test "$result" -eq 2
    fi
    case "$output" in *SRUN_ARG=*) echo 'Invalid input reached srun' >&2; exit 1 ;; esac
    checks=$((checks + 1))
}
expect_invalid
for gpu in 0 3 8 -1 invalid; do expect_invalid "$gpu"; done
for size in '' 0 0G -128G 1.5G 128GB '128G --exclusive' '; touch /tmp/unwanted'; do
    expect_invalid 1 --mem "$size"
done
for duration in '' 00:00:00 0:00:00 08:60:00 08:00:60 -1:00:00 8h unlimited '1-00:00:00'; do
    expect_invalid 1 --time "$duration"
done
expect_invalid 1 --mem
expect_invalid 1 --time
expect_invalid 1 --mem=
expect_invalid 1 --time=
expect_invalid 1 --bogus
expect_invalid 1 --mem --time 01:00:00
expect_invalid 1 2

for mode in --help -h help; do
    output=$(qi-gpu "$mode")
    assert_contains '--mem SIZE'
    assert_contains '8 hours'
    case "$output" in *SRUN_ARG=*) echo 'Help submitted a job' >&2; exit 1 ;; esac
    output=$(qi-gpu 1 --mem 128G "$mode")
    case "$output" in *SRUN_ARG=*) echo 'Help submitted a job' >&2; exit 1 ;; esac
    checks=$((checks + 1))
done
# Options must not leak into the next invocation.
output=$(qi-gpu 1)
assert_contains 'SRUN_ARG=--mem=52G'
assert_contains 'SRUN_ARG=--time=08:00:00'

# Preserve scheduler errors rather than reporting a successful allocation.
srun() { return 37; }
if output=$(qi-gpu 1); then
    echo 'Lost scheduler error status' >&2
    exit 1
else
    test "$?" -eq 37
fi
checks=$((checks + 2))
printf 'Passed %s argument/help checks; no Slurm allocation requested.\n' "$checks"
