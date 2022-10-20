import sqlite3
import aiosqlite
from datetime import timedelta
from datetime import datetime


today = datetime.strftime(datetime.now() - timedelta(0), '%d-%m-%Y')
time = datetime.now().strftime('%H:%M')

def dict_factory(cursor, row):
    """
    Convert result to dic
    Key = table descrition
    Value = the returned value it self
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DataBase:
    def __init__(self, db):
        self.db = db
        self.conn = sqlite3.connect(self.db)

    def get_table(self, table_name):
        """
        Get table rows in a dictioneries format
        {'line_id': x, 'line_name': y}
        """
        conn = sqlite3.connect(self.db)

        with conn:
            conn.row_factory = dict_factory
            curs = conn.cursor()
            curs.execute(f"SELECT * FROM {table_name}")
            rows = curs.fetchall()
            return rows

    # Create Line Result
    def create_today_row(self, line):
        """Create empty row  for argumnet line and make sure no duplicate rows is exists"""
        conn = sqlite3.connect(self.db)
        # validating the row existing
        curs = conn.execute(
                f"""SELECT * FROM results WHERE line_name = '{line['line_name']}' and date = '{today}'""")
        rows = curs.fetchall()     
        if rows:
            for row in rows:
                conn.execute(f"DELETE from results where id={row[0]}")
                conn.commit()
        conn.execute(f"""INSERT INTO results ('line_id', 'line_name', 'isp', 'line_using', 'line_number', 'date', 'time', 'upload', 'download') 
        VALUES
        ('{line['line_id']}', '{line['line_name']}', '{line['isp']}', '{line['line_using']}',  {line['line_number']}, '{today}', '{time}', '0', '0')""")
        conn.commit()
        conn.close()

    # Retreive Old data from table by day
    async def get_old_value(self, line, target, days):
        day = datetime.strftime(datetime.now() - timedelta(days), '%d-%m-%Y')
        print(line)
        db = await aiosqlite.connect(self.db)
        try:
            cursor = await db.execute(
                f"""SELECT {target} FROM results WHERE line_id="{line['line_id']}" AND date='{day}' ORDER BY id ASC LIMIT 1""")
            row = await cursor.fetchone()
            await cursor.close()
            await db.close()
            return (row[0])
        except Exception as ex:
            print

    # add process results to row
    async def add_result_to_today_line_row(self, line, result):
        db = await aiosqlite.connect(self.db)
        try:
            await db.execute(
                f"""Update results SET {result} WHERE line_name='{line['line_name']}' and date = '{today}'"""
                )
            await db.commit()
            await db.close()
        except Exception as ex:
            print(ex)
    
    def get_today_results(self, lines):
        """
        Get lines rows in a dictioneries format
        {'line_id': x, 'line_name': y}
        and return a list of the values
        """
        conn = sqlite3.connect(self.db)
        with conn:
            conn.row_factory = dict_factory
            rows: list = [] 
            for line in lines:
                curs = conn.cursor()
                curs.execute(f"SELECT * FROM results where line_name = '{line['line_name']}' and date= '{today}'")
                row = curs.fetchone()
                rows.append(row)
            return rows
 

    
if __name__ == "__main__":
    pass
