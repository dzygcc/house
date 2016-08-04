import sqlite3
import os


def create_lianjia(path):
    db = sqlite3.connect(path)
    cursor = db.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS lianjia
    ''')
    cursor.execute('''
        CREATE TABLE lianjia(id INTEGER PRIMARY KEY AUTOINCREMENT, city TEXT,
            district TEXT, total INTEGER, price FLOAT, date DATE)
    ''')
    cursor.execute('''
        CREATE INDEX "idx_lianjia" ON  lianjia(city, district, date);
    ''')
    db.commit()


def create_lianjia_stat(path):
    db = sqlite3.connect(path)
    cursor = db.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS lianjia_stat
    ''')
    cursor.execute('''
        CREATE TABLE lianjia_stat(id INTEGER PRIMARY KEY AUTOINCREMENT, city TEXT,
            vol INTEGER, price FLOAT, rate FLOAT, date DATE)
    ''')
    cursor.execute('''
        CREATE INDEX "idx_stat" ON lianjia_stat(city, date);
    ''')
    db.commit()

def create_hangzhou_tables(path):
    db = sqlite3.connect(path)
    cursor = db.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS house_project
    ''')
    cursor.execute('''
        CREATE TABLE house_project(id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT, city TEXT, developer TEXT, district TEXT,
                           total INTEGER, zhuzai INTEGER, total_area FLOAT, zhuzai_area FLOAT)
    ''')
    cursor.execute('''
        CREATE INDEX "idx_name" ON house_project (name);
    ''')
    cursor.execute('''
        DROP TABLE IF EXISTS project_sell_info
    ''')
    cursor.execute('''
        CREATE TABLE project_sell_info(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT,
                        project_id INTEGER, avg_price FLOAT, sold INTEGER, date DATE)
    ''')
    cursor.execute('''
        CREATE INDEX "idx_sell" ON project_sell_info (name, date);
    ''')
    cursor.execute('''
        DROP TABLE IF EXISTS project_open
    ''')
    cursor.execute('''
        CREATE TABLE project_open(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT,
                         open_id TEXT, district TEXT, total INTEGER, zhuzai INTEGER, date DATE)
    ''')
    cursor.execute('''
        CREATE INDEX "idx_open" ON project_open (open_id);
    ''')
    cursor.execute('''
        DROP TABLE IF EXISTS daily_vol
    ''')
    cursor.execute('''
        CREATE TABLE daily_vol(id INTEGER PRIMARY KEY AUTOINCREMENT, city TEXT,
            district TEXT, total INTEGER, zhuzai INTEGER, date DATE)
    ''')
    cursor.execute('''
        DROP TABLE IF EXISTS lianjia
    ''')
    cursor.execute('''
        CREATE TABLE lianjia(id INTEGER PRIMARY KEY AUTOINCREMENT, city TEXT,
            district TEXT, total INTEGER, price FLOAT, date DATE)
    ''')
    cursor.execute('''
        CREATE INDEX "idx_lianjia" ON  lianjia(city, district, date);
    ''')
    db.commit()


if __name__ == '__main__':
    file_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = ''.join([file_dir, "/../../db/house.db"])
    create_lianjia_stat(db_path)
