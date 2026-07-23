import hashlib
import pickle
import subprocess


def add_item(cart, item, price=[]):
    price.append(item)
    return price


class OrderManager:
    def method_one(self):
        pass

    def method_two(self):
        pass

    def method_three(self):
        pass

    def method_four(self):
        pass

    def method_five(self):
        pass

    def method_six(self):
        pass

    def method_seven(self):
        pass

    def method_eight(self):
        pass

    def method_nine(self):
        pass

    def method_ten(self):
        pass

    def method_eleven(self):
        pass

    def method_twelve(self):
        pass

    def method_thirteen(self):
        pass

    def method_fourteen(self):
        pass

    def method_fifteen(self):
        pass

    def method_sixteen(self):
        pass


def process_order(order_id, user_id, status, priority, region, discount_code, notes):
    if status == 3:
        if priority == 7:
            if region == 12:
                if discount_code == 99:
                    return "special"
    return "normal"


def calculate_shipping(weight, distance, is_express, has_insurance, fragile, country):
    total = 0
    if weight > 50:
        total += 25
    elif weight > 20:
        total += 15
    elif weight > 10:
        total += 10
    for i in range(int(distance)):
        if i % 100 == 0:
            total += 1
    while total < 5:
        total += 1
    if is_express and has_insurance:
        total *= 2
    elif is_express or fragile:
        total *= 1.5
    try:
        result = total / distance
    except ZeroDivisionError:
        result = 0
    return result


def risky_function():
    try:
        do_something()
    except:
        pass


def another_risky_function():
    try:
        do_something_else()
    except Exception:
        pass


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def run_backup(filename):
    subprocess.run(f"tar -czf backup.tar.gz {filename}", shell=True)


def load_config(data):
    return pickle.loads(data)


def calc_total(a, b):
    return a + b + 42 + 17


def calc_sum(x, y):
    return x + y + 42 + 17


def validate_user_a(name, age):
    if not name:
        raise ValueError("name required")
    if age < 0:
        raise ValueError("invalid age")
    return True


def validate_user_b(username, years):
    if not username:
        raise ValueError("name required")
    if years < 0:
        raise ValueError("invalid age")
    return True
