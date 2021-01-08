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
# token TEXT,
# username TEXT)

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


def decode_db_table_name(table_id):
    table_id = str(table_id)
    data = {'1': 'netflix', '2': 'netflix_hd', '3': 'disney', '4':'nord_vpn'}
    return data[table_id]


def decode_qiwi_column_name(param_id):
    param_id = str(param_id)
    data = {'1': 'qiwi_account', '2': 'qiwi_token'}
    return data[param_id]


def create_sales_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS sale_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        tg_id INTEGER,
        first_name TEXT,
        last_name TEXT,
        username TEXT,
        date TEXT,
        service_id INTEGER)""")
        cursor.close()
    except Exception as e:
        print(e)


def create_credit_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS credit_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        tg_id INTEGER,
        first_name TEXT,
        last_name TEXT,
        username TEXT,
        date TEXT,
        sum REAL)""")
        cursor.close()
    except Exception as e:
        print(e)


def create_sub_table(conn, table_id):
    table_name = decode_db_table_name(table_id)
    try:
        cursor = conn.cursor()
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        login TEXT,
        password TEXT,
        date TEXT,
        owner INTEGER)""")
        cursor.close()
    except Exception as e:
        print(e)


def create_user_params(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS user_params (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        tg_id INTEGER,
        promo TEXT,
        affiliate TEXT,
        subscription INTEGER)""")
        cursor.close()
    except Exception as e:
        print(e)


def create_qiwi_table(conn):
    try:
        cursor = conn.cursor()
        r = cursor.execute("""CREATE TABLE IF NOT EXISTS qiwi_params (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        qiwi_account TEXT,qiwi_token TEXT)""")
        cursor.close()
    except Exception as e:
        print(e)


def create_user_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS 
        users (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        tg_id INTEGER NOT NULL UNIQUE,
        first_name TEXT,
        last_name TEXT,
        reg_date TEXT,
        balance REAL,
        token TEXT,
        username TEXT,
        subscription INTEGER,
        promo TEXT)""")
        cursor.close()
    except Exception as e:
        print(e)


def add_user(conn, tg_id, first_name, last_name, username, balance=0):
    token = 0
    balance = 0.0
    reg_date = date.today().strftime("%d/%m/%Y")
    try:
        cursor = conn.cursor()
        existence = get_user(conn, tg_id)
        if not existence:
            cursor.execute('INSERT INTO users (tg_id, first_name, last_name, reg_date, balance, token, username) '
                           'VALUES (?,?,?,?,?,?,?)', (tg_id, first_name, last_name, reg_date, balance, token, username))
            conn.commit()
        else:
            return False
    except Exception as e:
        print(e)


def update_user_subscription(conn, tg_id, subscription):
    try:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET subscription={subscription} WHERE tg_id =" + str(tg_id))
        conn.commit()
    except Exception as e:
        print(e)


def check_user_subscription(conn, tg_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT subscription FROM users WHERE tg_id =" + str(tg_id))
        subscription = cursor.fetchone()
        if subscription:
            return subscription
        else:
            return 0
    except Exception as e:
        print(e)
        return 0


def get_user(conn, tg_id):
    print(tg_id)
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


def get_all_users(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        row = cursor.fetchall()
        if row:
            return row
        else:
            return None
    except Exception as e:
        print(e)


def update_user_token(conn, tg_id, token):
    try:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET token={token} WHERE tg_id =" + str(tg_id))
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
            print(table_name, row)
            if row:
                for i in range(len(row)):
                    result_subs.append({'sub_name': table_name.capitalize(), 'login': row[i][1], 'password': row[i][2]}) # 'date':row[i][3]
                # result_subs.append(row)
        return result_subs
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


def get_free_sub(conn, table_id):
    table_name = decode_db_table_name(table_id)
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
        print(f'result, selected user: {result}')
        user_balance = result[5]
        new_balance = user_balance - price
        print('new_balance_afrer_add_money: ', new_balance)
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


def give_sub_to_user(conn, table_id, sub, tg_id):
    table_name = decode_db_table_name(table_id)
    today_date = date.today().strftime("%d/%m/%Y")
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE ' + table_name + ' SET date = ' + today_date + ', owner = ' + str(tg_id) +
                       ' WHERE id =' + str(sub[0]))
        conn.commit()
        return True
    except Exception as e:
        print(e)


def add_service_sub(conn, login, password, table_id, owner=0):
    table_name = decode_db_table_name(table_id)
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


def select_subs(conn, table_id):
    table_name = decode_db_table_name(table_id)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ' + table_name)
        sub_list = cursor.fetchall()
        return sub_list
    except Exception as e:
        print(e)
        return False


def delete_db_sub(conn, table_id, sub_id):
    table_name = decode_db_table_name(table_id)
    try:
        cursor = conn.cursor()
        # cursor.execute('SELECT * FROM ' + table_name + ' WHERE id=' + str(sub_id))
        # if not cursor.fetchone():
        #     return False
        cursor.execute('DELETE FROM ' + table_name + ' WHERE id=' + str(sub_id))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False


def delete_user(conn, tg_id):
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE tg_id=' + str(tg_id))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False

#
# def update_qiwi_params(conn, param_id, param_value):
#     try:
#         column = decode_qiwi_column_name(param_id)
#         cursor = conn.cursor()
#         print(column, param_value)
#         print('UPDATE qiwi_params SET ' + column + '=' + param_value + ' WHERE id=1')
#         cursor.execute('UPDATE "qiwi_params" SET ' + column + '=' + param_value + ' WHERE id=1')
#         conn.commit()
#         return True
#     except Exception as e:
#         print(e)
#         return False


def get_qiwi_params(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM qiwi_params')
        qiwi_params = list(cursor.fetchone())
        if qiwi_params[1][0] != '+':
            qiwi_acc = qiwi_params[1]
            correct_qiwi_acc = qiwi_acc[:0] + '+' + qiwi_acc[0:]
            qiwi_params[1] = correct_qiwi_acc
        return qiwi_params
    except Exception as e:
        print(e)
        return False


def log_credit_transaction(conn, tg_id, first_name, last_name, username, sum):
    today_date = date.today().strftime("%d/%m/%Y")
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO credit_transactions (tg_id, first_name, last_name, username, date, sum) '
                       'VALUES (?,?,?,?,?,?)',
                       (tg_id, first_name, last_name, username, today_date, sum))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False


def get_credit_transaction_by_date(conn, curr_date):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM credit_transactions ')
        credit_list = cursor.fetchall()
        result_list = []
        if credit_list:
            for i in credit_list:
                if i[5] == curr_date:
                    result_list.append(i)
            return result_list
        else:
            return None

    except Exception as e:
        print(e)
        return False


def log_sale_transaction(conn, tg_id, first_name, last_name, username, service_id):
    today_date = date.today().strftime("%d/%m/%Y")
    try:
        print(tg_id, first_name, last_name, username, service_id)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO sale_transactions (tg_id, first_name, last_name, username, date, service_id) '
                       'VALUES (?,?,?,?,?,?)',
                       (tg_id, first_name, last_name, username, today_date, service_id))
        print('ADDed')
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False


def get_sale_log_by_date(conn, curr_date):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sale_transactions')
        sale_list = cursor.fetchall()
        result_list = []
        if sale_list:
            for i in sale_list:
                if i[5] == curr_date:
                    result_list.append(i)
            return result_list
        else:
            return None
    except Exception as e:
        print(e)
        return False


def get_user_by_date(conn, curr_date):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE reg_date=?", (curr_date,))
        user_list = cursor.fetchall()
        if user_list:
            return user_list
        else:
            return None
    except Exception as e:
        print(e)

# def update_user_subscription(conn, user_tg_id):
#     try:
#         cursor = conn.cursor()
#         cursor.execute('SELECT subscription FROM user_params WHERE tg_id='+str(user_tg_id))
#         if not cursor.fetchone():
#             cursor.execute('INSERT INTO user_params (tg_id, subscription) VALUES (?,?)',(user_tg_id, 0))
#             return False
#         cursor.execute('UPDATE ' + table_name + ' SET date = ' + today_date + ', owner = ' + str(tg_id) +
#                        ' WHERE id =' + str(sub[0]))
#         conn.commit()
#         return True
#     except Exception as e:
#         print(e)
