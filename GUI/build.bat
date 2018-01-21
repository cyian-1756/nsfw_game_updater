pyinstaller -F -w gui.py
robocopy . dist/ readme.md
robocopy . dist/ help.html
robocopy . dist/ tcl86t.dll
robocopy . dist/ tk86t.dll
pause