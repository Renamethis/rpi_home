#!/usr/bin/env python3

from dataclasses import dataclass, fields, asdict
from enviro_server.EnvironmentThread import EnvironmentThread

if __name__ == '__main__':
    mainthread = EnvironmentThread()
    mainthread.start()