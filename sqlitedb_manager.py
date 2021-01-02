import sqlite3
from datetime import date
from settings import SQLITE_DB_NAME

# users (
# id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
# tg_id INTEGER NOT NULL UNIQUE,
# first_name TEXT,
# last_name TEXT,
# reg_date TEXT,
# balance REAL,
# token TEXT)

# netflix/ netflix_hd / disney (
# id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
# login TEXT,
# password TEXT,
# date TEXT,
# owner INTEGER)


def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(SQLITE_DB_NAME)
        return conn
    except Exception as e:
        print(e)
    return conn

def get_table_name(table_id):
    table_id = str(table_id)
    a = {'1': 'netflix', '2': 'netflix_hd', '3': 'disney'}
    return a[table_id]


def db_create(conn):
    try:
        cursor = conn.cursor()
        # cursor.execute("INSERT INTO netflix(id, login, password, date, owner) SELECT id, login, password, date, status FROM netflix_orig;")

        # cursor.execute("SELECT * FROM users")
        # print(cursor.fetchall())
        cursor.execute('SELECT * FROM netflix WHERE owner=1478376263')
        print(cursor.fetchone())
        # cursor.execute("DROP TABLE users")
        # cursor.execute("""CREATE TABLE IF NOT EXISTS disney (
        # id INTEGER PRIMARY KEY AUTOINCREMENT,
        # login TEXT,
        # password TEXT,
        # date TEXT,
        # owner INTEGER)""")
        cursor.close()
    except Exception as e:
        print(e)


def db_add_user(conn, tg_id, first_name, last_name,balance=0):
    token = 0
    reg_date = date.today().strftime("%d/%m/%Y")
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (tg_id, first_name, last_name, reg_date, balance, token) '
                       'VALUES (?,?,?,?,?,?)', (tg_id, first_name, last_name, reg_date, balance, token))
        conn.commit()
        # cursor.execute("SELECT * FROM users")
        # print(cursor.fetchall())
    except Exception as e:
        print(e)


def get_user(conn, tg_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE tg_id =" + str(tg_id))
        row = cursor.fetchone()
        print(row)
        if row:
            return row
        else:
            return None
    except Exception as e:
        print(e)


def update_user_token(conn, tg_id, token):
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET token=" + token + " WHERE tg_id =" + str(tg_id))
        conn.commit()
    except Exception as e:
        print(e)


def get_user_subs(conn,tg_id):
    result_subs = []
    table_names = ["netflix", "netflix_hd", "disney"]
    try:
        cursor = conn.cursor()
        for table_name in table_names:
            cursor.execute("SELECT * FROM " + table_name + " WHERE owner =" + str(tg_id))
            row = cursor.fetchall()
            print(row)
            if row:
                for i in range(len(row)):
                    result_subs.append({'sub_name': table_name.capitalize(), 'login': row[i][1], 'password': row[i][2]}) # 'date':row[i][3]
                return result_subs
            else:
                return None
    except Exception as e:
        print(e)


def credit_user_account(conn, user_tg_id, new_balance, token):
    # today_date = date.today().strftime("%d/%m/%Y")
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET token = 0, balance = ' + str(new_balance) + '  WHERE tg_id=' + str(user_tg_id))
        conn.commit()
    except Exception as e:
        print(e)


def get_stock_sub(conn, table_id):
    table_name = get_table_name(table_id)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ' + table_name + ' WHERE owner = 0')
        result = cursor.fetchone()
        if result:
            return result
        else:
            return False
    except Exception as e:
        print(e)
        return False


def pay_for_sub(conn, tg_id, price):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE tg_id=' + str(tg_id))
        result = list(cursor.fetchone())
        user_balance = result[5]
        new_balance = user_balance - price
        print(result, new_balance)
        if new_balance >= 0:
            cursor.execute('UPDATE users SET balance = ' + str(new_balance) + ' WHERE tg_id =' + str(tg_id))
            conn.commit()
            print('UPDATE users SET balance = ' + str(new_balance) + ' WHERE tg_id =' + str(tg_id))
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def give_sub(conn, table_id, sub, tg_id):
    table_name = get_table_name(table_id)
    today_date = date.today().strftime("%d/%m/%Y")
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE ' + table_name + ' SET date = ' + today_date + ', owner = ' + str(tg_id) +
                       ' WHERE id =' + str(sub[0]))
        # print('UPDATE users SET balance = ' + str(user_blance) + ' WHERE id =' + str(user_tg_id))
        conn.commit()
        return True
    except Exception as e:
        print(e)


def db_add_sub(conn, login, password, table_id, owner=0):
    table_name = get_table_name(table_id)
    today_date = date.today().strftime("%d/%m/%Y")
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO ' + table_name + '(login, password, date, owner) VALUES (?,?,?,?)',
                       (login, password, today_date, owner))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False


def db_select_subs(conn, table_id):
    table_name = get_table_name(table_id)
    # print(sub)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ' + table_name)
        sub_list = cursor.fetchall()
        return sub_list
    except Exception as e:
        print(e)
        return False


def db_delete_sub(conn, table_id, sub_id):
    if not sub_id.isdigit():
        return False
    table_name = get_table_name(table_id)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ' + table_name + ' WHERE id=' + str(sub_id))
        if not cursor.fetchone():
            return False
        cursor.execute('DELETE FROM ' + table_name + ' WHERE id=' + str(sub_id))
        # print(r)
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False




# conn = create_connection()
# print(db_create(conn))
# db_add_sub(conn,'newacc@gmail.com','12345678','1')
# db_add_sub(conn,'rigstat@gmail.com','12345678','1')
# db_add_sub(conn,'vadim@gmail.com','12345678','1')
# update_selled_sub(conn,1)
# db_delete_sub(conn,'1',9)
# def db_user_update(conn,data,user_id):
#     try:
#         cursor = conn.cursor()
#         sql = "UPDATE tasks SET user_id = ?, first_name = ?, last_name = ?, chat_id = ?,  WHERE id =? "
#         cursor.executemany()
#         conn.commit()
#         cursor.close()
#     except Exception as e:
#         print(e)
#
#     sql = ''' UPDATE tasks
#                 SET priority = ? ,
#                     begin_date = ? ,
#                     end_date = ?
#                 WHERE id = ?'''
#     cur = conn.cursor()
#     cur.execute(sql, task)
#     conn.commit()
