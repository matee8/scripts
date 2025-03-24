#!/bin/env bash

SESSION_NAME="google_drive_mount"

if [ "$1" == "mount" ]; then
    tmux new-session -d -s "$SESSION_NAME";
    tmux send -t $SESSION_NAME:0 "rclone mount psg_drive: ~/PsgDrive" ENTER;
    echo "Google drive mounted."
elif [ "$1" == "umount" ]; then
    tmux send -t $SESSION_NAME:0 C-c;
    tmux kill-session -t $SESSION_NAME;
    echo "Google drive unmounted."
else
    echo "Usage: $0 <mount|umount>"
    exit 1
fi
