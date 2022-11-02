from time import sleep
import os
from rich.console import Console
from rich.live import Live
from rich.progress import TaskID
if os.name == 'nt':
    import Modules.win_st as Speedtest
else:
    import Modules.linux_st as Speedtest
from Modules.we import MYWE
from Modules.shells import Shell
from Modules.email import Email
from Modules.progress import ProgressGroup
from Modules.progress import Proc
from Modules.progress import RichOverall
from Modules.progress import SubProc
from Modules.connection import SQLiteDB
from Modules.tables import results_table

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

main_console = Console()

def _db_subproc(proc_pb: TaskID, db_table_name: str) -> list:
    _subproc_label = SubProc.label_create("importing lines information")
    result: list = SQLiteDB.get_table(db_table_name)
    SubProc.label_finish(_subproc_label)
    Proc.advance_pb(proc_pb)
    return result


def _import_database_rows():
        _db_proc_lbl = Proc.label_create("[1] Import DataBase Tables")
        _db_pb = Proc.pb_create(4)

        lines: list = _db_subproc(_db_pb, "lines")
        [SQLiteDB.create_today_row(line) for line in lines]  # Task

        settings: list = _db_subproc(_db_pb, 'settings')[0]
        cc: int = settings['concurrency_count']  # Uses in SpeedTest

        # End the Progress Task
        SubProc.labels_hide()
        Proc.finish(_db_pb, _db_proc_lbl)

        return lines, settings, cc


if __name__ == "__main__":
    if os.name == 'nt':
        os.system("cls")
    print("")

    with Live(ProgressGroup, refresh_per_second=30, vertical_overflow="visible") as live:
        print = live.console.print

        overall_pb = RichOverall.pb_create("[red]Daily InternetCheck Speed and Quota...", 4)
        lines, settings, cc = _import_database_rows()
        RichOverall.advance(overall_pb)

    #     _st_proc_lbl = Proc.label_create("[2] Analysis Internet Speed Tests")
    #     Speedtest.st_start(lines, cc) # Start Speedtest in Asyncio approach
    #     Proc.label_finish(_st_proc_lbl)

    #     BST_LBL = SubProc.label_create("Chaning ip address to best latency line")
    #     Shell.change_to_bestline(lines)
    #     SubProc.label_finish(BST_LBL)

    #     SubProc.labels_hide()
    #     RichOverall.advance(overall_pb) 
          
    #     _we_proc_lbl = Proc.label_create("[3] Start Internet Qouta Check")
    #     [asyncio.run(MYWE.start(line)) for line in lines ]
    #     SubProc.labels_hide()
    #     Proc.label_finish(_we_proc_lbl)

    # #     # # Start Quota Check
    # #     # _start_quota_check(lines)
    # #     # if MyWE.faild:
    # #     #     get_best_line_and_change_nic_ip(lines, st_results, 1)
    # #     #     _start_quota_check(MyWE.faild)
        
        lines_result = SQLiteDB.get_today_results(lines)
        print(results_table(lines_result))

        Email.start(lines_result)
