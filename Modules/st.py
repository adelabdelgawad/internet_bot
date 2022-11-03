import asyncio
from rich import print
from .progress import (
    Procs,
    STProgressBar
)
from .connection import SQLiteDB
from .shell import Shell
import os

class Speedtest:
    """
    Defined Class to execute speedtest using Shell Process 
    Windows: Running Speedtest-cli using python speedtest.pt Module
    Linux: Running Speedtest 
    """

    @classmethod
    async def _start_aiotestspeed(cls, line: dict) -> None:
        """
        Speedtest Executer Method
        """
        ST_PB = STProgressBar.add_task(f"{line['ip_address']} Speedtest", total=3)

        ping, download, upload = 0, 0, 0  # Default Values in case no captured
        downloads, uploads, pings = set(), set(), set()  # Sets to Containt Values

        if os.name == 'nt': # Windows
            cmd = f"python speedtest.py --csv --secure --source {line['ip_address']}"
        else:   # Other Os
            cmd = f"speedtest --csv --secure --source {line['ip_address']}"

        for _ in range(3):
            try:
                stdout, stderr = await Shell.run(cmd)
                if stdout:
                    try:
                        results = stdout.decode().split(',')
                        ping = int(float(results[5]))
                        download = round(float(results[6]) / 1000 / 1000, 1)
                        upload = round(float(results[7]) / 1000 / 1000, 1)
                    except:
                        pass
                if stderr:
                    print(f"[red]{line['ip_address']}: {stderr}")
            except Exception as ex:
                print(f"[red]{line['ip_address']}: {ex}")
            finally:
                pings.add(ping)
                downloads.add(download)
                uploads.add(upload)
                STProgressBar.update(ST_PB , advance=1)

        STProgressBar.stop_task(ST_PB)

        result = f"ping='{max(pings)}', upload='{max(uploads)}', download='{max(downloads)}'"
        await SQLiteDB.add_result_to_today_line_row(line, result)
    
    @classmethod
    async def start(cls, lines: list[dict])-> None:
        """
        Asyncio method to run speedtest 3x times and append each time result in a set
         Final Results:
           Ping(TotalPing/3)
            Download(Best Download result)
           Upload(Best Upload result)
        """
        _st_proc_lbl = Procs.add_task("[2] Starting Ookla Speedtest")

        async def _executing_st(cloned_lines):
            tasks: list = [Speedtest._start_aiotestspeed(line) for line in cloned_lines]
            await asyncio.gather(*tasks)
        await _executing_st(lines)

        Procs.stop_task(_st_proc_lbl)
        Procs.update(
            _st_proc_lbl,
            description = f"[green][2] Starting Ookla Speedtest",
            completed=True, finished_time=True)
        

