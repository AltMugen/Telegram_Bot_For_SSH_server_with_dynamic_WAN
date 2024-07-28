#utils.py
import subprocess
import re
import os
from config import WAN_IP_FILE

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

def extract_external_ip(output):
    match = re.search(r'ExternalIPAddress = (\d+\.\d+\.\d+\.\d+)', output)
    return match.group(1) if match else None

async def get_external_ip():
    output = run_command('upnpc -i -s')
    return extract_external_ip(output)

async def get_saved_wan_ip():
    if os.path.exists(WAN_IP_FILE):
        with open(WAN_IP_FILE, 'r') as file:
            return file.read().strip()
    return None

async def save_wan_ip(ip):
    with open(WAN_IP_FILE, 'w') as file:
        file.write(ip)

async def setup_port_forwarding(lip, lport, wport):
    command = f'upnpc -i -a {lip} {lport} {wport} TCP'
    run_command(command)
