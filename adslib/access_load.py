import pymysql

def get_table_columns(conn, table_name):
    cur = conn.cursor()
    cur.execute('SHOW COLUMNS FROM %s ORDER BY RAND()'%table_name)
    return cur.fetchall()

def get_row_sample(conn, table_name, limit = 100):
    cur = conn.cursor()
    cur.execute('SELECT * FROM %s ORDER BY RAND() LIMIT %s'%(table_name, limit))
    return cur.fetchall()

def get_postcode_data_for_area(conn, area, limit = 100):
    cur = conn.cursor()
    cur.execute('SELECT * FROM `postcode_data` WHERE postcode LIKE %(area)s ORDER BY RAND() LIMIT %(limit)s', \
        {'area': area + '%', 'limit': limit})
    return cur.fetchall()

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

def get_price_coord_data_between_years_for_coordinate_area(conn, north, east, south, west, start_year = 1995, end_year = 2022, limit = 100):
    cur = conn.cursor()
    query = '''SELECT * FROM 
            (SELECT price, date_of_transfer, postcode, property_type, new_build_flag, tenure_type, locality, town_city, district, county 
            FROM `pp_data`
            WHERE date_of_transfer BETWEEN %(start_date)s AND %(end_date)s) pp
            INNER JOIN 
            (SELECT postcode, country, lattitude, longitude 
            FROM `postcode_data`
            WHERE lattitude BETWEEN south AND north
            AND longitude BETWEEN west AND east) pc
            ON pp.postcode = pc.postcode
            ORDER BY RAND()
            LIMIT %(limit)s'''
    cur.execute(query, {'area': area + '%', 'start_date': str(start_year) + '/1/1', 'end_date': str(end_year) + '/12/31', 'limit': limit})
    return cur.fetchall()

def do_one_hot_encoding(df, feature):
    for feature_type in df[feature].unique():
        encoding_name = 'is_' + str(feature) + '_' + str(feature_type)
        df[encoding_name] = np.where(df[feature] == feature_type, 1, 0)
    return df
