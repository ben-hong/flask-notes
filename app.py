from flask import Flask, request, redirect, render_template, jsonify, session, flash
from models import db, connect_db, User
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

app.config['SECRET_KEY'] = "SECRET!"
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

@app.route('/')
def homepage():
    """ redirects to /register """

    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def register():
    """ Registers a user """

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, password, email, first_name, last_name)
        db.session.add(user)
        db.session.commit()

        session["username"] = user.username

        # on successful login, redirect to secret page
        return redirect("/secret")

    else:
        return render_template("register.html", form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """ Logs in a user """

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username  # keep logged in
            return redirect(f"/users/{username}")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)    

@app.route('/users/<username>')
def user_page(username):
    """ Renders user page which show user information """

    user = User.query.get_or_404(username)

    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/")

        # alternatively, can return HTTP Unauthorized status:
        #
        # from werkzeug.exceptions import Unauthorized
        # raise Unauthorized()

    else:
        return render_template("user_page.html", user=user)

@app.route('/logout')
def logout():
    """Logs out the user"""

    session.pop('username', None)

    return redirect('/')

@app.route("/users/<username>/delete", methods=['POST'])
def delete_user(username):
    username = User.query.get_or_404(username)
    db.session.delete(username)
    db.session.commit()

    return redirect("/")

@app.route("/users/<username>/notes/add", methods=['GET', 'POST'])
def add_notes(username):
    
    form = NotesForm()

    if validate_on_submit():
        title = form.title.data
        content = form.content.data

        note = Note(title=title, content=content, owner=username)
        db.session.add(note)
        db.session.commit()

        return redirect(f"/users/{username}")
    
    else:
        return render_template("add_notes_form.html", form=form)


