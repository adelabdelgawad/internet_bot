import sqlite3
import aiosqlite
import asyncio
from datetime import timedelta
from datetime import datetime
"""
The DataBase Manipulation Module
Uses SQLite Standard Module
and AIOSQLITE ASYNCIO Model Modules
"""
today = datetime.strftime(datetime.now() - timedelta(0), '%d-%m-%Y')
yesterday = datetime.strftime(datetime.now() - timedelta(1), '%d-%m-%Y')
time = datetime.now().strftime('%H:%M')
date = f"{today} | {time}"

def dict_factory(cursor: str, row: int) -> dict:
    """
    Convert cursor to dic
    Key = table descrition
    Value = row aurgment
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DataBase:
    """"
    DataBase Class: Takes a DatabaseName and Do Numerial Methods
        * get_table: Get Who Table Information
        * create_today_row: Create an Empty Row with a today Date
        * get_old_value: Get an old Value to use in in the coloring and consuimg Process
    """
    def __init__(self, db) -> None:
        self.db = db
        self._sqlite = sqlite3.connect(db)
        self._aiosqlite = aiosqlite.connect(db)

    def get_table(self, table_name: str) -> dict:
        """
        :prameter:
            table_name: str -> Table Rows in a dictioneries format
            column description = column value
        """
        with self._sqlite as conn:
            conn.row_factory = dict_factory
            return conn.execute(f"SELECT * FROM {table_name}").fetchall()

    async def fetch_yesterday_result(self, line: dict, value: str) -> dict:
        """
        Asycio Method to Fetch Table as Dict
         Key: column description
        Value: column value
        """
        try:
            db = await aiosqlite.connect(self.db)
            db.row_factory = dict_factory
            cursor = await db.execute(
                f"""SELECT {value} FROM results where line_name = '{line['line_name']}' and date= '{today}' 
                LAG {value} OVER (PARTITION BY {line['line_name']} ORDER BY id) AS previous_value
                ORDER id
                """)
            result = await cursor.fetchone()
            print(f"p: {result}")
            await db.close()
            return result[0]
        except Exception as ex:
            print(ex)

    def create_today_row(self, line: dict) -> None:
        """
        Search for today line row
        Delete it if found
        Create today empty row
        """
        with self._sqlite as conn:
            conn.execute(f"""INSERT INTO results ('line_id', 'line_name', 'isp', 'line_using', 'line_number', 'date', 'time') 
            VALUES
            ('{line['line_id']}', '{line['line_name']}', '{line['isp']}', '{line['line_using']}',  {line['line_number']}, '{today}', '{date}')""")


    async def get_old_value(self, line: dict, target: str) -> str:
        """
        ASYNCIO Model Method, Retreive a Specefic value for the results table
        :prameters:
            Line: dict -> a Dict value to get the Line Name
            Target: str -> The Desired Value Argument
        """
        day = datetime.strftime(datetime.now() - timedelta(1), '%d-%m-%Y')
        try:
            db = await aiosqlite.connect(self.db)
            cursor = await db.execute(f"""SELECT {target} FROM results WHERE line_name='{line['line_name']}' AND date='{day}' ORDER BY id DESC""")
            result = await cursor.fetchone()
            await db.close()
            return result[0]
        except:
            return ''
        

    async def add_result_to_today_line_row(self, line: str, result: str) -> None:
        """
        ASYNCIO Model Method, Update a Specefic value in the results table
        :prameters:
            Line: dict -> a Dict value to get the Line Name
            result: str -> The Desired Result to Update
        """
        async with aiosqlite.connect(self.db) as db:
            await db.execute(
                f"""Update results SET {result} WHERE line_name='{line['line_name']}' and date = '{today}'
                and id = (SELECT MAX(id) from results WHERE line_name='{line['line_name']}'
            )""")
            await db.commit()
            await asyncio.sleep(.1)

    def get_today_results(self, lines: dict) -> None:
        """
        Get lines rows in a dictioneries format
        {'line_id': x, 'line_name': y}
        and return a list of the values
        """
        with self._sqlite as conn:
            conn.row_factory = dict_factory
            return [ conn.execute(f"SELECT * FROM results where line_name = '{line['line_name']}' and date= '{today}'").fetchone() for line in lines ]

    async def get_today_row_result(self, line: dict, target: str):
        """
        ASYNCIO Model Method, Retreive today value for the result row
        :prameters:
            Line: dict -> a Dict value to get the Line Name
            Target: str -> The Desired Value Argument
        """
        async with aiosqlite.connect(self.db) as db:
            try:
                db.row_factory = aiosqlite.Row
                async with db.execute(f"""SELECT {target} FROM results WHERE line_name='{line['line_name']}' AND date='{today}'""") as cursor:
                    async for row in cursor:
                        return row[f'{target}']
            except:
                return ''


SQLiteDB = DataBase("data.sqlite3")
MemoryDB = DataBase(":memory:")
if __name__ == "__main__":
    pass
