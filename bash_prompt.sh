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

# Setup command line
function truncate_path {
    # Get the current working directory
    local pwd=$(pwd)
    # Use parameter expansion to keep only the last two directories
    local truncated=$(echo $pwd | awk -F/ '{n = split($0,a,"/"); if (n>2) print a[n-1]"/"a[n]; else print $0;}')
    echo $truncated
}

function set_prompt {
    local EXIT="$?"
    local RED="\[\033[01;31m\]"
    local GREEN="\[\033[01;32m\]"
    local NO_COLOR="\[\033[00m\]"
    local GRAY="\[\033[00;30m\]"

    local host_color="\[\033[00;32m\]󰒋 "   # Green by default

    # Check if the hostname contains "login"
    if [[ $(hostname) == *"login"* ]]; then
        host_color="\[\033[00;33m\] " # Orange
    fi

    if [[ -n "$VIRTUAL_ENV" ]]; then
        venv="\[\033[0;35m\]in 󰆧 ${VIRTUAL_ENV_PROMPT}\[\033[00m\] "
    fi

    local NUM_JOBS=$(python /gpfs/project/$USER_NAME/.usr_tls/get_num_jobs.py)
    local NUM_JOBS="  \[\033[00;32m\] ${NUM_JOBS}\[\033[00m\]"

    local NUM_FREE_GPUS=$(python /gpfs/project/$USER_NAME/.usr_tls/get_free_gpus.py)
    local NUM_FREE_GPUS="  \[\033[00;32m\]  2080:${NUM_FREE_GPUS}\[\033[00m\]"

    local PS1_HOST="${host_color}\h:\[\033[00;34m\]$(truncate_path)\[\033[00m\] "
    local PS1_GIT="$(if git rev-parse --git-dir > /dev/null 2>&1; then echo "${GRAY} ${GRAY}$(git rev-parse --abbrev-ref HEAD) ${NO_COLOR}"; else echo ""; fi)"
    local PS1_PYTHON="\[\033[01;32m\]  v$(python --version 2>&1 | cut -d" " -f2)\[\033[00m\] "

    if [[ $EXIT == 0 ]]; then
        export PS1="${PS1_HOST}${PS1_GIT}${PS1_PYTHON}${venv}${NUM_JOBS}${NUM_FREE_GPUS}\n${GREEN} ${NO_COLOR}"
    else
        export PS1="${PS1_HOST}${PS1_GIT}${PS1_PYTHON}${venv}${NUM_JOBS}${NUM_FREE_GPUS}\n${RED} ${NO_COLOR}"
    fi
}

PROMPT_COMMAND=set_prompt