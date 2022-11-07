import sqlite3
import aiosqlite
import asyncio
from datetime import timedelta
from datetime import datetime
from typing import NewType


"""
The DataBase Manipulation Module
Uses SQLite Standard Module
and AIOSQLITE ASYNCIO Model Modules
"""
today = datetime.strftime(datetime.now() - timedelta(0), '%d-%m-%Y')
yesterday = datetime.strftime(datetime.now() - timedelta(1), '%d-%m-%Y')

now = datetime.now()
DateTime = datetime.now().strftime("%d/%m/%Y %H:%M")
now = now.strftime("%d/%m/%Y %H:%M")

TableName = NewType("TableName", str)

def dict_factory(cursor: str, row: int) -> dict:
    """
    Convert cursor to dic
    Key = table descrition
    Value = row aurgment
    """
    dic_format = {}
    for idx, col in enumerate(cursor.description):
        dic_format[col[0]] = row[idx]
    return dic_format

class DataBase:
    """"
    DataBase Class: Takes a DatabaseName and Do Numerial Methods
        * get_table: Get Who Table Information
        * create_today_row: Create an Empty Row with a today Date
        * get_old_value: Get an old Value to use in in the coloring and consuimg Process
    """
    def __init__(self, db) -> None:
        self.db = db

    def select_table(self, table_name: str) -> dict:
        """
        Select Table using ARG: table_name
        """
        conn = sqlite3.connect(self.db)
        conn.row_factory = dict_factory
        cursor = conn.execute(f"SELECT * FROM {table_name}").fetchall()
        conn.close()
        return cursor
      
    async def insert_result(self, table: TableName, kwargs: dict) -> None:
        """
        Insert Result to a Table
        """
        db = await aiosqlite.connect(self.db)
        await db.execute(f"""INSERT INTO {table} {tuple(kwargs.keys())} VALUES {tuple(kwargs.values())}""")
        await db.commit()
        await db.close()
    
    def select_current_result(self, line: dict) -> None:
        """
        Query Select last result from SPEEDTEST and QUOTA TABLE for the Desired Line
        """
        conn = sqlite3.connect(self.db)
        conn.row_factory = dict_factory
        cursor = conn.execute(f"""SELECT 
            Ping, Download, Upload,Used, UsedPercentage, Remaining,
            Balance, Usage,RenewalDate, Hours, LineNumber, LineName,
            LineDescription, LineISP
            FROM SpeedTestResult
                INNER JOIN (SELECT *
                    FROM QuotaResult 
                    WHERE QuotaResult.Date  = '{today}' 
                    AND QuotaResult.LineID = {line['LineID']}
                    ORDER BY QuotaResult.ID DESC 
                    LIMIT(1)) AS QuotaResult		
                        ON QuotaResult.LineID = SpeedTestResult.LineID
                            INNER JOIN LinesData
                                ON LinesData.LineID = SpeedTestResult.LineID
                                WHERE SpeedTestResult.LineID = {line['LineID']}
                                AND SpeedTestResult.Date = '{today}'
                                ORDER BY SpeedTestResult.ID DESC LIMIT(1)""").fetchall()
        conn.close()
        return cursor[0]

           
    async def select_last_result(self, line:dict , target: str, table: str) -> str:
        """
        ASYNCIO Model Method, Select a Desired previous value for table in Specific Date
        """
        try:
            db = await aiosqlite.connect(self.db)
            cursor = await db.execute(f"""SELECT {target} FROM {table} WHERE LineID = {line['LineID']} ORDER BY ID DESC LIMIT(1)""")
            row = await cursor.fetchone()
            await cursor.close()
            await db.close()
            return row[0]
        except:
            return ''

SQLiteDB = DataBase("data.sqlite3")
MemoryDB = DataBase(":memory:")
if __name__ == "__main__":
    pass
