import json
import os
import uuid
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-dev-key")

USERS_FILE = os.path.join("data", "users.json")
INVOICES_FILE = os.path.join("data", "invoices.json")


def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


@app.route("/")
def index():
    if "user_email" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or len(password) < 6:
            return render_template("register.html", error="Valid email and password (min 6 chars) required.")

        users = load_json(USERS_FILE)
        if any(u["email"] == email for u in users):
            return render_template("register.html", error="An account with that email already exists.")

        users.append({
            "email": email,
            "password_hash": generate_password_hash(password)
        })
        save_json(USERS_FILE, users)

        session["user_email"] = email
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        users = load_json(USERS_FILE)
        user = next((u for u in users if u["email"] == email), None)

        if not user or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid email or password.")

        session["user_email"] = email
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if "user_email" not in session:
        return redirect(url_for("login"))

    all_invoices = load_json(INVOICES_FILE)
    user_invoices = [inv for inv in all_invoices if inv["user_email"] == session["user_email"]]
    return render_template("dashboard.html", user_email=session["user_email"], invoices=user_invoices)


@app.route("/invoices", methods=["POST"])
def create_invoice():
    if "user_email" not in session:
        return redirect(url_for("login"))

    client_name = request.form.get("client_name", "").strip()
    tax_rate = float(request.form.get("tax_rate", 0) or 0)
    descriptions = request.form.getlist("description[]")
    quantities = request.form.getlist("quantity[]")
    prices = request.form.getlist("price[]")

    items = []
    subtotal = 0.0
    for desc, qty, price in zip(descriptions, quantities, prices):
        q = float(qty or 0)
        p = float(price or 0)
        if desc.strip() and q > 0 and p >= 0:
            items.append({"description": desc.strip(), "quantity": q, "price": p})
            subtotal += q * p

    tax_amount = subtotal * (tax_rate / 100.0)
    total = subtotal + tax_amount

    invoices = load_json(INVOICES_FILE)
    invoices.append({
        "id": str(uuid.uuid4())[:8],
        "user_email": session["user_email"],
        "client_name": client_name,
        "items": items,
        "subtotal": round(subtotal, 2),
        "tax_rate": tax_rate,
        "tax_amount": round(tax_amount, 2),
        "total": round(total, 2),
        "status": "Unpaid"
    })
    save_json(INVOICES_FILE, invoices)

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)
