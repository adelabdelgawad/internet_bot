import asyncio
import re
import os
import sys
from .banners import print_st_table
from .progress import Progress
from time import sleep


def _change_nic_ip(ip):
    print(f"Changing Ethernet: {ip['ip_address']} {ip['subnet_mask']} {ip['gateway']}")
    os.system(rf"""netsh interface ipv4 set address name=Ethernet static {ip['ip_address']} {ip['subnet_mask']} {ip['gateway']}""")
    sleep(2)

def _add_second_ip(ips):
    for ip in ips:
        print(f"Adding Secondery IP: {ip['ip_address']} {ip['subnet_mask']}")
        os.system(rf"""netsh interface ipv4 add address name=Ethernet {ip['ip_address']} {ip['subnet_mask']}""")
        sleep(.5)
    
async def _start_subprocess_shell(DB, line, cmd, progress, pb):
    """
    Create the subprocess; redirect the standard output
    into a pipe
    """
    # Default Values in case no captured
    ping = ''
    download = ''
    upload = ''

    # Sets to Containt Values
    downloads: set = set()
    uploads: set = set()
    pings: set = set()

    # Start of the Process
    for _ in range(3):
        proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()
        if stdout:
            results = stdout.decode().split(',')
            ping = int(float(results[5]))
            download = round(float(results[6]) / 1000 / 1000, 1)
            upload = round(float(results[7]) / 1000 / 1000, 1)
            print(f"{line['line_name']}: {ping}, {download}, {upload}")
        if stderr:
            print(f"[stderr] Error in: {line['ip_address']}, {stdout.decode()}")
        pings.add(ping)
        downloads.add(download)
        uploads.add(upload)
        progress.update(pb, advance=1)

    result = f"ping='{max(pings)}', upload='{max(uploads)}', download='{max(downloads)}'"
    await DB.add_result_to_today_line_row(line, result)


def st_start(lines, DB, cc)-> None:
    chuck_lines = [lines[i:i +cc] for i in range (0, len(lines), cc)]
    for chuck_line in chuck_lines:
        with Progress(transient=True) as progress:
            cloned_lines = chuck_line.copy()
            primary_ip = chuck_line.pop()

            _change_nic_ip(primary_ip)
            _add_second_ip(chuck_line)
            sleep(3)

            async def main():
                tasks: list = []
                for line in cloned_lines:
                    pb = progress.add_task(f"[red]{line['line_name']} Speedtest Progress...", total=3)
                    cmd = f"python speedtest.py --csv --secure --source {line['ip_address']}"
                    tasks.append(_start_subprocess_shell(DB, line, cmd, progress, pb))
                await asyncio.gather(*tasks)
            asyncio.run(main())
            sleep(1)

    lines_result = DB.get_today_results(lines)
    print_st_table(lines_result)

