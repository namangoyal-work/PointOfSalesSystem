import os
import psycopg2
from datetime import datetime
from flask import Flask  , session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from .auth import auth
from flask import     redirect,url_for  , render_template , request , jsonify   ,flash  , Blueprint

app = Flask(__name__)
app.register_blueprint(auth , url_prefix='')
app.secret_key = 'naman'
app.config['JWT_SECRET_KEY'] = 'naman'

def get_db_connection():
        conn = psycopg2.connect(
                host="localhost",
                database="zapay",
                user='naman',
                password='naman')

        return conn
    
@app.route('/inventory'   ,  methods=["POST"  ,  "GET" , "PUT" , "DELETE"  ,"PATCH"])

def Inventory():
 
    conn = get_db_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM InventoryItem")
    Inventorydata  = cur.fetchall()
    cur.close()
    conn.close()

    
   


    return render_template("inventory/inventory.html" , Inventory=Inventorydata)



@app.route('/add_item'  , methods=['POST'])
def add_item():
    conn = get_db_connection()
    cur = conn.cursor()
    sku  = request.form["sku"]
    item_name = request.form['item_name']
    description = request.form['description']
    price = float(request.form['price'])
    quantity  = int(request.form['quantity'])
    
  
    cur.execute('INSERT INTO InventoryItem (Item_SKU, Item_Name, Item_Description, Item_Price , Item_Qty)'
        'VALUES (%s, %s, %s, %s  , %s  )',
        (f'{sku}',
        f'{item_name}',
        f'{description} ',
        price,
        quantity)
            )
    conn.commit()
    cur.close()
    conn.close()
    flash('Item Added Successfully' , 'info')
    return redirect(url_for('Inventory'))
@app.route('/delete_item' , methods=['POST'])
def delete_item():
    conn = get_db_connection()
    cur = conn.cursor()
    name = request.form['name']

    cur.execute('DELETE FROM InventoryItem WHERE item_name=%s',(name,))
    conn.commit()
    cur.close()
    conn.close()

    flash(f"{name} deleted Successfully" , 'info')
    return redirect(url_for('Inventory'))
@app.route('/edit_item', methods=['POST' , 'GET' , "PUT"  , "DELETE"])
def edit_item():
    conn = get_db_connection()
    cur = conn.cursor()
    sku  = request.form['sku']
    item_name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    quantity  = int(request.form['quantity'])

    cur.execute("""
        UPDATE InventoryItem
        SET Item_SKU= %s Item_Description = %s, Item_Price = %s, Item_Qty = %s
        WHERE Item_Name = %s
    """, ( sku,description, price, quantity , item_name))
    conn.commit()
    cur.close()
    conn.close()
    flash("edit Successful" , 'info')
    return redirect(url_for('Inventory'))