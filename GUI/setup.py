import sys
from cx_Freeze import setup, Executable
import os


os.environ['TCL_LIBRARY'] = r'D:\Softwares\python-362-x86\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'D:\Softwares\python-362-x86\tcl\tk8.6'
# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os", "sys", "tkinter", "time", "configparser", "json", "requests", "re", "platform", "mediafire", "pyperclip", "webbrowser", "praw", "threading"]\
					, "include_files":["help.html", "readme.md", "config.cfg", "games.json"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "NSFW Game Manager",
        version = "1.0.0",
        description = "NSFW Game Manager, for all your lewd gaming activities",
        options = {"build_exe": build_exe_options},
        executables = [Executable("gui.py", base=base)])
