#!/bin/bash

# Set the session name
SESSION_NAME="development_session"

# Start a new tmux session
tmux new-session -d -s $SESSION_NAME -x- -y-

# Rename the first window
tmux rename-window -t $SESSION_NAME:0 'Main'

# Create a vertical split (right)
tmux split-window -h

# Resize the panes
tmux select-pane -t 0
tmux resize-pane -x $(echo "$(tmux display -p "#{window_width}")*0.85/1" | bc)

# Run commands in each pane
tmux select-pane -t 0
tmux send-keys "clear" C-m

tmux select-pane -t 1
tmux send-keys "gs" C-m

tmux select-pane -t 0

# Attach to the session
tmux attach-session -t $SESSION_NAME
