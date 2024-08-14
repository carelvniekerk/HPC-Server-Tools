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

# Setup custom autocomplete
_poetry_run_completion() {
    local cur prev words cword
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    words=("${COMP_WORDS[@]}")
    cword=$COMP_CWORD

    # Find the dynamically generated poetry completion function
    poetry_completion_function=$(declare -F | awk '{print $3}' | grep -E '^_poetry_[0-9a-f]{16}_complete$')

    if [[ ${COMP_CWORD} -eq 2 && "${words[1]}" == "run" ]]; then
        # Complete the task (script) names from pyproject.toml
        _prun_completion
    elif [[ ${COMP_CWORD} -eq 1 && "${words[0]}" == "prun" ]]; then
        # Complete the task (script) names from pyproject.toml
        _prun_completion
    elif [[ ${COMP_CWORD} -gt 2 && "${words[1]}" == "run" ]]; then
        # After completing `poetry run <task>`, revert to normal Bash completion
        COMPREPLY=( $(compgen -o default -- "${cur}") )
    else
        case "${prev}" in
            poetry)
                # COMPREPLY=( $(compgen -W "run install add remove update" -- "${cur}") ) # Add other subcommands as needed
                "$poetry_completion_function"
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

_prun_completion() {
    local pyproject_script_commands=()

    if [[ -f "pyproject.toml" ]]; then
        pyproject_script_commands=($(awk '/\[tool.poetry.scripts\]/ {found=1; next} /\[.*\]/ {found=0} found && $0 !~ /^[[:space:]]*#/ {print $1}' pyproject.toml | sed "s/\(.*\)/\1/"))
    fi

    COMPREPLY=( $(compgen -W "${pyproject_script_commands[*]}" -- "${cur}") )
}

complete -F _poetry_run_completion poetry

