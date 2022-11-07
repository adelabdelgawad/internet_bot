from time import sleep
import os
from rich.live import Live
from Modules.st import Speedtest
from Modules.we import MYWE
from Modules.connection import SQLiteDB
from Modules.email import Email
from Modules.progress import ProgressGroup
from Modules.progress import Procs
import Modules.tables 
import asyncio

"""
A simple Python program Made to Automate the Speedtest and Quota Scraping
    
    The Speedtest is Uses OoklaSpeedtest-cli Library
    Quota Check Works fine for Egyptian IPS Websites (WE Only In This Version)

    The Software is DataBase Structured.
    Sending the Results in HTML Format on Email.

The Code is East Follow and Easy Manipulation
The Code Made and tested on a Python 3.10
"""

def _import_database_rows():
    _db_proc_lbl = Procs.add_task("[1] Import DataBase Tables")  # Create Process Task Label

    lines: list = SQLiteDB.select_table("LinesData")
    indicators: list = SQLiteDB.select_table('Indicators')[0]
    email_receipients: list = SQLiteDB.select_table('ReceipientsList')
    email_receipients = [receipient['EMail'] for receipient in email_receipients]

    Procs.stop_task(_db_proc_lbl)
    Procs.update(
        _db_proc_lbl,
        description = f"[green][1] Import DataBase Tables",
        completed=True, finished_time=True)

    return lines, indicators, email_receipients


if __name__ == "__main__":
    if os.name == 'nt':
        os.system("cls")
    print("")

    live = Live(ProgressGroup, refresh_per_second=2, vertical_overflow="visible")
    live.start()
    """
    Import DataBase Tables
    and Create Empty Rows
    """
    lines, indicators, email_receipients = _import_database_rows()

    # [SQLiteDB.create_today_row(line) for line in lines]  # Create Empty Today Rows
    
    """
    Start Speedtest and MYWE Scraping
    Speedtest Will Running all at once (asyncio approach)
    MYWE Will start at the same time of Speedtest but sequence
    """

    async def st_mywe_start():
        task1 = asyncio.create_task(Speedtest.start(lines))
        task2 = asyncio.create_task(MYWE.start(lines))

        await task1
        await task2

    asyncio.run(st_mywe_start())

    # asyncio.run(MYWE.start(lines))

    live.stop()

    lines_result = [SQLiteDB.select_current_result(line) for line in lines]
    Modules.tables.print_result(lines_result)

    Email.start(lines_result, email_receipients, indicators)

    print("Press Enter to continue ..." )
    input()


