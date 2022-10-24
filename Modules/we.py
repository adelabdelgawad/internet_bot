from datetime import timedelta
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import asyncio
import urllib3
import os
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
today = datetime.strftime(datetime.now() - timedelta(0), '%d-%m-%Y')
time = datetime.now().strftime('%H:%M')

class MYWEBaseClass():
    succeed: list = []
    faild: list = []

    def __init__(self):
        self.soup = ''
        self.browser = ''
        self.remaining:str = ''
        self.used:str = ''
        self.balance:str = ''
        self.last_balance: str = ''
        self.renew_date:str = ''
        self.used_percentage:str = ''
        self.consumed:str = ''
        self.credit_transaction:str = ''
        self.renew_status:str = ''

    async def start(self, progress, line, DB):
        self.progress = progress
        self.pt = progress.add_task(f"[red]{line['line_name']} WE Scraping Progress.....", total=4)
        self.DB = DB
        self.line = line

        """ Beginning of the web coding"""
        self.browser = await self._driver   # (Property Method)
        self._logged_succeed = await self._open_mywe_and_login(self.browser)
        if self._logged_succeed:
            html = self.browser.page_source
            self.soup = BeautifulSoup(html, 'html.parser')
            self.progress.update(self.pt, advance=1)
            self.used = await self._used  # Used  (Property Method)
            self.remaining = await self._remaining  # Remaining  (Property Method)
            self.balance = await self._balance  # Balance  (Property Method)
            self.progress.update(self.pt, advance=1)
            self.renew_date = await self._renew_date  # Renew Date  (Property Method)
            self.progress.update(self.pt, advance=1)
            self.used_percentage = await self._used_percentage  # Used Percentage  (Property Method)
            self.last_used = await self._last_used  # Last Used  (Property Method)
            self.consumed = await self._consumed  # Consumed  (Property Method)
            self.credit_transaction = await self._credit_transaction  # Credit Transaction  (Property Method)
            self.renew_status = await self._renew_status  # Renew Status  (Property Method)
            self.progress.update(self.pt, advance=1)

    @property
    async def _driver(self):
        driver_exe = 'chromedriver'  # assign Path
        await asyncio.sleep(.2)
        options = webdriver.ChromeOptions()
        await asyncio.sleep(.2)
        options.add_argument("--headless")  # Open chome hidden
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        return webdriver.Chrome(executable_path=driver_exe, options=options)
        
    async def _open_mywe_and_login(self, browser):
        try:

            browser.set_page_load_timeout(7)
            browser.get("https://my.te.eg/user/login")  # Open WE Website
            element_present = EC.presence_of_element_located(("id", "login-service-number-et"))
            WebDriverWait(browser, 7).until(element_present)
            browser.find_element("id", "login-service-number-et").send_keys(self.line['user_name']) # Sending Username
            await asyncio.sleep(.1)
            browser.find_element("id", "login-password-et").send_keys(self.line['password'])  # Sending Password
            await asyncio.sleep(.1)
            browser.find_element("id", "login-login-btn").click() # Click Login Button
            element_present = EC.presence_of_element_located(("id", "welcome_card"))
            WebDriverWait(browser, 7).until(element_present)
            await asyncio.sleep(3)
            return True
        except:
            browser.quit()
            MYWEBaseClass.faild.append(self.line)
            return False

    @property
    async def _used(self):
        try:
            used = self.soup.find(class_='usage-details').text.replace(' Used', '')
            used = int(float(used))
        except:
            used = ''
        finally:
            result = f"used='{used}'"
            await self.DB.add_result_to_today_line_row(self.line, result)
            return used

    @property
    async def _remaining(self):
        try:
            remaining = self.soup.find(class_='remaining-details').text.replace(' Remaining', '')
            remaining = int(float(remaining))
        except:
            remaining = ''
        finally:
            result = f"remaining='{remaining}'"
            await self.DB.add_result_to_today_line_row(self.line, result)
            return remaining

    @property
    async def _balance(self):
        try:
            balance = self.soup.find(class_='font-26px').text.replace(' ', '')
            balance = int(float(balance))
        except:
            balance = ''
        finally:
            result = f"balance='{balance}'"
            await self.DB.add_result_to_today_line_row(self.line, result)
            return balance

    @property
    async def _renew_date(self):
        self.browser.get("https://my.te.eg/offering/overview")  # Open WE Website
        await asyncio.sleep(5)
        html = self.browser.page_source
        self.soup = BeautifulSoup(html, 'html.parser')
        try:
            renew_date = self.soup.find(class_='mr-auto').text[14:-19]
        except:
            renew_date = ''
        finally:
            result = f"renew_date='{renew_date}'"
            await self.DB.add_result_to_today_line_row(self.line, result)
            return renew_date

    @property
    async def _used_percentage(self):
        try:
            used_percentage = int(100 - (float(self.remaining)/float(self.line['package'])*100))
        except:
            used_percentage = ""
        finally:
            result = f"used_percentage='{used_percentage}'"
            await self.DB.add_result_to_today_line_row(self.line, result)
            return used_percentage
    
    @property
    async def _last_used(self):
        last_used: str = ''
        last_used = await self.DB.get_old_value(self.line, 'used')
        if last_used:
            return last_used

    @property
    async def _consumed(self):
        # Creating Consumed
        consumed : str = ''
        try: 
            if self.last_used:
                if int(self.used) > int(self.last_used):
                    consumed = int(self.used) - int(self.last_used)
                else:
                    consumed=self.used
            else:
                consumed=self.used
        except Exception as ex:
            print(ex)
        finally:
            result = f"consumed='{consumed}'"
            await self.DB.add_result_to_today_line_row(self.line, result)
            return consumed

    @property
    async def _credit_transaction(self):
        last_balance: str = ''
        try:
            # Getting Last Balance since one day to three days
            if await self.DB.get_old_value(self.line, 'balance'):
                last_balance = await self.DB.get_old_value(self.line, 'balance')

            if last_balance: # If last balance found
                if self.balance != last_balance: # if there is a difference between balance and last balance
                    credit_transaction = int(self.balance) - int(last_balance)
                    if credit_transaction < 100:    # In case a additional packages added (like real ip fees, taxes, etc..)
                        credit_transaction = ''
                else:
                    credit_transaction = ''
            else:
                credit_transaction = ''
            
        except Exception as ex:
            print(ex)
            credit_transaction = ''
        finally:
            result = f"credit_transaction='{credit_transaction}'"
            await self.DB.add_result_to_today_line_row(self.line, result)
            return credit_transaction

    @property
    async def _renew_status(self):
        if self.credit_transaction:
            if await self.DB.get_old_value(self.line, 'renew_date'):
                last_renew_date = await self.DB.get_old_value(self.line, 'renew_date')
            if last_renew_date == today:
               renew_status =  "Automatic"
            if last_renew_date != today:
                renew_status =  "Manual"
            result = f"renew_status='{renew_status}'"
            await self.DB.add_result_to_today_line_row(self.line, result)
            return renew_status
