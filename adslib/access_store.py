import pymysql
import pandas as pd

def create_connection(user, password, host, database, port=3306):
    """ Create a database connection to the MariaDB database
        specified by the host url and database name.
    :param user: username
    :param password: password
    :param host: host url
    :param database: database
    :param port: port number
    :return: Connection object or None
    """
    conn = None
    try:
        conn = pymysql.connect(user=user,
                               passwd=password,
                               host=host,
                               port=port,
                               local_infile=1,
                               db=database
                               )
    except Exception as e:
        print(f"Error connecting to the MariaDB Server: {e}")
    return conn

def save_local_data_in_table(conn, table_name, file_location, reset = True):
    if reset:
        cur = conn.cursor()
        cur.execute('DELETE FROM ' + table_name)
        conn.commit()
        print("Deleted table entries")
        cur.close()

    cur = conn.cursor()
    data_to_insert = pd.read_csv(file_location).fillna('').replace('\\N', '0')

    list_of_rows = list(data_to_insert.to_records(index=False))
    list_of_rows = [tuple(i) for i in list_of_rows]

    cur = conn.cursor()
    cur.execute('SHOW COLUMNS FROM ' + table_name) 
    cols = cur.fetchall()
    column_list = list(zip(*cols))[0][:-1]
    number_of_columns = len(column_list)
    template = '%s, ' * (number_of_columns - 1) + '%s'
    query = 'INSERT INTO ' + table_name + ' ' + str(column_list).replace("'", '') + ' VALUES (' + template + ')'
    cur.executemany(query, list_of_rows)
    print("Inserted %s lines in %s", (len(list_of_rows), table_name))
    conn.commit()

