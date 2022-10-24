import Modules.st as Speedtest
from Modules.we import MYWEBaseClass
import Modules.we
from Modules.email import EmailCreator
from Modules.email import EmailSender
from Modules.progress import Progress
import connection
import asyncio
import os
from time import sleep

"""
A simple Python program Made to Automate the Speedtest and Quota Scraping
    
    The Speedtest is Uses OoklaSpeedtest-cli Library
    Quota Check Works fine for Egyptian IPS Websites (WE Only In This Version)

    The Software is DataBase Structured.
    Sending the Results in HTML Format on Email.

The Code is East Follow and Easy Manipulation
The Code Made and tested on a Python 3.10
"""


DB = connection.DataBase("data.db")
Email = EmailCreator()
MyWE = MYWEBaseClass()

def send_email() -> None:
    """
    Function Sequence:
        - Receipients: List ->  email to lists of receipients list
        - EmailSettings: List -> Using the Email Settings table in the DataBase
        - Tables: List -> Resultes of converted Lines in Table Format    
    """
    receipients = [line['email'] for line in DB.get_table('email_receipients')]
    email_settings: list = DB.get_table('settings')[0]
    tables: list = " ".join(EmailCreator.result_formated)

    # Sending Email for Loop in Receipients List
    [EmailSender.send(email_settings, recipient, tables) for recipient in receipients]

def _start_quota_check(lines: list):
    """
    AsyncIO Function to Run Quota Scraping
    Function is Runs under Progress

    Argumentes:
        - Lines: list -> Each line is in Dic Format
    """
    with Progress(transient=True) as progress:  # Start Daily Interline QutaCheck
        [asyncio.run(MyWE.start(progress, line, DB)) for line in lines ]

def get_best_line_and_change_nic_ip(lines: list, results: list, index: int):
    """
    Convert The NEtwork Interface Card to the best IPAdress
    The IPAdress Determined Based on Ping Result of SpeedTest

    :parameters:
        - Lines: list -> Each line is in Dic Format
        - Results: List -> Is the Result of speedtest Process
        - index: int -> is the sequence of the line index after sorted by Ping
    """
    # Sorting the list by Ping
    lines_sorted: list = sorted(results, key=lambda d: float(d['ping']), reverse=True)  # Sort lines by Download
    
    # Loop in the lines list to get the line information and change the IPAddress
    for line in lines:
        if line['line_id'] == lines_sorted[index]['line_id']:
            os.system(
            rf"""netsh interface ipv4 set address name=Ethernet static {line['ip_address']} {line['subnet_mask']} {line['gateway']}"""
            )
            print(f"Changing IP To: {line['ip_address']} {line['subnet_mask']} {line['gateway']}")
            sleep(5)
            
if __name__ == "__main__":
    """Init the Lists from The DB"""
    lines: list = DB.get_table('lines')  # Get Lines
    settings: list = DB.get_table('settings')[0]    # Get Settings List
    indicators: list = DB.get_table('indicators_limit')[0]    # Get Settings List
    email_receipients: list = DB.get_table('email_receipients')[0]  # Get Email Receivers
    cc = settings['concurrency_count']  # Uses in SpeedTest


    """Begging of the Process"""
    list(map(DB.create_today_row, lines))   # Create Empty Row for all lines

    Speedtest.st_start(lines, DB, cc)# Start Daily Speedtest

    # Change The IP Address after speed test Based on Ping results
    st_results = DB.get_today_results(lines)
    get_best_line_and_change_nic_ip(lines, st_results, 0)

    # Start Quota Check
    _start_quota_check(lines)
    if MyWE.faild:
        get_best_line_and_change_nic_ip(lines, st_results, 1)
        _start_quota_check(MyWE.faild)
    
    lines_result = DB.get_today_results(lines)
    Email.convert_line_to_html(lines_result, indicators)
    send_email()  # Send E-Email

