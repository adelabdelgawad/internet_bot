import sqlite3
import aiosqlite
import asyncio
from datetime import timedelta
from datetime import datetime


today = datetime.strftime(datetime.now() - timedelta(0), '%d-%m-%Y')
time = datetime.now().strftime('%H:%M')

def dict_factory(cursor, row):
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
    def __init__(self, db):
        self._sqlite = sqlite3.connect(db)
        self._aiosqlite = aiosqlite.connect(db)

    def get_table(self, table_name):
        """
        Get table rows in a dictioneries format
        column descroption = column value
        """
        with self._sqlite as conn:
            conn.row_factory = dict_factory
            return conn.execute(f"SELECT * FROM {table_name}").fetchall()

    # Create Line Result
    def create_today_row(self, line):
        """
        Search for today line row
        Delete it if found
        Create today empty row
        """
        with self._sqlite as conn:  # validating the row existing
            rows = conn.execute(
                f"""SELECT * FROM results WHERE line_name = '{line['line_name']}' and date = '{today}'""").fetchall()
            if rows:
                for row in rows:
                    conn.execute(f"DELETE from results where id={row['id']}")
            conn.execute(f"""INSERT INTO results ('line_id', 'line_name', 'isp', 'line_using', 'line_number', 'date', 'time', 'upload', 'download') 
            VALUES
            ('{line['line_id']}', '{line['line_name']}', '{line['isp']}', '{line['line_using']}',  {line['line_number']}, '{today}', '{time}', '0', '0')""")

    # Retreive Old data from table by day
    async def get_old_value(self, line, target):
        async with self._aiosqlite as db:
            day = datetime.strftime(datetime.now() - timedelta(1), '%d-%m-%Y')
            db.row_factory = aiosqlite.Row
            async with db.execute(f"""SELECT {target} FROM results WHERE line_name='{line}' AND date='{day}' ORDER BY id ASC LIMIT 1""") as cursor:
                async for row in cursor:
                    return row[target]
            
    # add process results to row
    async def add_result_to_today_line_row(self, line, result):
        async with self._aiosqlite as db:
            await db.execute(f"""Update results SET {result} WHERE line_name='{line['line_name']}' and date = '{today}'""")

    def get_today_results(self, lines):
        """
        Get lines rows in a dictioneries format
        {'line_id': x, 'line_name': y}
        and return a list of the values
        """
        with self._sqlite as conn:
            conn.row_factory = dict_factory
            return [ conn.execute(f"SELECT * FROM results where line_name = '{line['line_name']}' and date= '{today}'").fetchone() for line in lines ]

if __name__ == "__main__":
    pass
