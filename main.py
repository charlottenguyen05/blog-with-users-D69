from functools import wraps
import flask
from flask import render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from forms import RegisterForm, CreatePostForm, LoginForm, CommentForm
from database import app, db, BlogPost, User, Comment

ckeditor = CKEditor(app)
Bootstrap(app)
db.create_all()
login_manager = LoginManager()
login_manager.login_view = "/login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        name = form.name.data
        password = form.password.data
        find_user = User.query.filter_by(email=email).first()
        if find_user is not None:
            flash(f"Email address already in use, please try another email or go to ")
            return redirect("/register")
        else:
            new_user = User(
                email=email,
                name=name,
                password=generate_password_hash(password, 'pbkdf2:sha256', salt_length=8)
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        old_user = User.query.filter_by(email=email).first()
        if old_user is None or not check_password_hash(pwhash=old_user.password, password=password):
            flash("We can not find any account with that email/ password.")
            return redirect(url_for("login"))
        else:
            login_user(old_user)
            return redirect('/')
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    form = CommentForm()
    list_of_comments_obj = requested_post.comments  #
    if form.validate_on_submit() and current_user is not None:
        comment = form.comment.data
        new_com = Comment(comment=comment, blog=requested_post, poster=current_user)
        db.session.add(new_com)
        db.session.commit()
        return redirect(url_for("show_post", post_id=requested_post.id))
    return render_template("post.html", post=requested_post, form=form, user=current_user, comment=list_of_comments_obj, find=User.query.get)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

# Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 or user not login then return abort with 403 error
        if not current_user.is_authenticated or current_user.id != 1:
            return flask.abort(403)
        # Otherwise, continue with the route function
        return f(*args, **kwargs)
    return decorated_function


@app.route("/new-post", methods=['POST', 'GET'])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=['POST', 'GET'])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run()
