import asyncio
from aiotestspeed.aio import Speedtest
from rich import print
from .connection import SQLiteDB
from .progress import TaskPB
from .progress import SubProc
from .shells import Shell

async def _start_aiotestspeed(line):
    TASK = TaskPB.create(f"{line['ip_address']} Speedtest", 3)

    ping, download, upload = 0, 0, 0  # Default Values in case no captured
    downloads, uploads, pings = set(), set(), set()  # Sets to Containt Values
    # Start of the Process
    for _ in range(3):
        try:
            cmd = f"python speedtest.py --csv --secure --source {line['ip_address']}"
            stdout, stderr = await Shell.run(cmd)
            if stdout:
                results = stdout.decode().split(',')
                ping = int(float(results[5]))
                download = round(float(results[6]) / 1000 / 1000, 1)
                upload = round(float(results[7]) / 1000 / 1000, 1)
                print(f"{line['line_name']}: {ping}, {download}, {upload}")
            if stderr:
                print(f"{line['ip_address']}:  {stderr.decode()}")
        except Exception as ex:
            print(f"{line['ip_address']}: {ex}")
        finally:
            pings.add(ping)
            downloads.add(download)
            uploads.add(upload)
            TaskPB.advance(TASK)

    result = f"ping='{max(pings)}', upload='{max(uploads)}', download='{max(downloads)}'"
    await SQLiteDB.add_result_to_today_line_row(line, result)

async def _modifing_address(primary_ip, chuck_line):
    # Changing Primary IP Address
    CHANGING_LABEL = SubProc.create_label("Modifying IP Addresses")
    await Shell.change_nic_ip(primary_ip)
    await asyncio.sleep(3)
    [await Shell.add_second_ip(line) for line in chuck_line]
    await asyncio.sleep(2)
    SubProc.finish_label(CHANGING_LABEL)

async def _executing_st(cloned_lines):
    await asyncio.sleep(.5)
    tasks: list = [_start_aiotestspeed(line) for line in cloned_lines]
    await asyncio.gather(*tasks)

def st_start(lines, cc)-> None:
    # Executing Speedtest
    chuck_lines = [lines[i:i +cc] for i in range (0, len(lines), cc)]
    for chuck_line in chuck_lines:
        cloned_lines = chuck_line.copy()
        primary_ip = chuck_line.pop()
        asyncio.run(_modifing_address(primary_ip, chuck_line))
        asyncio.run(_executing_st(cloned_lines))
        

