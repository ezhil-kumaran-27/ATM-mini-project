from flask import Flask, render_template, request, redirect, session
from config import get_db_connection

app = Flask(__name__)
app.secret_key = "atm_secret_key"

@app.route("/")
def index():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        account_no = request.form["account_no"]
        pin = request.form["pin"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM users WHERE account_no = %s AND pin = %s",
            (account_no, pin)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session["account_no"] = account_no
            return redirect("/dashboard")
        else:
            error = "Invalid Account Number or PIN"

    return render_template("login.html", error=error)


@app.route("/dashboard")
def dashboard():
    if "account_no" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        account_no=session["account_no"]
    )

@app.route("/balance")
def balance():
    if "account_no" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT balance FROM users WHERE account_no = %s",
        (session["account_no"],)
    )
    balance = cur.fetchone()[0]
    cur.close()
    conn.close()

    return render_template("balance.html", balance=balance)

@app.route("/deposit",methods=['GET', 'POST'])
def deposit():
    if "account_no" not in session:
        return redirect("/login")
    error = None
    if request.method == 'POST':
        amount = request.form['amount']

        if int(amount) < 0:
            error = "Amount cannot be negative"
        else:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                "UPDATE users SET balance = %s WHERE account_no = %s",
                (amount, session["account_no"])
            )
            cursor.execute(
                "INSERT INTO transactions (account_no,type, amount) VALUES (%s,%s, %s)",
                (session["account_no"],'Deposit',amount)
            )

            connection.commit()
            cursor.close()
            connection.close()

            return redirect("/dashboard")
    return render_template("deposit.html", error=error)


@app.route("/withdraw",methods=['GET', 'POST'])
def withdraw():
    if "account_no" not in session:
        return redirect("/login")
    error = None
    if request.method == "POST":
        amount = int(request.form['amount'])

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT balance FROM users WHERE account_no = %s",
            (session["account_no"],)
        )
        balance = cursor.fetchone()[0]
        if amount <=0:
            error = "Amount cannot be negative"
        elif amount > balance:
            error = "Insufficent balance"
        else:
            #deduct balance
            cursor.execute("UPDATE users SET balance = %s WHERE account_no = %s",
                           ( amount, session["account_no"])
                           )
            connection.commit()
            cursor.close()
            connection.close()
            return redirect("/dashboard")
        cursor.close()
        connection.close()
    return render_template("withdraw.html", error=error)

@app.route("/transcation",methods=['GET', 'POST'])
def transcation():
    if "account_no" not in session:
        return redirect("/login")

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT type,amount, data FROM transaction WHERE account_no = %s ORDER BY date DESC",
        (session["account_no"],)
    )
    transcation = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("transcation.html", transcation=transcation)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
