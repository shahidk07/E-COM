from flask import Flask, request, redirect, render_template, session
from random import randint
import sqlite3
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = "some-random-secret-key"

@app.route("/forgot_password",methods=["GET"])
def send_page():
    return render_template('forgot.html')


@app.route("/send_otp", methods=["POST"])
def send_otp():
    
    email = request.form.get("email")
    if not email:
        return "<script>alert('Email is required');window.location='/forgot_password';</script>"

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    row = conn.execute("SELECT * FROM forgot_password_app WHERE email=?", (email,)).fetchone()
    conn.close()
    if not row:
        return "<script>alert('We do not have an account registered with this email id')</script>"
        
    otp = str(randint(100000, 999999))
    session["email"] = email
    session["otp"] = otp
   
    # create email
    msg = EmailMessage()
    msg["Subject"] = "Password Reset OTP Testing"
    msg["From"] = "viperoflegendkiller@gmail.com"
    msg["To"] = email
    html = render_template(
    "email.html",
    otp=otp
)

    msg.set_content(f"your otp is {otp}")
    msg.add_alternative(html, subtype="html")
    # send email
    #Secure Socket Layer
    #SSL is a tech that encrypts data sent between computers over a network
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("viperoflegendkiller@gmail.com","qmkr qfhl uepd ktra")
        smtp.send_message(msg)
        
    return redirect("/verify")

@app.route("/verify",methods=["POST","GET"])
def verify():
    if(request.method=="GET"):
        print("GET request received",flush=True)
        return render_template("verify.html")
    
    else:
        entered_otp=request.form["otp"]
        sent_otp=session["otp"]
        if sent_otp==entered_otp:
            print("OTP verified successfully",flush=True)
            return render_template("reset.html")
        else:
            print("Invalid OTP",flush=True)
            return "<script>alert('Invalid OTP');window.location='/verify';</script>"
        
        
@app.route("/reset",methods=["POST","GET"])

def reset():
    if(request.method=="GET"):
        return render_template("reset.html")
    else:
        email=session["email"]
        password=request.form["password"]
        
        conn = sqlite3.connect('database.db')
        print("Database Connection Established")
        conn.row_factory = sqlite3.Row
        conn.execute("UPDATE forgot_password_app set password=? WHERE email=?", (password, email))
        conn.commit()
        conn.close()
        return "<script>alert('Password changed successfully');</script>"


if __name__ == "__main__":
    app.run(debug=True)