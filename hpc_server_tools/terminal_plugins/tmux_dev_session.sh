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
# Define the minimum width required for the right pane
min_right_pane_width=25

# Get the total width of the terminal
total_width=$(tmux display -p "#{window_width}")

# Calculate the target width for pane 0 (85% of total width)
target_left_pane_width=$(echo "$total_width*0.85/1" | bc)

# Calculate the remaining width for the right pane
right_pane_width=$(($total_width - $target_left_pane_width))

# If the right pane is too small, adjust the left pane width
if [ $right_pane_width -lt $min_right_pane_width ]; then
  target_left_pane_width=$(($total_width - $min_right_pane_width))
fi

# Resize pane 0 to the calculated width
tmux resize-pane -x $target_left_pane_width

# Run commands in each pane
tmux select-pane -t 0
tmux send-keys "clear" C-m

tmux select-pane -t 1
tmux send-keys "gs" C-m

tmux select-pane -t 0

# Attach to the session
tmux attach-session -t $SESSION_NAME
