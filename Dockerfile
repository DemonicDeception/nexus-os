FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:1
ENV VNC_PORT=5900
ENV NOVNC_PORT=6080
ENV RESOLUTION=1920x1080x24

# Core system packages
RUN apt-get update && apt-get install -y \
    # Virtual display + VNC
    xvfb x11vnc novnc websockify \
    # KDE Plasma desktop (lightweight selection)
    plasma-desktop plasma-nm plasma-pa kwin-x11 \
    sddm breeze kde-cli-tools dolphin konsole kate \
    # System utilities
    dbus-x11 systemsettings \
    # Wine for .exe support
    wine64 wine32 \
    # App management
    flatpak software-properties-common \
    # Browsers and apps
    firefox \
    # File management
    thunar xarchiver \
    # Python + NexusOS dependencies
    python3 python3-pip python3-venv \
    # System tools NexusOS needs
    xdotool xclip scrot wmctrl \
    # Fonts (makes everything look good)
    fonts-noto fonts-liberation fonts-dejavu \
    # Build essentials
    curl wget git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up Flatpak for easy app installs
RUN flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo 2>/dev/null || true

# Create nexus user
RUN useradd -m -s /bin/bash nexus && \
    echo "nexus:nexus" | chpasswd && \
    adduser nexus sudo

# Install NexusOS
WORKDIR /home/nexus/nexus-os
COPY . .
RUN pip3 install --break-system-packages anthropic httpx pillow pyautogui mss pynput rich python-dotenv

# Startup script
COPY docker/startup.sh /startup.sh
RUN chmod +x /startup.sh

# Expose VNC and noVNC
EXPOSE 5900 6080

CMD ["/startup.sh"]
