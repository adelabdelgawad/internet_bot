import asyncio
from multiprocessing.connection import wait
from aiotestspeed.aio import Speedtest
from rich import print
from .progress import TaskPB
from .progress import SubProc
from .progress import SpeedtestTable
from .connection import SQLiteDB
from .shells import Shell
import time

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
                SpeedtestTable.add_row(
                    "Speedtest",
                    f"{line['line_name']}",
                    f"[green]Latency {ping}ms, Download: {download}mb/s, Upload: {upload}mb/s"
                    )
                await asyncio.wait(1)

            if stderr:
                SpeedtestTable.add_row(
                    "Speedtest",
                    f"{line['line_name']}",
                    f"[red]{stderr.decode()}"
                    )
            await asyncio.sleep(1)
        except Exception as ex:
            SpeedtestTable.add_row(
                "Speedtest",
                f"{line['line_name']}",
                f"[red]{ex.decode()}"
                )
            await asyncio.sleep(1)
        finally:
            pings.add(ping)
            downloads.add(download)
            uploads.add(upload)
            TaskPB.advance(TASK)
        TaskPB.finish(TASK)
        await asyncio.sleep(1)

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
    ST_Label = SubProc.create_label("Starting Ookla Speedtest")
    
    await asyncio.sleep(.5)
    tasks: list = [_start_aiotestspeed(line) for line in cloned_lines]
    await asyncio.gather(*tasks)

    SubProc.finish_label(ST_Label)

def st_start(lines, cc)-> None:
    # Executing Speedtest
    chuck_lines = [lines[i:i +cc] for i in range (0, len(lines), cc)]
    for chuck_line in chuck_lines:
        cloned_lines = chuck_line.copy()
        primary_ip = chuck_line.pop()
        asyncio.run(_modifing_address(primary_ip, chuck_line))
        SpeedtestTable.add_column("Task Type")
        SpeedtestTable.add_column("Line Name")
        SpeedtestTable.add_column("Result")
        asyncio.run(_executing_st(cloned_lines))
    
        
