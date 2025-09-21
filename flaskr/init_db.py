import os
import psycopg2 
from psycopg2.extras import RealDictCursor
import click 
from flask import current_app ,g 
from datetime import datetime
def get_db_connection():
        conn = psycopg2.connect(
                host="localhost",
                database="zapay",
                user='naman',
                password='naman')
        return conn
conn = get_db_connection()
cur  = conn.cursor()
cur.execute('DROP TABLE IF EXISTS InventoryItem')
cur.execute('CREATE TABLE InventoryItem ('
                                 'Item_SKU VARCHAR(100) NOT NULL UNIQUE ,'
                                 'Item_Name varchar (150) NOT NULL UNIQUE,'
                                 'Item_Description varchar (500) NOT NULL,'
                                 'Item_Price integer NOT NULL CONSTRAINT positive_price   CHECK (Item_Price >  0 ),'
                                 'Item_Qty integer NOT NULL);'
			         )
cur.execute('CREATE TABLE Customer ('
                                 'c_ID  SERIAL PRIMARY KEY ,'

                                 'c_name varchar(100) NOT NULL,'
                                 'c_email varchar(100) NOT NULL,'
                                 'c_contact bigint NOT NULL UNIQUE);'
                                 )
cur.execute('CREATE TABLE Staff ('
                                 's_ID serial PRIMARY KEY,'
                                 's_name  varchar(100) ,'
                                 's_email varchar(100)  ,'
                                 's_isAdmin varchar(13) ,'
                                 's_contact varchar(10)  UNIQUE,'
                                 'pass varchar(199)  CHECK(LENGTH(pass) >= 8),'
                                 'mfa_secret VARCHAR(255));'
                                 )
cur.execute('CREATE TABLE Transaction ('
                                 't_ID bigserial PRIMARY KEY,'
                                 't_date bigint,'
                                 't_amount bigint,'
                                 't_category integer ,'
                                 'c_ID SERIAL UNIQUE ,'
                                 'FOREIGN KEY(c_ID) REFERENCES Customer(c_ID));'
                                 )
conn.commit()
cur.close()
conn.close()
