from flask import Flask, render_template, request,redirect
from config import db
import matplotlib.pyplot as plt
import os
app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Expense Tracker</h1><p>Welcome to our Expense Tracker Web App!</p>"
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users(username, email, password) VALUES(%s, %s, %s)",
            (username, email, password)
        )
        db.commit()
        cursor.close()

        return "Registration Successful!"

    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()
        cursor.close()

        if user:
            return redirect("/dashboard")
        else:
            return "Invalid Email or Password!"

    return render_template("login.html")
@app.route("/dashboard")
def dashboard():
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM expenses WHERE user_id=%s", (1,))
    expenses = cursor.fetchall()
    categories = [expense["category"] for expense in expenses]
    amounts = [float(expense["amount"]) for expense in expenses]

    plt.figure(figsize=(6,4))
    plt.bar(categories, amounts)
    plt.title("Expenses by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount")
    plt.tight_layout()

    if not os.path.exists("static"):
      os.makedirs("static")

    plt.savefig("static/chart.png")
    plt.close()

    cursor.execute("SELECT SUM(amount) AS total FROM expenses WHERE user_id=%s", (1,))
    total = cursor.fetchone()["total"] or 0
    print(total)
    cursor.close()
    return render_template("dashboard.html",expenses=expenses,total=total,chart="chart.png")
@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        description = request.form["description"]
        expense_date = request.form["expense_date"]

        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO expenses(user_id, amount, category, description, expense_date) VALUES(%s, %s, %s, %s, %s)",
        (1, amount, category, description, expense_date)
    )
        db.commit()
        cursor.close()

        return redirect("/dashboard")
    return render_template("add_expense.html")

@app.route("/edit_expense/<int:id>",methods=["GET","POST"])
def edit_expense(id):
    cursor = db.cursor(dictionary=True)

    cursor.execute(
    "SELECT * FROM expenses WHERE id=%s",
    (id,)
)

    expense = cursor.fetchone()
    cursor.close()
    if request.method == "POST":
        print(request.method)
        amount = request.form["amount"]
        category = request.form["category"]
        description = request.form["description"]
        expense_date = request.form["expense_date"]

        cursor = db.cursor()
        cursor.execute("""
            UPDATE expenses
            SET amount=%s,
              category=%s,
              description=%s,
              expense_date=%s
            WHERE id=%s
        """, (amount, category, description, expense_date, id))

        db.commit()
        cursor.close()

        return redirect("/dashboard")

    return render_template("edit_expense.html",expense=expense)
@app.route("/delete_expense/<int:id>")
def delete_expense(id):
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id=%s",
        (id,)
    )

    db.commit()
    cursor.close()

    return redirect("/dashboard")
@app.route("/view_expenses")
def view_expenses():
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM expenses WHERE user_id=%s", (1,))
    expenses = cursor.fetchall()

    cursor.close()

    return render_template("view_expenses.html", expenses=expenses)
    
if __name__ == "__main__":
    app.run(debug=True)