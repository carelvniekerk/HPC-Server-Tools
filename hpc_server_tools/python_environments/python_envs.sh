# coding=utf-8
#--------------------------------------------------------------------------------
# Project: Hilbert HPC Server Tools
# Author: Carel van Niekerk
# Year: 2025
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

# UV commands
alias uva='uv add'
alias uvt='uv tree'
alias uvs='uv-sync'
alias uvi='uv init --package'
alias uvrm='uv remove'
alias uvr='uv run'
alias uvu='uv python pin'
alias upy='uv run python'
alias uup='rm uv.lock && uv sync'

uv-sync() {
    local sync_script="${HPC_USER_ROOT}/${USER_NAME}/.usr_tls/hpc_server_tools/python_environments/uv_sync.py"
    uv run --active $sync_script $1
}

# Custom cd function for auto venv changing
cd() {
    # Call the built-in cd command with all passed arguments
    builtin cd "$@" || return

    # Try to run the activate command
    if ! activate . 2>/dev/null; then
        # If activate fails, run deactivate and set venv prompt to empty string
        deactivate 2>/dev/null || true
        export VIRTUAL_ENV_PROMPT=""
    fi
}

# Setup custom autocomplete
_uv_run_completion() {
    local cur prev words cword
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    words=("${COMP_WORDS[@]}")
    cword=$COMP_CWORD

    if [[ ${COMP_CWORD} -eq 1 && "${words[0]}" == "uvr" ]]; then
        _uvr_completion
    elif [[ ${COMP_CWORD} -eq 2 && "${words[1]}" == "run" ]]; then
        # Complete the task (script) names from pyproject.toml
        _uvr_completion
    elif [[ ${COMP_CWORD} -gt 2 && "${words[1]}" == "run" ]]; then
        # After completing `poetry run <task>`, revert to normal Bash completion
        COMPREPLY=( $(compgen -o default -- "${cur}") )
    elif [[ ${COMP_CWORD} -gt 1 && "${words[0]}" == "uvr" ]]; then
        # After completing `poetry run <task>`, revert to normal Bash completion
        COMPREPLY=( $(compgen -o default -- "${cur}") )
    else
        case "${prev}" in
            uv)
                # COMPREPLY=( $(compgen -W "run install add remove update" -- "${cur}") ) # Add other subcommands as needed
                COMPREPLY=( $(compgen _uv -- "${cur}") )
                ;;
            run)
                COMPREPLY=( $(compgen -c -- "${cur}") )
                ;;
            *)
                COMPREPLY=()
                ;;
        esac
    fi
}

_uvr_completion() {
    local pyproject_script_commands=()

    if [[ -f "pyproject.toml" ]]; then
        pyproject_script_commands=($(awk '/\[project.scripts\]/ {found=1; next} /\[.*\]/ {found=0} found && $0 !~ /^[[:space:]]*#/ {print $1}' pyproject.toml | sed "s/\(.*\)/\1/"))
    fi

    COMPREPLY=( $(compgen -W "${pyproject_script_commands[*]}" -- "${cur}") )
}

complete -F _uv_run_completion -o bashdefault -o default uvr
