# setup.py
from distutils.core import setup
import py2exe

py2exeoptions = {"py2exe":{"optimize": 2, "bundle_files":1}}

setup(windows=["gui.py"], options={"py2exe":{"optimize": 2, "bundle_files":1}})
