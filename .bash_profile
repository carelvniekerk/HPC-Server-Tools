# .bash_profile
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

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

# Load the base environment
home

if [[ $(hostname) == *"login"* ]]
then
    # Load only python and display status on login node (Python is needed for the utils)
    load_python &&
    clear &&
    qs
else
    # Load all base modules needed during dev and running and activate latest venv
    base &&
    activate_cur_venv

    # Always start a dev tmux session for interactive sessions.
    if tmux has-session -t development_session 2>/dev/null
    then
        echo ""
    else
        dev-tmux
    fi
fi
