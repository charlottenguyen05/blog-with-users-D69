from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("KEY")
# Update the app config to use "DATABASE_URL" environment variable if provided,
# but if it's None (e.g. when running locally) then we can provide sqlite:///blog.db as the alternative.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL_1",  "sqlite:///blog.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Base = declarative_base()


# Video tutorial on relationship patterns:
# https://www.nsfwyoutube.com/watch?v=VVX7JIWx-ss
# https://www.nsfwyoutube.com/watch?v=mwjrtntk0PE

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    # Create a FOREIGN KEY to LINK USERS (MUST BE ON THE CHILD class) (Refer to the PRIMARY KEY of the user) (CREATE NEW COLUMN name author_id INSIDE BLOGPOST DB)
    # Inside ForeignKey function is what is going to be associate with this column (users.id - The id column in the table name users)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts property in the User class.
    # list of posts of one author: <author_obj>.posts.img_url
    author = db.relationship("User", back_populates="posts")
    # 3. Add db.relationship() with Comment class
    comments = db.relationship("Comment", back_populates="blog")

class User(UserMixin, db.Model):
    __tablename__ = "users"  # Name of the table
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    # Add db.relationship() to create a relationship -> this attribute act like a List of BlogPost objects attached to each User.
    # First argument: NAME OF THE OTHER CLASS (TO LINK)
    # Second argument: back_populates: Tên của user object nói chung, dùng để access tất cả các property của class đấy.
    # EX: <post_obj>.author.id will return the id of the user that write that post và tương tự author.email, author.name,...
    posts = db.relationship("BlogPost", back_populates="author")
    comments = db.relationship("Comment", back_populates="poster")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(500), nullable=False)
    poster = db.relationship("User", back_populates="comments")
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # ForeignKey for the users table
    # Create a one-to-many relationship: Comment = children and BlogPost = parent (a post can have a lot of comments)
    # 1. ForeignKey for blog_posts table
    blog_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    # 2. Add db.relationship() with BlogPost class
    blog = db.relationship("BlogPost", back_populates="comments")

