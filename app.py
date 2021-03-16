from flask import Flask, request, redirect, render_template, jsonify, session, flash
from models import db, connect_db, User, Note
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm, NotesForm

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
        return redirect(f"/users/{user.username}")

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

    if "username" not in session or session["username"] != username:
        flash("You must be logged in to view!")
        return redirect("/")

    else:
        return render_template("user_page.html", user=user)

@app.route('/logout')
def logout():
    """Logs out the user"""

    session.pop('username', None)

    return redirect('/')

@app.route("/users/<username>/delete", methods=['GET', 'POST'])
def delete_user(username):
    user = User.query.get_or_404(username)
    for note in user.notes:
        db.session.delete(note)
    db.session.delete(user)
    db.session.commit()

    return redirect("/")

@app.route("/users/<username>/notes/add", methods=['GET', 'POST'])
def add_notes(username):
    
    form = NotesForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        note = Note(title=title, content=content, owner=username)
        db.session.add(note)
        db.session.commit()

        return redirect(f"/users/{username}")
    
    else:
        return render_template("add_notes_form.html", form=form)

@app.route("/notes/<int:note_id>/update", methods=['GET', 'POST'])
def update_note(note_id):
    """ updates a note and redirects it to the user page"""

    note = Note.query.get_or_404(note_id)
    form = NotesForm(obj=note)
    form.populate_obj(note)

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data

        db.session.commit()
        return redirect(f'/users/{note.user.username}')
    
    return render_template("update_notes_form.html", form=form)

@app.route("/notes/<int:note_id>/delete", methods=['GET', 'POST'])
def delete_note(note_id):
    """deletes note and redirects to current user"""
    note = Note.query.get_or_404(note_id)
    user = note.user.username
    db.session.delete(note)
    db.session.commit()

    return redirect(f"/users/{user}")



