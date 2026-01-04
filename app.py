from flask import Flask, render_template, request, redirect, session
from config import get_db_connection

app = Flask(__name__)
app.secret_key= 'atm_secret_key'

@app.route('/',methods=['GET','POST'])
def login():
    error = None

    if request.method == 'POST':
        account_no = request.form['account_no']
        pin = request.form['pin']

        connection = get_db_connection()
        cursor = connection.cursor(
            "SELECT * FROM accounts WHERE account_no = %s AND pin = %s;",
            (account_no, pin)
        )
        user= cursor.fetchone()
        cursor.close()
        connection.close()

        if user:
            session['account_no'] = account_no
            return redirect('/dashboard')
        else:
            error = 'Invalid Account Number or PIN.'
    return render_template('login.html', error=error)


@app.route("/dashboard")
def dashboard():
    if "account_no" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        account_no=session["account_no"]
    )


@app.route('/balance')
def balance():
    if 'account_no' not in session:
        return redirect('/login')

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE account_no = %s;", (session["account_no"],))
    balance = cursor.fetchone()
    cursor.close()
    connection.close()

    return  render_template('balance.html', balance=balance)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
