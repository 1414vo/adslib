import pymysql

''' Takes the columns of a table
    :param conn: A pymysql connection to a database
    :param table_name: The name of the table queried
    :return: A sequence of column names
'''
def get_table_columns(conn, table_name):
    cur = conn.cursor()
    cur.execute('SHOW COLUMNS FROM %s ORDER BY RAND()'%table_name)
    return cur.fetchall()

''' Fetches a random sample from the table
    :param conn: A pymysql connection to a database
    :param table_name: The name of the table queried
    :param limit: The amount of rows to be sampled
    :return: A sequence of rows
'''
def get_row_sample(conn, table_name, limit = 100):
    cur = conn.cursor()
    cur.execute('SELECT * FROM %s ORDER BY RAND() LIMIT %s'%(table_name, limit))
    return cur.fetchall()

''' Fetches a random sample from the table
    :param conn: A pymysql connection to a database
    :param area: The first characters of a postcode
    :param limit: The amount of rows to be sampled
    :return: A sequence of rows
'''
def get_postcode_data_for_area(conn, area, limit = 100):
    cur = conn.cursor()
    cur.execute('SELECT * FROM `postcode_data` WHERE postcode LIKE %(area)s ORDER BY RAND() LIMIT %(limit)s', \
        {'area': area + '%', 'limit': limit})
    return cur.fetchall()

''' Fetches a random sample from the table within a given postcode area
    :param conn: A pymysql connection to a database
    :param area: The first characters of a postcode
    :param limit: The amount of rows to be sampled
    :return: A sequence of rows
'''
def get_price_coord_data_for_area(conn, area, limit = 100):
    cur = conn.cursor()
    query = '''SELECT * FROM 
            (SELECT price, date_of_transfer, postcode, property_type, new_build_flag, tenure_type, locality, town_city, district, county  FROM `pp_data`
            WHERE postcode LIKE %(area)s) pp
            INNER JOIN 
            (SELECT postcode, country, lattitude, longitude FROM `postcode_data`
            WHERE postcode LIKE %(area)s) pc
            ON pp.postcode = pc.postcode 
            ORDER BY RAND()
            LIMIT %(limit)s'''
    cur.execute(query, {'area': area + '%', 'limit': limit})
    return cur.fetchall()

''' Fetches a random sample from the table in a given year range
    :param conn: A pymysql connection to a database
    :param start_year: The first possible year for the query
    :param end_year: The last possible year for the query
    :param limit: The amount of rows to be sampled
    :return: A sequence of rows
'''
def get_price_coord_data_between_years(conn, start_year = 1995, end_year = 2022, limit = 100):
    cur = conn.cursor()
    query = '''SELECT * FROM 
            (SELECT price, date_of_transfer, postcode, property_type, new_build_flag, tenure_type, locality, town_city, district, county FROM `pp_data`
            WHERE date_of_transfer BETWEEN %(start_date)s AND %(end_date)s) pp
            INNER JOIN 
            (SELECT postcode, country, lattitude, longitude FROM `postcode_data`) pc
            ON pp.postcode = pc.postcode
            ORDER BY RAND()
            LIMIT %(limit)s''' 
    cur.execute(query, {'start_date': str(start_year) + '/1/1', 'end_date': str(end_year) + '/12/31', 'limit': limit})
    return cur.fetchall()

''' Fetches a random sample from the table in a given year range inside a postcode area
    :param conn: A pymysql connection to a database
    :param area: The first characters of a postcode
    :param start_year: The first possible year for the query
    :param end_year: The last possible year for the query
    :param limit: The amount of rows to be sampled
    :return: A sequence of rows
'''
def get_price_coord_data_between_years_for_area(conn, area, start_year = 1995, end_year = 2022, limit = 100):
    cur = conn.cursor()
    query = '''SELECT * FROM 
            (SELECT price, date_of_transfer, postcode, property_type, new_build_flag, tenure_type, locality, town_city, district, county 
            FROM `pp_data`
            WHERE postcode LIKE %(area)s AND
            date_of_transfer BETWEEN %(start_date)s AND %(end_date)s) pp
            INNER JOIN 
            (SELECT postcode, country, lattitude, longitude 
            FROM `postcode_data`
            WHERE postcode LIKE %(area)s) pc
            ON pp.postcode = pc.postcode
            ORDER BY RAND()
            LIMIT %(limit)s'''
    cur.execute(query, {'area': area + '%', 'start_date': str(start_year) + '/1/1', 'end_date': str(end_year) + '/12/31', 'limit': limit})
    return cur.fetchall()

''' Fetches a random sample from the table in a given year range inside a coordinate box
    :param conn: A pymysql connection to a database
    :param north: The north edge of the box
    :param east: The east edge of the box
    :param south: The south edge of the box
    :param west: The west edge of the box
    :param start_year: The first possible year for the query
    :param end_year: The last possible year for the query
    :param limit: The amount of rows to be sampled
    :return: A sequence of rows
'''
def get_price_coord_data_between_years_for_coordinate_area(conn, north, east, south, west, start_year = 1995, end_year = 2022, limit = 100):
    cur = conn.cursor()
    query = '''SELECT * FROM 
            (SELECT price, date_of_transfer, postcode, property_type, new_build_flag, tenure_type, locality, town_city, district, county 
            FROM `pp_data`
            WHERE date_of_transfer BETWEEN %(start_date)s AND %(end_date)s) pp
            INNER JOIN 
            (SELECT postcode, country, lattitude, longitude 
            FROM `postcode_data`
            WHERE lattitude BETWEEN %(south)s AND %(north)s
            AND longitude BETWEEN %(west)s AND %(east)s) pc
            ON pp.postcode = pc.postcode
            ORDER BY RAND()
            LIMIT %(limit)s'''
    cur.execute(query, {'north': north, 'south': south, 'west': west, 'east': east, 'start_date': str(start_year) + '/1/1', 'end_date': str(end_year) + '/12/31', 'limit': limit})
    return cur.fetchall()
