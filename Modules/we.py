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
from .progress import SubProc
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
today = datetime.strftime(datetime.now() - timedelta(0), '%d-%m-%Y')
time = datetime.now().strftime('%H:%M')


ClassID = NewType("ClassID", str)
SeleniumDriver = NewType("SeleniumDriver", str)
DB_RowID = NewType("DB_RowID", str)

class MYWE():
    succeed: list = []
    faild: list = []

    @classmethod
    async def start(cls, line: dict):
        """
        Start MyWE Scraping Using Line Information
        Args:
         line: dic -> Line information
        """
        QUOTA_LABEL = SubProc.create_label(f"{line['line_name']} QuotaCheck") 
        QUOTA_PB = SubProc.create_pb(4)

        driver_exe = 'chromedriver'  # assign Path
        await asyncio.sleep(.2)
        options = webdriver.ChromeOptions()
        await asyncio.sleep(.2)
        # options.add_argument("--headless")  # Open chome hidden
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        browser =  webdriver.Chrome(executable_path=driver_exe, options=options)
        SubProc.advance_pb(QUOTA_PB)
        if await MYWE.logged(browser, line, QUOTA_PB, QUOTA_LABEL):
            html = browser.page_source
            soup = BeautifulSoup(html, 'html.parser')
            SubProc.advance_pb(QUOTA_PB)
            USED = await MYWE._grab_and_add_to_db(line, soup, 'usage-details', ' Used', 'used')
            REMAINING = await MYWE._grab_and_add_to_db(line, soup, 'remaining-details', ' Remaining', 'remaining')
            USED_PERCENTAGE = await MYWE._used_percentage(line, REMAINING)
            BALANCE = await MYWE._grab_and_add_to_db(line, soup, 'font-26px', ' ', 'balance')
            SubProc.advance_pb(QUOTA_PB)
            RENEWAL = await MYWE._grab_renewal_and_add_to_db(browser, line, 'renew_date')
            CREDIT_TRANSCATION = await MYWE._credit_transaction(line)
            RENEWA_STATUS = await MYWE._renew_status(CREDIT_TRANSCATION, line) 
            SubProc.advance_pb(QUOTA_PB)
            SubProc.finish_label(QUOTA_LABEL)
            SubProc.pb_finish(QUOTA_PB)
            browser.quit()

    @classmethod
    async def logged(cls, browser, line: dict, QUOTA_PB: TaskID, QUOTA_LABEL: TaskID):
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
            SubProc.finish_label(QUOTA_LABEL)
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
            last_renew_date = await SQLiteDB.get_old_value(line, 'renew_date')
            if last_renew_date:
                if last_renew_date == today:
                    result = f"renew_status='Automatic'"
                    await SQLiteDB.add_result_to_today_line_row(line, result)
                if last_renew_date != today:
                    result = f"renew_status='Manual'"
                    await SQLiteDB.add_result_to_today_line_row(line, result)
