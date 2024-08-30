import json
import random
from flask_login import current_user

def load_users():
    with open('./database/users.json', 'r') as file:
        return json.load(file)

def load_payments():
    with open('./database/payments.json', 'r') as file:
        return json.load(file)

def save_user(user):
    with open('./database/users.json','w') as users_db:
        json.dump(user, users_db, indent=4)

def save_payments(payments):
    with open('./database/payments.json','w') as payments_db:
        json.dump(payments, payments_db, indent=4)

def login_user(username,password):
    users = load_users()
    try:
        for user in users:
            if user.get('username') == username:
                if user.get('password') == password:
                    return True
                return False
    except:
        return False

def register_user(username,password):
    users = load_users()
    for user in users:
        if user.get('username') == username:
            return False
            break
    new_user = {"username": username, "password": password, "saldo": 0}
    users.append(new_user)
    save_user(users)
    return True

def get_user_saldo(username):
    users = load_users()
    for user in users:
        if user.get('username') == username:
            saldo = user.get('saldo')
            return int(saldo)

def convert_value(value):
    payment_str = str(value)
    cleaned_str = ''.join(char for char in payment_str if char.isdigit() or char == ',')
    payment_float = float(cleaned_str.replace(',', '.'))
    payment_rounded = round(payment_float, 2)
    return payment_rounded

def add_saldo(username,value):
    users = load_users()
    for user in users:
        if user.get('username') == username:
            user['saldo'] += value
            save_user(users)
            break

def remove_saldo(username,value):
    users = load_users()
    for user in users:
        if user.get('username') == username:
            user['saldo'] -= value
            save_user(users)
            break

def aprove_payment(transfer_to,value):
    users = load_users()
    value = convert_value(value)
    if transfer_to == current_user.username:
        return False
    for user in users:
        if user.get('username') == current_user.username:
            saldo = get_user_saldo(user.get('username'))
            if saldo <= value:
                return False
            for user in users:
                if user.get('username') == transfer_to:
                    add_saldo(transfer_to,value)
                    remove_saldo(current_user.username,value)
                    return True
                    break
            return False

def check_payment_request(payment_id):
    payment_requests = load_payments()
    for payment in payment_requests:
        if payment.get('payment_user') == current_user.username:
            return False
        if payment.get('payment_id') == int(payment_id):
            return True
    return False

def payment_request_accept(payment_id):
    payment_requests = load_payments()
    for payment in payment_requests:
        if payment.get('payment_id') == int(payment_id):
            pay_value = payment.get('payment_value')
            pay_user = payment.get('payment_user')
            break
    if current_user.saldo <= int(pay_value):
        return False
    add_saldo(pay_user,int(pay_value))
    remove_saldo(current_user.username,int(pay_value))
    for payment in payment_requests:
        if payment.get('payment_id') == int(payment_id):
            payment_requests.remove(payment)
            save_payments(payment_requests)
            break
    return True

def create_payment(value,comment):
    if comment == '':
        comment = 'None'
    payment_requests = load_payments()
    for payment in payment_requests:
        if payment.get('payment_user') == current_user.username:
            return False
            break
    payment_id = ""
    for _ in range(7):
        payment_id += str(random.randint(0, 9))

    value = convert_value(value)
    new_request = {"payment_id": int(payment_id),"payment_user": current_user.username,"payment_value": value,"payment_comment": comment}
    payment_requests.append(new_request)
    save_payments(payment_requests)
    return True

if __name__ == '__main__':
    print('you cannot open this module alone.')