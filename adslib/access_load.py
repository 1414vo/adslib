import pymysql

def get_row_sample(conn, table_name, limit = 100):
    cur = conn.cursor()
    cur.execute('SELECT * FROM %s LIMIT %s' % (table_name, limit))
    return cur.fetchall()

def get_postcode_data_for_area(conn, area):
    cur = conn.cursor()
    cur.execute('SELECT * FROM `postcode_data` WHERE postcode LIKE "%s%"' % area)
    return cur.fetchall()

def get_price_coord_data_for_area(conn, area):
    cur = conn.cursor()
    query = '''SELECT * FROM 
            (SELECT price, date_of_transfer, postcode, property_type, new_build_flage, tenure_type FROM `pp_data`
            WHERE postcode LIKE "%s%") pp
            INNER JOIN 
            (SELECT postcode, locality, town_city, district, county, country, latitude, longitude FROM `property_prices`
            WHERE postcode LIKE "%s%") pc
            ON pp.postcode = pc.postcode''' % (area, area)
    cur.execute(query)
    return cur.fetchall()

def get_price_coord_data_between_years(conn, start_year = 1995, end_year = 2022):
    cur = conn.cursor()
    query = '''SELECT * FROM 
            (SELECT price, date_of_transfer, postcode, property_type, new_build_flage, tenure_type FROM `pp_data`
            WHERE date_of_transfer BETWEEN YEAR %s AND YEAR %s) pp
            INNER JOIN 
            (SELECT postcode, locality, town_city, district, county, country, latitude, longitude FROM `property_prices`) pc
            ON pp.postcode = pc.postcode''' % (start_year, end_year)
    cur.execute(query)
    return cur.fetchall()

def get_price_coord_data_between_years_for_area(conn, area, start_year = 1995, end_year = 2022):
    cur = conn.cursor()
    query = '''SELECT * FROM 
            (SELECT price, date_of_transfer, postcode, property_type, new_build_flage, tenure_type 
            FROM `pp_data`
            WHERE postcode LIKE "%s%" AND
            date_of_transfer BETWEEN YEAR %s AND YEAR %s) pp
            INNER JOIN 
            (SELECT postcode, locality, town_city, district, county, country, latitude, longitude 
            FROM `property_prices`
            WHERE postcode LIKE "%s%") pc
            ON pp.postcode = pc.postcode''' % (area, start_year, end_year, area)
    cur.execute(query)
    return cur.fetchall()
