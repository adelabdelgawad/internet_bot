import  Modules.st_library
from datetime import datetime
from Modules.we_library import MYWEBaseClass
import Modules.we_library
from Modules.email_lib import EmailCreator
from Modules.email_lib import EmailSender
import Modules.banners as Banner
from Modules.progress import Progress
import connection
import asyncio
from time import sleep
import os

DB = connection.DataBase("DataBase.db")
Email = EmailCreator()
MyWE = MYWEBaseClass()

def send_email() -> None:
    receipients = [line['email'] for line in DB.get_table('email_receipients')]
    email_settings: list = DB.get_table('settings')[0]
    table: list = " ".join(EmailCreator.result_formated)

    [EmailSender.send(email_settings, recipient, table) for recipient in receipients]

def _start_quota_check(lines):
    with Progress(transient=True) as progress:  # Start Daily Interline QutaCheck
        for line in lines:
            if line['isp'] == 'WE':
                [asyncio.run(MyWE.start(progress, line, DB)) for line in lines ]
            else:
                print("UnCoded ISP")

def get_best_line_and_change_nic_ip(lines, results, index):
    try:
        lines_sorted: list = sorted(results, key=lambda d: float(d['download']), reverse=True)  # Sort lines by Download
        for line in lines:
            if line['line_id'] == lines_sorted[index]['line_id']:
                os.system(
                rf"""netsh interface ipv4 set address name=Ethernet static {line['ip_address']} {line['subnet_mask']} {line['gateway']}"""
                )
    except Exception as ex:
        print(ex)

if __name__ == "__main__":
    # """Get Tables from the Data Base"""
    lines: list = DB.get_table(table_name = 'lines')
    settings: list = DB.get_table(table_name = 'settings')[0]
    email_receipients: list = DB.get_table(table_name = 'email_receipients')[0]
    cc = settings['concurrency_count']

    """Begenning of the process"""
    list(map(DB.create_today_row, lines))   # Create Empty Row for all lines

    Modules.st_library.st_start(lines, DB, cc)# Start Daily Speedtest

    # Quota Check
    results = DB.get_today_results(lines)
    get_best_line_and_change_nic_ip(lines, results, 0)
    _start_quota_check(lines)
    if MyWE.faild:
        get_best_line_and_change_nic_ip(lines, results, 1)
        _start_quota_check(MyWE.faild)

    lines_result = DB.get_today_results(lines)
    Email.convert_line_to_html(lines_result)
    send_email()  # Send E-Email

    os.system(rf"""netsh interface ipv4 set address name=Ethernet static {settings['primary_ip']} {settings['primary_subnetmask']} {settings['primary_gateway']}""")
