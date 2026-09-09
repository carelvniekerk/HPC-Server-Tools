# HPC User Tools

--------------------------------------------------------------------------------
Project: User tools for HPC  
Author: Carel van Niekerk  
Year: 2024  
Group: Dialogue Systems and Machine Learning Group  
Institution: Heinrich Heine University Düsseldorf
--------------------------------------------------------------------------------

This repository contains a collection of tools and scripts that are useful for HPC users. The tools are written in Python and Bash. The tools are designed to be easy to use and to be useful for a wide range of users.

## Installation
Load the Python module on the HPC system. 
```bash
module load lang/Python/3.13.1-GCCcore-14.2.0
```

Install the required packages. 
```bash
pip3 install --user uv fzf-bin
```

Clone the user_tools repository to your home directory on the HPC system. 
```bash
cd /pc2/users/t/<user_name>
git clone https://github.com/carelvniekerk/HPC-Server-Tools.git --branch feature/noctua2_cluster .usr_tls
```

Run the installation script to install the tools. 
```bash
cd .usr_tls
python3 install.py
source setup_symlinks.sh
cd ..
```
Should you wish to rerun this script at a later time, change the value of the `SETUP_COMPLETE` variable in the `.bash_env file` to `False`.

## Tools
### Noctua2 interactive GPU allocations

On a Noctua2 login node, inside tmux:

```bash
qi-gpu 1 --mem 128G                  # Default: eight hours
qi-gpu 1 --mem=256G --time=01:00:00
qi-2-gpu --mem 160G
qi-gpu --help
```

The memory override is total **host RAM per node**, not GPU VRAM or RAM per GPU.
Defaults remain two CPUs, 52 GiB host RAM per GPU, one production GPU node, and
eight hours. Options affect only this invocation; plain `qi` keeps its saved
command. More RAM may increase queue wait. Check placement with `qs` first.

The implementation belongs to this repository at
`hpc_server_tools/job_submission/interactive_gpu.sh`, sourced by `scripts/aliases`.
Deploy those files together; do not replace machine-local shell configuration or
the generated `qi.sh`. Existing shells can source the helper again or reconnect.
Neither Topo_LLM nor rl_experiments is needed to use it.

Run the dependency-free tests from this repository root (the scheduler is stubbed;
these commands never request an allocation):

```bash
bash tests/test_interactive_gpu.sh
zsh tests/test_interactive_gpu.sh
```

### Other commands
The following tools are available in the user_tools repository:

- `qi-setup`: A tool to set up the parameters for an interactive job on the HPC system.
- `qi`: A tool to submit an interactive job on the HPC system.
- `qs`: A GPU-aware view of active jobs and schedulable resources. Use
  `qs --recent-days 7` to add ended allocations for the current user with
  their allocated CPUs, RAM, GPUs, and nodes. `qs --user <username>` requests
  another user's live and recent jobs. When the cluster's Slurm privacy policy
  applies, the command warns that empty tables may mean hidden records while
  still allowing privileged Slurm operators to see what their role permits.
  `qs --project-jobs` similarly labels its output as privacy-limited instead of
  claiming a complete project inventory.
- `activate`: A tool to activate a Python virtual environment in a project directory. (Virtual env should be in the project repository named `.venv`.)
- `submit_job`: A tool to submit a job to the HPC system. Job script parameters should be specified as:
```bash
# My bash job
submit_job --job_name my_bash_job --job_script my_bash_script.sh --job_script_args "--arg1 val1 --arg2 val2"
# My Python job
submit_job --job_name my_python_job --job_script my_python_script.py --job_script_args "--arg1 val1 --arg2 val2"
```
- `cleanup_job_logs`: A tool to clean up job logs on the HPC system. The tool will remove all job logs for completed jobs.
- `job_log`: Follow the selected Slurm batch job's stdout log. Use `job_log --error` (or `--stderr`) to follow
  stderr instead. Stdout normally contains program output; stderr contains errors, warnings, and some progress output.
  The selection table requests longer job names from Slurm and identifies the stream currently being followed.
  Interactive allocations write to their attached terminal or tmux session and may not have Slurm log files.
