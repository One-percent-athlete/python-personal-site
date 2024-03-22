from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime
import requests
import smtplib
import dotenv
import os
dotenv.load_dotenv()

my_email = os.environ.get("my_email")
password = os.environ.get("password")

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

with app.app_context():
    db.create_all()

class PostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField('body')
    submit = SubmitField("Submit Post")


@app.route('/')
def home():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    posts = db.session.execute(db.select(BlogPost).order_by(BlogPost.id)).scalars().all()
    return render_template("index.html", all_posts=posts)

# TODO: Add a route so that you can click on individual posts.
@app.route('/post/<int:post_id>', methods=["GET"])
def show_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


@app.route("/new-post", methods=["GET", "POST"])
def new_post():
    form = PostForm()
    # TODO: add_new_post() to create a new blog post
    if form.validate_on_submit():
        new_post = BlogPost(
            title = request.form["title"],
            subtitle = request.form["subtitle"],
            author = request.form["author"],
            date = datetime.now().strftime("%B %d, %Y"),
            body = request.form["body"],
            img_url = request.form["img_url"]
            )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make-post.html", form=form)

# TODO: edit_post() to change an existing blog post
@app.route('/edit-post/<int:post_id>', methods=["GET","POST"])
def edit_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    edit_post = db.get_or_404(BlogPost, post_id)
    edit_form = PostForm(
        title=edit_post.title,
        subtitle=edit_post.subtitle,
        img_url=edit_post.img_url,
        author=edit_post.author,
        body=edit_post.body
    )
    if edit_form.validate_on_submit():
        edit_post.title = edit_form.title.data
        edit_post.subtitle = edit_form.subtitle.data
        edit_post.author = edit_form.author.data
        edit_post.body = edit_form.body.data
        edit_post.img_url = edit_form.img_url.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=edit_post.id))
    return render_template("make-post.html", form=edit_form, post=edit_post, is_edit=True)



# TODO: delete_post() to remove a blog post from the database
@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    requested_post = db.get_or_404(BlogPost, post_id)
    db.session.delete(requested_post)
    db.session.commit()
    return redirect(url_for("home"))


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


if __name__ == "__main__":
    app.run(debug=True)
