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
    receipients: list = []
    [receipients.append(line[1]) for line in DB.get_table('email_receipients')]
    email_settings: list = DB.get_table_as_dict('settings')[0]
    table: list = " ".join(EmailCreator.result_formated)

    for recipient in receipients:
        EmailSender.send(email_settings, recipient, table)  # Send Email

if __name__ == "__main__":
    # """Get Tables from the Data Bas"""
    lines: list = DB.get_table_as_dict(table_name = 'lines')
    # settings: list = DB.get_table_as_dict(table_name = 'settings')[0]
    # email_receipients: list = DB.get_table_as_dict(table_name = 'email_receipients')[0]
    # cc = settings['concurrency_count']

    # """Begenning of the process"""
    # list(map(DB.create_today_row, lines))   # Create Empty Row for all lines

    # st = Modules.st_library.st_start(lines, DB, cc)# Start Daily Speedtest

    with Progress(transient=True) as progress:  # Start Daily Interline QutaCheck
        try:
            lines_sorted: list = sorted(st, key=lambda d: float(d['download']), reverse=True)  # Sort lines by Download
            os.system(
                rf"""netsh interface ipv4 set address name=Ethernet static {lines_sorted['ip_address']} {lines_sorted['subnet_mask']} {lines_sorted['gateway']}"""
                )
        except:
            pass
        [asyncio.run(MyWE.start(progress, line, DB)) for line in lines ]

        if MyWE.faild:
        # Change to Second IP
            os.system(rf"""netsh interface ipv4 set address name=Ethernet static {lines_sorted[1]}""")  # Change to Best IP
            [asyncio.run(MyWE.start(progress, line, DB)) for line in MyWE.faild]

        if MyWE.faild:
        # Change to Second IP
            os.system(rf"""netsh interface ipv4 set address name=Ethernet static {lines_sorted[2]}""")  # Change to Best IP
            [asyncio.run(MyWE.start(progress, line, DB)) for line in MyWE.faild]
    
    lines_result = DB.get_last_result_dict(lines)
    Email.convert_line_to_html(lines_result)
    send_email()  # Send E-Email

    # os.system(rf"""netsh interface ipv4 set address name=Ethernet static {settings['primary_ip']} {settings['primary_subnetmask']} {settings['primary_gateway']}""")
