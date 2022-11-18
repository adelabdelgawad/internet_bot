import time
import os
import schedule
from rich.live import Live
from rich import print
from Modules.st import Speedtest
import Modules.we as MyWE
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
    Emailing the Results in HTML Format to Recepients and CC Lists.
    Already tested With Exchange Internal Server

The Code Made and tested on a Python 3.11
"""

def _import_database_rows():
    """
    Select data from a database. and Store in List variables
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
    """
    Check if code runs in an elevated priviledges
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    """
    Main Performing Function
    Import DB, Start Both Speedtest and MYWE in asyncio/await approach
    """
    if os.name == 'nt':  # If Windows
        os.system("cls")
        print("")
        
    live = Live(ProgressGroup, refresh_per_second=3, vertical_overflow="visible")
    live.start()

    lines, indicators, setting = _import_database_rows()

    async def st_mywe_start():
        """
        Start Speedtest and MYWE Scraping
        Speedtest Will Running all at once (asyncio approach)
        MYWE Will start at the same time of Speedtest but sequence
        """
        task1 = asyncio.create_task(Speedtest.start(lines))
        task2 = asyncio.create_task(MyWE.start(lines))

        await task1
        await task2

    asyncio.run(st_mywe_start())
    

    live.stop()

    lines_result = [SQLiteDB.select_current_result(line) for line in lines]
    Modules.tables.print_result(lines_result)

    asyncio.run(Email.start(lines_result, setting, indicators))

    time.sleep(60)



if __name__ == "__main__":
    if is_admin():
        main()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)