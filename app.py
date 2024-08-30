
import os
from flask_session import Session
from modules import database_module
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import Flask, render_template, url_for, request, redirect, send_from_directory, flash,get_flashed_messages

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'secretkey'

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, username, saldo):
        self.username = username
        self.saldo = saldo

@login_manager.user_loader
def load_user(user_id):
    users = database_module.load_users()
    for user in users:
        if user['username'] == user_id:
            loaded_user = User(user_id, user['saldo'])
            return loaded_user
    return None

@app.route('/')
def main_page():
    return render_template('index.html')

@app.route('/register',methods=["GET","POST"])
def register_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == '':
            flash('Choose an username for you.')
            return redirect(url_for('register_page'))
        if password == '':
            flash('You didnt pass any password.')
            return redirect(url_for('register_page'))
        if len(username) >= 17:
            flash('You reached the limit of characters, 16.')
            return redirect(url_for('register_page'))
        if database_module.register_user(username,password):
            return redirect(url_for('login_page'))
        flash('This username is already taken.')
        return redirect(url_for('register_page'))
    messages = get_flashed_messages()
    return render_template('register.html',flashed_messages=messages)

@app.route('/login',methods=["GET","POST"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if database_module.login_user(username,password):
            user_obj = User(username, database_module.get_user_saldo(username))
            user_obj.id = username
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        flash('Username or password wrong.')
        return redirect(url_for('login_page'))
    messages = get_flashed_messages()
    return render_template('login.html',flashed_messages=messages)

@app.route('/dashboard')
@login_required
def dashboard():
    messages = get_flashed_messages()
    return render_template('dashboard.html',flashed_messages=messages)

@app.route('/recive',methods=["GET","POST"])
@login_required
def paymentcreator_page():
    if request.method == "POST":
        value = request.form['value-field']
        comment = request.form['comment']
        if value == '':
            flash('You didnt pass the value.')
            return redirect(request.referrer)
        if database_module.create_payment(value,comment):
            return redirect(url_for('dashboard'))
        return redirect(request.referrer)
    messages = get_flashed_messages()
    return render_template('transaction.html',flashed_messages=messages)

@app.route('/pay/<pay_id>',methods=["GET","POST"])
@login_required
def recive_page(pay_id):
    if request.method == "POST":
        if database_module.payment_request_accept(pay_id):
            return redirect(url_for('dashboard'))
        flash("You dont have enough cash to pay")
        return redirect(request.referrer)
    if database_module.check_payment_request(pay_id):
        payments = database_module.load_payments()
        for payment in payments:
            if payment.get('payment_id') == pay_id:
                payment = payment
                break
        messages = get_flashed_messages()
        return render_template('pay.html',payment=payment,pay_id=pay_id,flashed_messages=messages)
    return redirect(url_for('dashboard'))

@app.route('/aprove-payment', methods=["POST"])
@login_required
def aprove_payment():
    transfer_to = request.form['user-field']
    value = request.form['value-field']
    if transfer_to == '':
        flash("You didn't pass transfer account.")
        return redirect(url_for('dashboard'))
    if value == '':
        flash("You need to add the value.")
        return redirect(url_for('dashboard'))
    if database_module.aprove_payment(transfer_to,value):
        return redirect(url_for('dashboard'))
    
    flash("Transaction error, check any errors.")
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_page'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static','imgs'),'favicon.png', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(401)
def unauthorized(error):
     return redirect(url_for('main_page')) 

@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('main_page'))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=80)
