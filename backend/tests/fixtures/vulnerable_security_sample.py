import os
import pickle
import subprocess
import hashlib
import yaml
from flask import Flask, request, render_template_string

app = Flask(__name__)

API_KEY = "sk-live-51H8xJ2eZvKYlo2CabcDEF123456"
DB_PASSWORD = "changeme"


def get_user(username):
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)


def get_user_safe(username):
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))


def run_command(filename):
    subprocess.run(f"tar -czf backup.tar.gz {filename}", shell=True)


def run_command_safe(filename):
    subprocess.run(["tar", "-czf", "backup.tar.gz", filename], shell=False)


def old_system_call(target):
    os.system("ping " + target)


def load_data(raw_bytes):
    return pickle.loads(raw_bytes)


def load_yaml_config(raw_text):
    return yaml.load(raw_text)


def load_yaml_config_safe(raw_text):
    return yaml.safe_load(raw_text)


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def hash_password_safe(password):
    import bcrypt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def run_eval(expr):
    return eval(expr)


@app.route("/render")
def render_page():
    name = request.args.get("name")
    return render_template_string(f"<h1>Hello {name}</h1>")


@app.route("/admin/delete", methods=["POST"])
def delete_user():
    user_id = request.form.get("id")
    db.delete(user_id)
    return "deleted"


@app.route("/admin/delete-safe", methods=["POST"])
def delete_user_safe(current_user=Depends(require_admin)):
    user_id = request.form.get("id")
    db.delete(user_id)
    return "deleted"
