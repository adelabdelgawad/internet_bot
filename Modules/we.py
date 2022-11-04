from datetime import timedelta
from datetime import datetime
from selenium import webdriver
from rich.progress import TaskID
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import asyncio
import urllib3
from typing import NewType
from .connection import SQLiteDB
from .progress import (
    Procs,
    WEProgressBar
)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
today = datetime.strftime(datetime.now() - timedelta(0), '%d-%m-%Y')
time = datetime.now().strftime('%H:%M')
date = f"{today} | {time}"

ClassID = NewType("ClassID", str)
SeleniumDriver = NewType("SeleniumDriver", str)
DB_RowID = NewType("DB_RowID", str)

class MYWE():
    succeed: list = []
    faild: list = []

    @classmethod
    async def start(cls, lines):
        _we_proc_lbl = Procs.add_task("[3] Start Internet Qouta Check")  # Create Process Task Label

        [await MYWE.start_scraping(line) for line in lines]

        Procs.stop_task(_we_proc_lbl)
        Procs.update(
            _we_proc_lbl,
            description = f"[green][3] Start Internet Qouta Check",
            completed=True, finished_time=True)

    @classmethod
    async def start_scraping(cls, line: dict):
        """
        Start MyWE Scraping Using Line Information
        Args:
         line: dic -> Line information
        """
        QUOTATASK = WEProgressBar.add_task(f"{line['line_name']} QuotaCheck", total=3) 

        driver_exe = 'chromedriver'  # assign Path
        await asyncio.sleep(.2)
        options = webdriver.ChromeOptions()
        await asyncio.sleep(.2)
        options.add_argument("--headless")  # Open chome hidden
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        browser =  webdriver.Chrome(executable_path=driver_exe, options=options)
        if await MYWE.logged(browser, line, QUOTATASK):
            html = browser.page_source
            soup = BeautifulSoup(html, 'html.parser')
            WEProgressBar.update(QUOTATASK, advance=1)
            USED = await MYWE._grab_and_add_to_db(line, soup, 'usage-details', ' Used', 'used')
            usage = await MYWE._usage_calculation(USED, line)
            REMAINING = await MYWE._grab_and_add_to_db(line, soup, 'remaining-details', ' Remaining', 'remaining')
            USED_PERCENTAGE = await MYWE._used_percentage(line, REMAINING)
            BALANCE = await MYWE._grab_and_add_to_db(line, soup, 'font-26px', ' ', 'balance')
            WEProgressBar.update(QUOTATASK, advance=1)
            RENEWAL = await MYWE._grab_renewal_and_add_to_db(browser, line, 'renew_date')
            CREDIT_TRANSCATION = await MYWE._credit_transaction(line)
            RENEWA_STATUS = await MYWE._renew_status(CREDIT_TRANSCATION, line)
            usage = await MYWE._renew_status(CREDIT_TRANSCATION, line)

            WEProgressBar.update(QUOTATASK, advance=1)
            browser.quit()

    @classmethod
    async def logged(cls, browser, line: dict, QUOTATASK: TaskID):
        try:
            browser.set_page_load_timeout(5)
            browser.get("https://my.te.eg/user/login")  # Open WE Website
            element_present = EC.presence_of_element_located(("id", "login-service-number-et"))
            WebDriverWait(browser, 5).until(element_present)
            browser.find_element("id", "login-service-number-et").send_keys(line['user_name']) # Sending Username
            await asyncio.sleep(.1)
            browser.find_element("id", "login-password-et").send_keys(line['password'])  # Sending Password
            await asyncio.sleep(.1)
            browser.find_element("id", "login-login-btn").click() # Click Login Button
            element_present = EC.presence_of_element_located(("id", "welcome_card"))
            WebDriverWait(browser, 7).until(element_present)
            await asyncio.sleep(3)
            return True
        except:
            browser.quit()
            MYWE.faild.append(line)
            WEProgressBar.stop_task(QUOTATASK)
            return False

    @classmethod
    async def _grab_and_add_to_db(cls, line, soup, element: ClassID, remove_text:str, row_id: DB_RowID):
        item = soup.find(class_=element).text.replace(remove_text, '')
        item =  int(float(item))
        result = f"{row_id}='{item}'"
        await SQLiteDB.add_result_to_today_line_row(line, result)
        return item

    @classmethod
    async def _grab_renewal_and_add_to_db(cls, browser: SeleniumDriver, line: dict, row_id: DB_RowID):
        """
        Go to Overview Page
        Get Renewal Date Value
        Add to value to The DataBase
        """
        browser.get("https://my.te.eg/offering/overview")
        await asyncio.sleep(5)
        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        result = soup.find(class_='mr-auto').text[14:-19]
        result = f"{row_id}='{result}'"
        await SQLiteDB.add_result_to_today_line_row(line, result)

    @classmethod
    async def _used_percentage(self, line: dict, remaining):
        if remaining:
            result = int(100 - (float(remaining)/float(line['package'])*100))
            result = f"used_percentage='{result}'"
            await SQLiteDB.add_result_to_today_line_row(line, result)
        else:
            result = f"used_percentage=''"
            await SQLiteDB.add_result_to_today_line_row(line, result)
    
    @classmethod
    async def _credit_transaction(cls, line: dict):
        """
        Compare between current and last Balance to get the Credit Transaction Amount
        """
        last_balance = await SQLiteDB.get_old_value(line, 'balance')
        balance = await SQLiteDB.get_today_row_result(line, 'balance')
        if last_balance: # If last balance found
            if balance != last_balance: # if there is a difference between balance and last balance
                credit_transaction = int(balance) - int(last_balance)
                result = f"credit_transaction='{credit_transaction}'"
                await SQLiteDB.add_result_to_today_line_row(line, result)
                return credit_transaction

    @classmethod
    async def _renew_status(cls, credit_transaction: str, line: dict):
        if credit_transaction:
            if credit_transaction < 0: 
                last_renew_date = await SQLiteDB.get_old_value(line, 'renew_date')
                if last_renew_date:
                    if last_renew_date == today:
                        result = f"renew_status='Automatic'"
                        await SQLiteDB.add_result_to_today_line_row(line, result)
                    if last_renew_date != today:
                        result = f"renew_status='Manual'"
                        await SQLiteDB.add_result_to_today_line_row(line, result)

    @classmethod
    async def _usage_calculation(cls, used: int, line: dict) -> dict:
        last_used = await SQLiteDB.get_old_value(line, 'used')
        if last_used:
            start = await SQLiteDB.get_old_value(line, 'time')
            start = datetime.strptime(start, "%d-%m-%Y | %H:%M")
            end =   datetime.strptime(date, "%d-%m-%Y | %H:%M")
            diff = end - start
            diff = int(diff.total_seconds() / 3600)
            usage = int(used) - int(last_used)
            if int(usage) > 0:
                result = f"usage={usage}"
                await SQLiteDB.add_result_to_today_line_row(line, result)
                result = f"dif_hours={diff}"
                await SQLiteDB.add_result_to_today_line_row(line, result)
            return
        result = f"usage=''"
        await SQLiteDB.add_result_to_today_line_row(line, result)
