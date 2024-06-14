# don't put duplicate lines or lines starting with space in the history.
# See bash(1) for more options
HISTCONTROL=ignoreboth

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=1000
HISTFILESIZE=2000

# Colors for the terminal
BLUE="\033[34m"
GREEN="\033[32m"
MAGENTA="\033[35m"
RESET="\033[0m"

# Fuzzy find function for command history
fzf_history_search() {
    local selected_command
    selected_command=$(history | awk '{$1=""; print substr($0,2)}' | fzf --height 40% --layout=reverse)
    
    if [ -n "$selected_command" ]; then
        READLINE_LINE="$selected_command"
        READLINE_POINT=${#selected_command}
    fi
}

# Bind Ctrl+R to the fuzzy find history search function
bind -x '"\C-r": fzf_history_search'

# Bind Up arrow key to the fuzzy find history search function
bind '"\e[A": "\C-r"'
