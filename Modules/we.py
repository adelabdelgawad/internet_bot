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


async def _manipulate_parsered_data(soup, element: ClassID, remove_text:str):
    try:
        item = soup.find(class_=element).text.replace(remove_text, ' ')
        return int(float(item))
    except:
        return ' '


class MyWeBaseClass():
    """
    MyWe WebScraping BaseClase.
    ---------------------------

    Scraping Performing Based on Selenuim Using Chrome Browser for Login,
    and Pages Parsing Using BeautifullSoup Library
    """
    succeed: list = []
    faild: list = []

    async def run_browser(self) -> None:
        """
        Start Chrome WebDriver 
        """
        self.used: int = ' '
        self.used_percentage: int = ' '
        self.remaining: int = ' '
        self.balance: int = ' '
        self.usage: int = 0
        self.hours: int = 0
        self.credit_transaction: int = ' '
        self.renewal_date: str = ' '
        self.renewal_status: str = ' '

        self.browser = await self.driver
        self.browser.set_page_load_timeout(5)

    @property
    async def driver(self) -> SeleniumDriver:
        driver_exe = 'chromedriver'  # assign Path
        await asyncio.sleep(.2)
        options = webdriver.ChromeOptions()
        await asyncio.sleep(.2)
        options.add_argument("--headless")  # Open chome hidden
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        return  webdriver.Chrome(
            executable_path=driver_exe, options=options
            )

    async def login(self, line) -> bool:
        """
        MYWE Portal Site Login, and Return True/False Based on the Login State
        """
        self.line: list[dict] = line
        self.logged: bool = False

        try:
            self.browser.get("https://my.te.eg/user/login")  # Open WE Website
            element_present = EC.presence_of_element_located(("id", "login-service-number-et"))
            WebDriverWait(self.browser, 5).until(element_present)
            self.browser.find_element("id", "login-service-number-et").send_keys(self.line['PortalUsername']) # Sending Username
            await asyncio.sleep(.1)
            self.browser.find_element("id", "login-password-et").send_keys(self.line['PortalPassword'])  # Sending Password
            await asyncio.sleep(.1)
            self.browser.find_element("id", "login-login-btn").click() # Click Login Button
            element_present = EC.presence_of_element_located(("id", "welcome_card"))
            WebDriverWait(self.browser, 7).until(element_present)
            self.logged = True
        except Exception as ex:
            print(ex)
            MyWeBaseClass.faild.append(self.line)

    async def scrape_usage_page(self) -> None:
        """
        Parsing Account Overview page using BeautifulSoup technique [The First Page]
         Returning used, remaining, balance, usage and used_percentage
        """
        try:
            await asyncio.sleep(3)

            html = self.browser.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Automatic Return
            self.used = await _manipulate_parsered_data(soup, 'usage-details', ' Used')
            self.remaining = await _manipulate_parsered_data(soup, 'remaining-details', ' Remaining')
            self.balance = await _manipulate_parsered_data(soup, 'font-26px', ' ')

            # Manual Computing
            self.used_percentage = await self._compute_used_percentage
            self.credit_transaction = await self._compute_credit_transaction

            self.usage, self.hours = await self._compute_usage
        except:
            pass

    async def srape_renewdate_page(self) -> None:
        """
        Navigate to https://my.te.eg/offering/overview, 
        Returning RenewalDate and RenewalStatus
        """
        self.browser.get("https://my.te.eg/offering/overview")
        try:
            await asyncio.sleep(5)
            html = self.browser.page_source
            soup = BeautifulSoup(html, 'html.parser')
            self.renewal_date= soup.find(class_='mr-auto').text[14:-19]
            self.renewal_status = await self._compute_renewal_status
            MyWeBaseClass.succeed.append(self.line)
        except Exception as ex:
            print(ex)

    async def close_browser(self) -> None:
        """
        - Closes the browser and shuts down the ChromiumDriver executable
        that is started when starting the ChromiumDriver
        """    
        self.browser.quit()

    @property
    async def result(self) -> dict:
        if self.credit_transaction == 0:
            self.credit_transaction = ''
        if self.renewal_status == 0:
            self.renewal_status = ''
            
        return {
            'LineID': self.line['LineID'],
            'Used': self.used,
            'UsedPercentage': self.used_percentage,
            'Remaining': self.remaining,
            'Balance': self.balance,
            'Usage': self.usage,
            'RenewalDate': self.renewal_date,
            'Hours': self.hours,
            'Date': today,
            'DateTime': DateTime,
            'CreditTransaction': self.credit_transaction,
            'RenewalStatus': self.renewal_status
            }

    @property
    async def _compute_used_percentage(self) -> int:
        try:
            used_perc = (int(self.used) / (int(self.used) + int(self.remaining)))*100
            return int(used_perc)
        except:
            return 0

    @property
    async def _compute_usage(self) -> int:
        try:
            last_used = await SQLiteDB.select_last_result(self.line, 'Used', 'QuotaResult')
            if last_used:
                last_datetime = await SQLiteDB.select_last_result(self.line, 'DateTime','QuotaResult')
                last_datetime = datetime.strptime(last_datetime, "%d-%m-%Y %H:%M")
                now = datetime.now()
                diff = now - last_datetime
                diff = int(diff.total_seconds() / 3600)
                usage = int(self.used) - int(last_used)
                if int(usage) > 0:
                    return int(usage), int(diff)
            return 0, 0
        except Exception as ex:
            print(ex)
            return 0, 0

    @property
    async def _compute_credit_transaction(self) -> int:
        """
        Compare between current and last Balance to get the Credit Transaction Amount
        """
        last_balance = await SQLiteDB.select_last_result(self.line, 'balance', 'QuotaResult')
        if last_balance: # If last balance found
            if self.balance != last_balance: # if there is a difference between balance and last balance
                return (int(self.balance) - int(last_balance))
            else:
                return 0
        else:
            return 0

    @property
    async def _compute_renewal_status(self) -> str:
        if self.credit_transaction:
            if self.credit_transaction < 0: 
                last_renew_date = await SQLiteDB.select_last_result(self.line, 'RenewalDate','QuotaResult')
                if last_renew_date:
                    if last_renew_date == today:
                        return 'Automatic'
                    if last_renew_date != today:
                        return 'Manual'
            else:
                return 0
        else:
            return 0

MyWE = MyWeBaseClass()



async def start(lines: list[dict]):
    """
    MyWe WebScraping Performing Function.
    ---------------------------

    Scraping Performing Based on Selenuim Using Chrome Browser for Login,
    and Pages Parsing Using BeautifullSoup Library
    """
    _we_proc_lbl = Procs.add_task("[3] Start Internet Qouta Check")  # Create Process Task Label

    for index, line in enumerate(lines):
        index += 1
        task_pb = WEProgressBar.add_task(f"{index}. {line['LineName']} QuotaCheck", total=4)
        await MyWE.run_browser()
        await MyWE.login(line)

        if MyWE.logged:
            WEProgressBar.update(task_pb, advance=1)
            await MyWE.scrape_usage_page()
            WEProgressBar.update(task_pb, advance=1)
            await MyWE.srape_renewdate_page()
            WEProgressBar.update(task_pb, advance=1)
        resut = await MyWE.result
        await SQLiteDB.insert_result('QuotaResult', resut)
        WEProgressBar.update(task_pb, advance=1)

        await MyWE.close_browser()
        WEProgressBar.update(
            task_id = task_pb, finished_time=True
            )

    
    Procs.stop_task(_we_proc_lbl)
    Procs.update(
        _we_proc_lbl,
        description = f"[green][3] Start Internet Qouta Check",
        completed=True, finished_time=True)