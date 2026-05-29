from flask import Flask, render_template, request, redirect
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

def get_db():
    return sqlite3.connect("database.db")

# HOME PAGE
@app.route("/")
def home():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses ORDER BY date DESC")
    expenses = cur.fetchall()
    conn.close()
    return render_template("index.html", expenses=expenses)

# ADD EXPENSE
@app.route("/add", methods=["GET","POST"])
def add():
    if request.method == "POST":
        title = request.form["title"]
        amount = float(request.form["amount"])
        category = request.form["category"]
        date = request.form["date"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO expenses(title,amount,category,date) VALUES (?,?,?,?)",
            (title, amount, category, date)
        )
        conn.commit()
        conn.close()
        return redirect("/")

    return render_template("add.html")

# REPORT
@app.route("/report")
def report():
    conn = get_db()
    df = pd.read_sql_query("SELECT category, amount FROM expenses", conn)
    conn.close()

    if df.empty:
        return render_template("report.html", chart=False)

    summary = df.groupby("category")["amount"].sum()

    plt.figure(figsize=(8,8))

    colors = ['#ff6b6b', '#4ecdc4', '#ffe66d', '#5f27cd']

    plt.pie(
        summary,
        labels=summary.index,
        autopct='%1.1f%%',
        colors=colors,
        shadow=True,
        startangle=90
    )

    plt.title("📊 Expense Distribution", fontsize=18)
    plt.ylabel("")

    os.makedirs("static/charts", exist_ok=True)
    plt.savefig("static/charts/report.png")
    plt.close()

    return render_template("report.html", chart=True)
if __name__ == "__main__":
    app.run(debug=True)