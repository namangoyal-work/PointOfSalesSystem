from flask import Flask  , abort , Blueprint  ,redirect ,render_template   , url_for , jsonify , flash ,session , request
from datetime import timedelta 
import psycopg2
import pyotp
from twilio.rest import Client
from flask_bcrypt import Bcrypt

from werkzeug.security import generate_password_hash , check_password_hash

from functools import wraps
def get_db_connection():
        conn = psycopg2.connect(
                host="localhost",
                database="zapay",
                user='naman',
                password='naman')
        return conn
auth = Blueprint('auth',__name__,static_folder='static' , template_folder='templates/auth')
auth.permanent_session_lifetime = timedelta(days=10)
def enable_mfa_for_user(user_id):
    # Generate a new TOTP secret
    secret = pyotp.random_base32()
    
    # Save the secret to the database
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Staff SET mfa_secret = %s WHERE s_email = %s", (secret, user_id))
    conn.commit()
    cur.close()
    conn.close()

    
    return secret
def generate_otp(mfa_secret):
	totp = pyotp.TOTP(mfa_secret)
	otp = totp.now()
	return otp
def send_otp_sms(user_phone_number, otp):
    # Twilio credentials
    account_sid = 'your_account_sid'
    auth_token = 'your_auth_token'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f"Your One-Time Password (OTP) is: {otp}",
        from_='+1234567890',  # Your Twilio phone number
        to=user_phone_number
    )
    return message.sid
@auth.route('/verify-mfa', methods=['POST'])
def verify_mfa():
    email = session.get('email')  # Assuming the user ID is in the session after initial login
    otp = request.form['otp']
    
    # Retrieve the user's MFA secret
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT mfa_secret FROM Staff WHERE s_email = %s", (email,))
    result = cursor.fetchone()
    cur.close()
    conn.close()
    
    if result:
        secret = result[0]
        totp = pyotp.TOTP(secret)
        
        # Validate the OTP
        if totp.verify(otp):
            session['mfa_authenticated'] = True
            flash("MFA successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid MFA code. Please try again.", "danger")
    else:
        flash("MFA not enabled for this account.", "warning")
    
    return redirect(url_for('login'))

@auth.route('/dashboard' , methods=['POST' , "GET"])
def dashboard():
	if request.method == 'POST':
		if session['admin'] == True:
			
			return render_template('auth.login')

		elif session['admin'] == False:
			return render_template('register')

		if 'admin' not in session:
			return redirect(url_for('login'))



	else:
		return render_template('dashboard.html')

@auth.route('/login' , methods=['POST' , 'GET'])
def login():
	if request.method == 'POST':
		email  = request.form['email']
		password = request.form['password']
		remember = request.form['remember']
		session['email'] = email
		if remember == '1':
			session.permanent = True
		else:
			session.permanent = False

		conn = get_db_connection()
		cur  = conn.cursor()
		cur.execute("SELECT * FROM Staff WHERE s_email = %s",(email,))
		data = cur.fetchone()
		cur.execute("SELECT staff.s_isadmin FROM Staff WHERE s_email = %s" , (session['email'],))
		data12 = cur.fetchall()

		cur.close()
		conn.close()
		if email:
			stored_password  = data[5]
			if check_password_hash(stored_password , password):
				

				return redirect(url_for('Inventory'))
			else:
				return 'Incorrect Password typed'

	if request.method == "GET":
		return render_template('auth.html')
#session.permanent=True
@auth.route('/register', methods=['GET'])
def register():


	return render_template('register.html')

@auth.route('/new_acc' , methods=['POST'])

def new_acc():
	conn = get_db_connection()
	cur = conn.cursor()

	username = request.form['username']
	email = request.form['email']
	password = request.form['password']

	contact = request.form['contact']
	pp  = generate_password_hash(password , method='pbkdf2:sha256', salt_length=12)
	is_admin = request.form['is_admin']
	cur.execute('INSERT INTO Staff ( s_name , s_email  , s_contact  ,pass)'
        'VALUES ( %s, %s, %s  , %s )',
        (
         f'{str(username)}',
         f'{str(email)}',
         f'{str(contact)}',
         f'{pp}')
        )
	conn.commit()
	cur.close()
	conn.close()
	print('account_succefully created' , 'info')
	return redirect(url_for('auth.login'))