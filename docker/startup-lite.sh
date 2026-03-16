#!/bin/bash
set -e

echo "╔══════════════════════════════════════╗"
echo "║     NexusOS Lite — Starting Up       ║"
echo "╚══════════════════════════════════════╝"

# Virtual display
Xvfb :1 -screen 0 ${RESOLUTION} -ac +extension GLX +render -noreset &
sleep 1

# Lightweight window manager
openbox &
sleep 0.5

# Panel (taskbar)
tint2 &

# VNC
x11vnc -display :1 -forever -shared -nopw -rfbport ${VNC_PORT} -bg

# noVNC web client
websockify --web /usr/share/novnc ${NOVNC_PORT} localhost:${VNC_PORT} &

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  NexusOS Lite is running!                            ║"
echo "║  Open: http://localhost:${NOVNC_PORT}/vnc.html              ║"
echo "╚══════════════════════════════════════════════════════╝"

# Start NexusOS
cd /home/nexus/nexus-os
export DISPLAY=:1
python3 run.py &

tail -f /dev/null
