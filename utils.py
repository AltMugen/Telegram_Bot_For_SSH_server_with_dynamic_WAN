import subprocess
import re
from time import sleep

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

def extract_external_ip(output):
    sleep(10)
    match = re.search(r'ExternalIPAddress = (\d+\.\d+\.\d+\.\d+)', output)
    return match.group(1) if match else None

async def get_external_ip():
    output = run_command('upnpc -i -s')
    return extract_external_ip(output)

