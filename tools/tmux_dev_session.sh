#!/bin/bash

# Set the session name
SESSION_NAME="development_session"

# Start a new tmux session
tmux new-session -d -s $SESSION_NAME

# Rename the first window
tmux rename-window -t $SESSION_NAME:0 'Main'

# Create a vertical split (right)
tmux split-window -h

# Create a horizontal split in the right pane (bottom)
tmux select-pane -t 1
tmux split-window -v

# Resize the panes
tmux select-pane -t 0
tmux resize-pane -R 80 # Adjust this value to resize the left pane

tmux select-pane -t 1
tmux resize-pane -U 5  # Adjust this value to resize the top right pane

# Run commands in each pane
tmux select-pane -t 0
tmux send-keys "clear" C-m

tmux select-pane -t 1
tmux send-keys "gs" C-m

tmux select-pane -t 2
tmux send-keys "htop" C-m

tmux select-pane -t 0

# Attach to the session
tmux attach-session -t $SESSION_NAME
