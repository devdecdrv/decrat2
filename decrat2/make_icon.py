import subprocess

subprocess.run([
    "powershell", "-NoProfile", "-Command",
    "Add-Type -AssemblyName System.Drawing; "
    "$i = [System.Drawing.Icon]::ExtractAssociatedIcon('C:\\Windows\\System32\\services.exe'); "
    "$i.Save('service.ico')"
], check=True)
print("service.ico created")
