import os
import sys
import subprocess

def open_file(path: str) -> None:
    if not os.path.exists(path):
        return
    if sys.platform.startswith('win'):
        os.startfile(path)
    elif sys.platform.startswith('darwin'):
        subprocess.run(['open', path])
    else:
        subprocess.Popen(['xdg-open', path])

def reveal_in_file_manager(path: str) -> None:
    if not os.path.exists(path):
        return
    if sys.platform.startswith('win'):
        subprocess.Popen(['explorer', '/select,', os.path.normpath(path)])
    elif sys.platform.startswith('darwin'):
        subprocess.run(['open', '-R', path])
    else:
        folder = path if os.path.isdir(path) else os.path.dirname(path)
        subprocess.Popen(['xdg-open', folder])
        