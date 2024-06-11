# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

# Load the base environment
home

if [[ $(hostname) == *"login"* ]]
then
    module load Python/3.11.4 &&
    clear &&
    qs
else
    base &&
    activate_cur_venv
    if tmux has-session -t development_session 2>/dev/null
    then
        echo ""
    else
        dev-tmux
    fi
fi
