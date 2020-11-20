#!/bin/sh

# This is the session we'll create or attach to.
SESSION_NAME="badge-pull-requests"
MAIN_WINDOW="server"

add_nvim_window() {
    tmux new-window -d -t ${SESSION_NAME} -n $1
    tmux send-keys -t "${SESSION_NAME}:$1" "pipenv run nvim $1.py" Enter
    echo "created window $1"
}

attach_to_session() {
    # The test is to ensure it works from both outside
    # tmux and inside another tmux session.
    [ -n "${TMUX:-}" ] &&
        tmux switch-client -t ${SESSION_NAME} ||
        tmux attach-session -t ${SESSION_NAME}
}

if tmux has-session -t ${SESSION_NAME} 2> /dev/null; then
    echo "Session ${SESSION_NAME} already exists."
    attach_to_session
    exit 0
fi

# Debug
echo "session does not exist"

# Create a new session and name the first window server.
tmux new -d -s ${SESSION_NAME} -n ${MAIN_WINDOW}

# Split the server window in two and be ready to start
# the server on the bottom.
tmux splitw -v -d -t "${SESSION_NAME}:${MAIN_WINDOW}"
tmux resize-pane -D 20 -d -t "${SESSION_NAME}:${MAIN_WINDOW}" # doesn't work?

# Attach all the other windows
add_nvim_window streamlit_app
add_nvim_window streamlit_github
add_nvim_window streamlit_subprocess

# Finally, attach to the session we just created.
attach_to_session
