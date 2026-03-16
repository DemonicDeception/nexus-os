#!/usr/bin/env python3
"""Quick launcher for NexusOS"""
from nexus.core import NexusOS

if __name__ == "__main__":
    nexus = NexusOS()
    nexus.interactive()
