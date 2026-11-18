# Run once: python get_icon.py
# Extracts gear icon from Windows shell32.dll → service.ico
import ctypes, os, struct

RES_ICON = 3
shell32_path = r"C:\Windows\System32\shell32.dll"

# icon index 19 = classic Windows services gear
os.system(
    'powershell -NoProfile -Command "'
    'Add-Type -AssemblyName System.Drawing; '
    '[System.Drawing.Icon]::ExtractAssociatedIcon('
    r"'C:\Windows\System32\services.exe'"
    ').Save(\'service.ico\')"'
)
print("service.ico saved — commit this file to the repo")
