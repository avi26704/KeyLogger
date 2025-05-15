# Windows Keylogger with Auto Email & Startup

This is a stealth keylogger for Windows that captures keystrokes, clipboard data, and system information. It sends regular email reports and runs silently on system startup using Windows Task Scheduler.

## Features

- Keystroke logging with human-readable formatting

- Clipboard monitoring

- System and GPU information gathering

- Periodic email reporting with log attachments

- Auto-run on boot using Task Scheduler

- Self-aware startup (prevents duplicate task creation)

- Silent background operation (no console or windows)

- Compilable to a standalone `.exe` using PyInstaller

## Dependencies used

**Dependencies and their Usage:**

- `pynput`: Listens to and captures keyboard input.

- `python-dotenv`: Loads environment variables from a `.env` file.

- `GPUtil`: Retrieves GPU information.

- `psutil`: Gathers system and hardware information (CPU, memory, boot time).

- `tabulate`: Formats GPU information in a table.

- `pywin32 (win32clipboard)`: Accesses and reads clipboard contents on Windows.

- `requests`: Fetches the public IP address via a web API.

- `smtplib`, `email.mime`: Sends emails with log attachments.

- `threading.Timer`: Schedules periodic email sending.

- `platform`: Gets system platform and architecture details.

- `os`, `socket`, `getpass`, `time`, `datetime`: Standard Python libraries for OS interactions, networking, timing, and file handling.

## Execution

Once run, the script will:

- Gather system information (once)

- Capture clipboard contents

- Start listening for keystrokes

- Create a scheduled task named `WindowsSecUpdate` to run the logger at each login

- Send log files via email every 5 minutes (default)

## File Logs

The following logs are saved temporarily in `APPDATA`:

- `System32.txt` — Keystrokes

- `SystemClip.txt` — Clipboard data

- `System64.txt` — System info (sent only once)

These files are deleted after each email is sent.

## Safety Disclaimer

This project is for **educational purposes only**. Unauthorized use of this software to record user activity without consent is illegal and unethical. Use responsibly and only on systems you own or have explicit permission to monitor.
