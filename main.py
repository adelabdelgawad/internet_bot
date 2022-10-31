from time import sleep
import os
from typing import Optional
from rich.progress import TaskID
import Modules.st as Speedtest
from Modules.we import MYWEBaseClass
from rich.live import Live
from Modules.shells import Shell
from Modules.progress import rich_console
from Modules.progress import Proc
from Modules.progress import RichOverall
from Modules.progress import SubProc
import connection
from rich.console import Console
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

DB = connection.DataBase("data.sqlite3")
MyWE = MYWEBaseClass()

main_console = Console()

def _start_quota_check(lines: list):
    """
    AsyncIO Function to Run Quota Scraping
    Function is Runs under Progress

    Argumentes:
        - Lines: list -> Each line is in Dic Format
    """
    [asyncio.run(MyWE.start(line, DB)) for line in lines ]


def _db_subproc(proc_pb: TaskID, db_table_name: str) -> list:
    _subproc_label = SubProc.create_label("importing lines information")
    result: list = DB.get_table(db_table_name)
    SubProc.finish_label(_subproc_label)
    Proc.advance_pb(proc_pb)
    return result
        
def _import_database_rows():
        _db_proc_lbl = Proc.create_label("[1] Import DataBase Tables")
        _db_pb = Proc.create_pb(4)

        lines: list = _db_subproc(_db_pb, "lines")
        [DB.create_today_row(line) for line in lines]  # Task

        settings: list = _db_subproc(_db_pb, 'settings')[0]
        cc: int = settings['concurrency_count']  # Uses in SpeedTest
        indicators: list = _db_subproc(_db_pb, 'indicators_limit')[0]
        email_receipients: list = _db_subproc(_db_pb, 'email_receipients')[0]

        # End the Progress Task
        SubProc.hide_labels()
        Proc.finish(_db_pb, _db_proc_lbl)

        return lines, settings, cc, indicators, email_receipients

def _change_to_bestline(lines):
    st_results = DB.get_today_results(lines)
    lines_sorted: list = sorted(st_results, key=lambda d: float(d['ping']))  # Sort lines by Ping
    # Loop in the lines list to get the line information and change the IPAddress
    for line in lines:
        if line['line_id'] == lines_sorted[0]['line_id']:
            asyncio.run(Shell.change_nic_ip(line))


if __name__ == "__main__":
    os.system("cls")
    print("")

    with Live(rich_console, refresh_per_second=30, vertical_overflow="visible") as live:
        RichOverall.construct_rows() # Call The Progress Rows
        print = live.console.print
        console = live.console

        overall_pb = RichOverall.create_pb("[red]Daily InternetCheck Speed and Quota...", 4)
        lines, settings, cc, indicators, email_receipients = _import_database_rows()
        RichOverall.advance(overall_pb)

        _st_proc_lbl = Proc.create_label("[2] Analysis Internet Speed Tests")
        Speedtest.st_start(lines, cc, DB) # Start Speedtest in Asyncio approach
        RichOverall.advance(overall_pb)

        # Change IP to Best Ping Latency Line
        _change_to_bestline(lines)
        
    # #     # # Change The IP Address after speed test Based on Ping results


    #     # # Start Quota Check
    #     # _start_quota_check(lines)
    #     # if MyWE.faild:
    #     #     get_best_line_and_change_nic_ip(lines, st_results, 1)
    #     #     _start_quota_check(MyWE.faild)
        
    #     # lines_result = DB.get_today_results(lines)
    #     # Email.convert_line_to_html(lines_result, indicators)
    #     # send_email()  # Send E-Email