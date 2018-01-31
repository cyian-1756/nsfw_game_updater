@echo off
REM pip3 install pipreqs
echo "Writing requirements.txt..."
pipreqs --force .
echo "building the .exe...."
pyinstaller -F -w gui.py
echo "Copying files..."
robocopy . dist/ readme.md
robocopy . dist/ help.html
robocopy . dist/ tcl86t.dll
robocopy . dist/ tk86t.dll
robocopy . dist/ favicon.ico
set /p version="Version Number: "
python package.py %version%
pause