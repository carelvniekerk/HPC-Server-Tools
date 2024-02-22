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
# limitations under the License.

# Define user information
export USER_NAME=""
export CURRENT_VENV=""
export SETUP_COMPLETE=False

# Aliases for loading modules
alias base_installers='module load Python/3.11.4 intel/xe2020.4 gcc/11.1.0 SentencePiece/0.1.94 CUDA/11.7.1; module load Python/3.11.4'
alias base='module load Python/3.11.4 CUDA/11.7.1; module load Python/3.11.4'

# Aliases for environment variables
alias hf_offline='export HF_DATASETS_OFFLINE=1; export TRANSFORMERS_OFFLINE=1; export HF_EVALUATE_OFFLINE=1'
alias activate_cur_venv="source $CURRENT_VENV"

# Aliases for user tools
alias activate="source /gpfs/project/$USER_NAME/.usr_tls/activate_venv.sh"
alias qi-setup="python3 /gpfs/project/$USER_NAME/.usr_tls/get_interactive.py"
alias qi="source /gpfs/project/$USER_NAME/.usr_tls/qi.sh"
alias qs="python3 /gpfs/project/$USER_NAME/.usr_tls/resource_check.py"
alias submit_job="python3 /gpfs/project/$USER_NAME/.usr_tls/submit_job.py"
alias cleanup_job_logs="python3 /gpfs/project/$USER_NAME/.usr_tls/cleanup_logs.py"
alias job_log="python3 /gpfs/project/$USER_NAME/.usr_tls/job_log.py"

# Some alias for convenience:
alias home="cd /gpfs/project/$USER_NAME"
alias q='exit'
alias c='cd'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'

# Setup command line
[ -z "$PS1" ] && return
export PS1="\[\033[34;1m\]\u@\h\[\033[m\]:\[\033[32m\]\[\033[32;1m\]\W\[\033[m\]\$ "

# Load the base environment
home
hf_offline
base
activate_cur_venv
qs