import schedule
import time
from countdown import countdown
import os
from rich.live import Live
from rich import print
from Modules.st import Speedtest
from Modules.we import MYWE
from Modules.connection import SQLiteDB
from Modules.email import Email
from Modules.progress import ProgressGroup
from Modules.progress import Procs
import Modules.tables
import asyncio
import ctypes, sys

"""
A simple Python program Made to Automate the Speedtest and Quota Scraping
    
    The Speedtest is Uses OoklaSpeedtest-cli Library
    Quota Check Works fine for Egyptian IPS Websites (WE Only In This Version)

    The Software is DataBase Structured.
    Sending the Results in HTML Format on Esetting.

The Code is East Follow and Easy Manipulation
The Code Made and tested on a Python 3.11
"""

def _import_database_rows():
    """
    Use Database Connection Module to Run Select Query Based On Each Table Name
    """
    _db_proc_lbl = Procs.add_task("[1] Import DataBase Tables")  # Create Process Task Label

    lines: list = SQLiteDB.select_table("LinesData")
    indicators: list = SQLiteDB.select_table('Indicators')[0]
    setting: list = SQLiteDB.select_table('Settings')[0]

    Procs.stop_task(_db_proc_lbl)
    Procs.update(
        _db_proc_lbl,
        description = f"[green][1] Import DataBase Tables",
        completed=True, finished_time=True)

    return lines, indicators, setting

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    live = Live(ProgressGroup, refresh_per_second=2, vertical_overflow="visible")
    live.start()

    # Import DataBase Tables
    # and Create Empty Rows

    lines, indicators, setting = _import_database_rows()

    # Start Speedtest and MYWE Scraping
    # Speedtest Will Running all at once (asyncio approach)
    # MYWE Will start at the same time of Speedtest but sequence

    async def st_mywe_start():
        task1 = asyncio.create_task(Speedtest.start(lines))
        task2 = asyncio.create_task(MYWE.start(lines))

        await task1
        await task2

    asyncio.run(st_mywe_start())

    live.stop()

    lines_result = [SQLiteDB.select_current_result(line) for line in lines]
    Modules.tables.print_result(lines_result)

    asyncio.run(Email.start(lines_result, setting, indicators))

    countdown(mins=int(setting['Periodically Hours'])*60, secs=0)
    schedule.every(int(setting['Periodically Hours'])).hours.do(main)

if __name__ == "__main__":

    if os.name == 'nt':
        os.system("cls")
    print("")

    if is_admin():
        main()
        while True:
            schedule.run_pending()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)