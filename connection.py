import sqlite3
import aiosqlite
from datetime import timedelta
from datetime import datetime


today = datetime.strftime(datetime.now() - timedelta(0), '%d-%m-%Y')

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

    def get_table_as_dict(self, table_name):
        """
        Get lines rows in a dictioneries format
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
        conn = sqlite3.connect(self.db)
        conn.execute(f"""INSERT INTO results ('line_id', 'line_name', 'isp', 'line_using', 'line_number', 'date', 'upload', 'download') 
        VALUES
        ('{line['line_id']}', '{line['line_name']}', '{line['isp']}', '{line['line_using']}',  {line['line_number']}, '{today}', '0', '0')""")
        conn.commit()
        conn.close()
    
    async def async_create_today_row(self, lines):
        db = await aiosqlite.connect(self.db)
        for line in lines:
            
        try:
            cursor = await db.execute(
                f"""SELECT * FROM results WHERE line_name = '{line_name}' where date = '{today}'""")
            row = await cursor.fetchone()
            await cursor.close()
            await db.close()
            return (row[0])
        except:
            pass


    def get_row_id(self, line_name):
        conn = sqlite3.connect(self.db)
        curs = conn.cursor()
        try:
            res = curs.execute(f"""SELECT * FROM results WHERE line_name = '{line_name}' ORDER BY ID DESC LIMIT 11""")
            res = res.fetchone()
            conn.commit()
            conn.close()
            return (res[0])
        except:
            conn.close()
            return

    async def async_get_row_id(self, line_name):
        db = await aiosqlite.connect(self.db)
        try:
            cursor = await db.execute(
                f"""SELECT * FROM results WHERE line_name = '{line_name}' where date = '{today}'""")
            row = await cursor.fetchone()
            await cursor.close()
            await db.close()
            return (row[0])
        except:
            pass

    # Retreive Old data from table by day
    async def get_old_value(self, line, target, days):
        day = datetime.strftime(datetime.now() - timedelta(days), '%d-%m-%Y')
        db = await aiosqlite.connect(self.db)
        try:
            cursor = await db.execute(
                f"""SELECT {target} FROM results WHERE line_name="{line['line_name']}" AND date='{day}' ORDER BY id ASC LIMIT 1""")
            row = await cursor.fetchone()
            await cursor.close()
            await db.close()
            return (row[0])
        except:
            pass

    # add process results to row
    async def add_results_to_today_row(self, row_id, result):
        db = await aiosqlite.connect(self.db)
        try:
            await db.execute(
                f"""Update results SET {result} WHERE id='{row_id}'"""
                )
            await db.commit()
            await db.close()
        except Exception as ex:
            print(ex)
    
    def get_last_result_dict(self, lines):
        """
        Get lines rows in a dictioneries format
        {'line_id': x, 'line_name': y}
        """
        conn = sqlite3.connect(self.db)

        with conn:
            conn.row_factory = dict_factory
            rows: list = [] 
            for line in lines:
                curs = conn.cursor()
                curs.execute(f"SELECT * FROM results where line_name = '{line['line_name']}' and date= '{today}' ORDER BY id Desc")
                row = curs.fetchone()
                rows.append(row)
            return rows

    def get_today_results(self, line_name= None):
        db = sqlite3.connect(self.db)
        try:
            db.row_factory = dict_factory
            if line_name:
                cursor = db.execute(
                    f"""SELECT * FROM results
                    WHERE line_name={line_name}
                    and date = '{today}'
                    ORDER BY id ASC"""
                    )
            else:
                cursor = db.execute(
                    f"""SELECT * FROM results WHERE date = '{today}'"""
                    )
            rows = cursor.fetchall()
            cursor.close()
            db.close()
            print(rows)
            return (rows)
        except Exception as ex:
            print(ex)
            
    def get_table(self, table_name):
        conn = sqlite3.connect(self.db)
        res = conn.execute(f"""SELECT * FROM {table_name}""")
        res = res.fetchall()
        conn.commit()
        conn.close()
        return (res)
 

    
if __name__ == "__main__":
    pass
