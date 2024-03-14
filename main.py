from flask import Flask, render_template, request
import requests
import smtplib
import dotenv
import os
dotenv.load_dotenv()
my_email = os.environ.get("my_email")
password = os.environ.get("password")

app = Flask(__name__)
res = requests.get("https://api.npoint.io/d3fe87fb4bf6191d3651")
articles = res.json()

@app.route("/")
def home():
    return render_template("index.html", all_articles=articles)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = request.form
        name = data["name"]
        email = data["email"]
        message = data["message"]
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.sendmail(
                from_addr=my_email, 
                to_addrs=email, 
                msg=f"Subject:{name}Thank you for your inquiry\n\nYou message was {message}Here is your answer!")
        return render_template("contact.html", message_sent=True)
    return render_template("contact.html", message_sent=False)

@app.route('/post/<int:index>')
def get_post(index):
    article = None
    for a in articles:
        if a["id"] == index:
            article = a
    return render_template("post.html", article=article)


if __name__ == "__main__":
    app.run(debug=True)
