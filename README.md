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
git clone https://gitlab.cs.uni-duesseldorf.de/dsml/user_tools.git --branch noctua2_cluster .usr_tls
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
The following tools are available in the user_tools repository:

- `qi-setup`: A tool to set up the parameters for an interactive job on the HPC system.
- `qi`: A tool to submit an interactive job on the HPC system.
- `qs`: A tool to get the status of jobs and resources on the HPC system.
- `activate`: A tool to activate a Python virtual environment in a project directory. (Virtual env should be in the project repository named `.venv`.)
- `submit_job`: A tool to submit a job to the HPC system. Job script parameters should be specified as:
```bash
# My bash job
submit_job --job_name my_bash_job --job_script my_bash_script.sh --job_script_args "--arg1 val1 --arg2 val2"
# My Python job
submit_job --job_name my_python_job --job_script my_python_script.py --job_script_args "--arg1 val1 --arg2 val2"
```
- `cleanup_job_logs`: A tool to clean up job logs on the HPC system. The tool will remove all job logs for completed jobs.
- `job_log`: A tool to get the log of a job on the HPC system. The tool will stream the log of the job with the specified job ID.
