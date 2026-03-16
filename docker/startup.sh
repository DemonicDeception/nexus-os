#!/bin/bash
set -e

echo "╔══════════════════════════════════════╗"
echo "║        NexusOS — Starting Up         ║"
echo "╚══════════════════════════════════════╝"

# Start virtual display
echo "[NexusOS] Starting virtual display at ${RESOLUTION}..."
Xvfb :1 -screen 0 ${RESOLUTION} -ac +extension GLX +render -noreset &
sleep 2

# Start D-Bus (needed for KDE)
export DBUS_SESSION_BUS_ADDRESS=$(dbus-daemon --session --fork --print-address)

# Start KDE window manager
echo "[NexusOS] Starting KDE Plasma desktop..."
kwin_x11 &
sleep 1

# Start Plasma shell
plasmashell &
sleep 2

# Start VNC server (no password for dev, add -passwd for production)
echo "[NexusOS] Starting VNC server on port ${VNC_PORT}..."
x11vnc -display :1 -forever -shared -nopw -rfbport ${VNC_PORT} -bg -o /tmp/x11vnc.log

# Start noVNC web client
echo "[NexusOS] Starting noVNC web client on port ${NOVNC_PORT}..."
websockify --web /usr/share/novnc ${NOVNC_PORT} localhost:${VNC_PORT} &

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  NexusOS is running!                                 ║"
echo "║                                                      ║"
echo "║  VNC:    vnc://localhost:${VNC_PORT}                       ║"
echo "║  Web:    http://localhost:${NOVNC_PORT}/vnc.html            ║"
echo "║                                                      ║"
echo "║  Open the Web URL in your browser to see the desktop ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Start NexusOS AI shell in the background
echo "[NexusOS] Starting AI shell..."
cd /home/nexus/nexus-os
export DISPLAY=:1
python3 -c "
from nexus.core import NexusOS
import threading, time

nexus = NexusOS()
print('[NexusOS] AI brain online. Listening for commands...')

# Keep alive
while True:
    time.sleep(1)
" &

# Keep container alive
tail -f /dev/null
