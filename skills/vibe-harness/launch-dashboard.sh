#!/bin/bash
# Launch the Vibe Harness dashboard for the current project
# Usage: launch-dashboard.sh [project-dir]

DIR="${1:-$(pwd)}"
DASH="$HOME/.claude/skills/vibe-harness/dashboard.html"
PORT=9999

# Kill any existing dashboard server on this port
lsof -ti:$PORT 2>/dev/null | xargs kill 2>/dev/null
sleep 0.5

# Copy dashboard to project
cp "$DASH" "$DIR/harness-dashboard.html"

# Start server from project dir
python3 -m http.server $PORT &>/dev/null &
SERVER_PID=$!
echo "Dashboard server started (PID: $SERVER_PID, port: $PORT)"
echo "Project: $DIR"

# Open in browser
open "http://localhost:$PORT/harness-dashboard.html"

echo "Dashboard is live. Auto-refresh will pick up HARNESS-STATE.md changes."
echo "Press Ctrl+C to stop."

# Keep running until interrupted
trap "kill $SERVER_PID 2>/dev/null; echo 'Dashboard stopped.'; exit" INT TERM
wait $SERVER_PID
