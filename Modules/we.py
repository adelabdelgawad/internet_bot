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
now = datetime.now()
DateTime = datetime.now().strftime("%d-%m-%Y %H:%M")
now = now.strftime("%d-%m-%Y %H:%M")

ClassID = NewType("ClassID", str)
SeleniumDriver = NewType("SeleniumDriver", str)
DB_RowID = NewType("DB_RowID", str)

async def driver():
    driver_exe = 'chromedriver'  # assign Path
    await asyncio.sleep(.2)
    options = webdriver.ChromeOptions()
    await asyncio.sleep(.2)
    options.add_argument("--headless")  # Open chome hidden
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return  webdriver.Chrome(executable_path=driver_exe, options=options)


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
        QUOTATASK = WEProgressBar.add_task(f"{line['LineName']} QuotaCheck", total=4) 

        used: str = ''
        used_percentage: str = ''
        remaining: str = ''
        balance: str = ''
        renewal_date: str = ''
        usage: str = ''
        hours: str = ''
        credit_transaction: str = ''
        renewal_status: str = ''

        browser = await driver()

        if await MYWE.logged(browser, line, QUOTATASK):
            html = browser.page_source
            soup = BeautifulSoup(html, 'html.parser')
            WEProgressBar.update(QUOTATASK, advance=1)

            used = await MYWE._manipulate_parsered_data(soup, 'usage-details', ' Used')
            remaining = await MYWE._manipulate_parsered_data(soup, 'remaining-details', ' Remaining')
            balance = await MYWE._manipulate_parsered_data(soup, 'font-26px', ' ')
            WEProgressBar.update(QUOTATASK, advance=1)

            renewal_date = await MYWE._renewal_date(browser)
            WEProgressBar.update(QUOTATASK, advance=1)

            browser.quit()

            used_percentage = await MYWE._used_percentage(used, remaining)
            credit_transaction = await MYWE._credit_transaction(line, balance)
            renewal_status = await MYWE._renewal_status(line, credit_transaction)
            usage, hours = await MYWE._calculating_usage(line, used)
            if usage and hours:
                usage = int(float(usage))
                hours = int(float(hours))
            WEProgressBar.update(QUOTATASK, advance=1)
        
        result: dict = {
            'LineID': line['LineID'],
            'Used': used,
            'UsedPercentage': used_percentage,
            'Remaining': remaining,
            'Balance': balance,
            'Usage': usage,
            'RenewalDate': renewal_date,
            'Hours': hours,
            'Date': today,
            'DateTime': DateTime,
            'CreditTransaction': credit_transaction,
            'RenewalStatus': renewal_status
            }

        await SQLiteDB.insert_result('QuotaResult', result)
        
    @classmethod
    async def logged(cls, browser, line: dict, QUOTATASK: TaskID):
        try:
            browser.set_page_load_timeout(5)
            browser.get("https://my.te.eg/user/login")  # Open WE Website
            element_present = EC.presence_of_element_located(("id", "login-service-number-et"))
            WebDriverWait(browser, 5).until(element_present)
            browser.find_element("id", "login-service-number-et").send_keys(line['PortalUsername']) # Sending Username
            await asyncio.sleep(.1)
            browser.find_element("id", "login-password-et").send_keys(line['PortalPassword'])  # Sending Password
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
    async def _renewal_date(cls, browser: SeleniumDriver):
        """
        Go to Overview Page
        Get Renewal Date Value
        Add to value to The DataBase
        """
        browser.get("https://my.te.eg/offering/overview")
        await asyncio.sleep(3)
        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        return soup.find(class_='mr-auto').text[14:-19]
      
    @classmethod
    async def _manipulate_parsered_data(cls, soup, element: ClassID, remove_text:str):
        try:
            item = soup.find(class_=element).text.replace(remove_text, '')
            return int(float(item))
        except:
            return ''

    @classmethod
    async def _used_percentage(cls, used, remaining):
        try:
            used_perc = (int(used) / (int(used) + int(remaining)))*100
            return int(used_perc)
        except:
            return ''

    @classmethod
    async def _credit_transaction(cls, line: dict, balance: int):
        """
        Compare between current and last Balance to get the Credit Transaction Amount
        """
        last_balance = await SQLiteDB.select_last_result(line, 'balance', 'QuotaResult')
        if last_balance: # If last balance found
            if balance != last_balance: # if there is a difference between balance and last balance
                return (int(balance) - int(last_balance))
            else:
                return ""
        else:
            return ''

    @classmethod
    async def _renewal_status(cls, line: dict, credit_transaction: str):
        if credit_transaction:
            if credit_transaction < 0: 
                last_renew_date = await SQLiteDB.select_last_result(line, 'RenewalDate','QuotaResult')
                if last_renew_date:
                    if last_renew_date == today:
                        return 'Automatic'
                    if last_renew_date != today:
                        return 'Manual'
            else:
                return ''
        else:
            return ''

    @classmethod
    async def _calculating_usage(cls, line: dict, used: int):
        try:
            last_used = await SQLiteDB.select_last_result(line, 'Used', 'QuotaResult')
            if last_used:
                start = await SQLiteDB.select_last_result(line, 'DateTime','QuotaResult')
                start = datetime.strptime(start, "%d-%m-%Y %H:%M")
                end =   datetime.strptime(DateTime, "%d-%m-%Y %H:%M")
                diff = end - start
                diff = int(diff.total_seconds() / 3600)
                usage = int(used) - int(last_used)
                if int(usage) > 0:
                    return int(usage), int(diff)
            return '', ''
        except Exception as ex:
            return '', ''
