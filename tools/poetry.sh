# Aliases for simplified poetry usage
alias pad='poetry add'
alias pbld='poetry build'
alias pch='poetry check'
alias pcmd='poetry list'
alias pconf='poetry config --list'
alias pexp='poetry export --without-hashes > requirements.txt'
alias pin='poetry init'
alias pinst='poetry install'
alias plck='poetry lock'
alias pnew='poetry new'
alias ppath='poetry env info --path'
alias pplug='poetry self show plugins'
alias ppub='poetry publish'
alias prm='poetry remove'
alias prun='poetry run'
alias ppy='poetry run python'
alias psad='poetry self add'
alias psh='poetry shell'
alias pshw='poetry show'
alias pslt='poetry show --latest'
alias psup='poetry self update'
alias psync='poetry install --sync'
alias ptree='poetry show --tree'
alias pup='poetry update'
alias pvinf='poetry env info'
alias pvoff='poetry config virtualenvs.create false'
alias pvrm='poetry env remove'
alias pvu='poetry env use'

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

# Custom Poetry completion function
_prun_completion() {
    local cur prev commands pyproject_script_commands

    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Extract commands from pyproject.toml if it exists
    if [[ -f "pyproject.toml" ]]; then
        pyproject_script_commands=$(awk '/\[tool.poetry.scripts\]/ {found=1; next} /\[.*\]/ {found=0} found {print $1}' pyproject.toml | sed 's/=$//')
        commands="${pyproject_script_commands}"
    fi

    # Add custom script completions for 'poetry run' or 'prun'
    if [[ ${prev} == "prun" ]]; then
        COMPREPLY+=($(compgen -W "${commands}" -- "$cur"))
    fi
}

complete -F _prun_completion prun