@echo off
pyinstaller -F -w gui.py
robocopy . dist/ readme.md
robocopy . dist/ help.html
robocopy . dist/ tcl86t.dll
robocopy . dist/ tk86t.dll
set /p version="Version Number: "
python package.py %version%
pause