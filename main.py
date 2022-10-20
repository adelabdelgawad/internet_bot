import  Modules.st_library
import Modules.we_library
from Modules.email_lib import EmailCreator
from Modules.email_lib import EmailSender
import Modules.banners as Banner
from Modules.progress import Progress
import connection
import asyncio
from time import sleep
import os
from time import sleep


DB = connection.DataBase("DataBase.db")
Email = EmailCreator()

def send_email() -> None:
    receipients: list = []
    [receipients.append(line[1]) for line in DB.get_table('email_receipients')]
    email_settings: list = DB.get_table_as_dict('settings')[0]
    table: list = " ".join(EmailCreator.result_formated)

    for recipient in receipients:
        EmailSender.send(email_settings, recipient, table)  # Send Email


if __name__ == "__main__":
    lines: list = DB.get_table_as_dict(table_name = 'lines')
    settings: list = DB.get_table_as_dict(table_name = 'settings')[0]
    email_receipients: list = DB.get_table_as_dict(table_name = 'email_receipients')[0]
    cc = settings['concurrency_count']

    list(map(DB.create_today_row, lines))

    # Start Daily Speedtest 
    Modules.st_library.st_start(lines, DB, cc)
    sleep(1)
    
    lines_result = DB.get_last_result_dict(lines)
    print('here')
    Banner.print_st_table(lines_result)

    # Start Daily Interline QutaCheck
    with Progress(transient=True) as progress:
        best_line: list = sorted(lines_result, key=lambda d: float(d['download']), reverse=True)
        asyncio.run(Modules.we_library.start_mywe(progress, DB, lines, best_line))

    # E-Mail
    Email.convert_line_to_html(lines_result)
    send_email()  # Send E-Email

    os.system(rf"""netsh interface ipv4 set address name=Ethernet static {settings['primary_ip']} {settings['primary_subnetmask']} {settings['primary_gateway']}""")
