from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, EditProfileForm
from config import secret_key

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key


# Connect to db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy()
db.init_app(app)


# Configure tables
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    profile_picture = db.Column(db.String(255), default="/static/images/astro.png")


# Creating tables
with app.app_context():
    db.create_all()


# Initializing flask-login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)



@app.route('/')
def home():
    return render_template('index.html')



@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegisterForm()
    if form.validate_on_submit():

        result = db.session.execute(db.select(User).where(User.email==form.email.data))
        user = result.scalar()
        if user:
            flash("This email address is already in use, please log in or try with another email.", category="danger")
            return redirect(url_for('login'))
        
        # Hashing and salting password
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method="pbkdf2:sha256",
            salt_length=8
        )

        # Creating new user 
        new_user = User(
            username = form.name.data,
            email = form.email.data,
            password = hash_and_salted_password,
            profile_picture="/static/images/profile_pictures/astronaut.jpg"  # Default profile picture
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))
    
    # Checking if both passwords match
    if form.password.data != form.password2.data:
        flash("Passwords do not match, please try again.", category="danger")
        return redirect(url_for("register"))


    return render_template('register.html', form=form)



@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        # If email does not exist
        if not user:
            flash("This email does not exist, please try again.", category="danger")
            return redirect(url_for('login'))
        
        #If incorrect password
        elif not check_password_hash(user.password, password):
            flash("Incorrect password, please try again.", category="danger")
            return redirect(url_for('login'))
        
        else:
            login_user(user)
            flash("Logged in successfully.", category="success")
            return redirect(url_for('home'))
        
    return render_template('login.html', form=form)



@app.route('/logout')
def logout():
    logout_user()
    flash("Logged out", category="success")
    return redirect(url_for("home"))



@app.route('/contact')
def contact_page():
    return render_template("contact.html")



@app.route('/about')
def about_page():
    return render_template("about.html")



@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    
    form = EditProfileForm()

    if form.validate_on_submit():
        new_username = form.username.data
        new_email = form.email.data
        new_password = form.password.data
        new_profile_picture = form.profile_picture.data

        if new_username:
            current_user.username = new_username
        
        # Warunki sprawdzające, czy new_email nie jest puste, poza blokiem validate_on_submit
        if new_email:
            current_user.email = new_email


        if new_password:
            # Użyj funkcji generate_password_hash, aby uzyskać zahashowane hasło
            hashed_password = generate_password_hash(
                new_password,
                method="pbkdf2:sha256",
                salt_length=8
            )
            # Przypisz zahashowane hasło do pola password
            current_user.password = hashed_password

        if new_profile_picture:
            current_user.profile_picture = new_profile_picture

        if 'cancel' in request.form:
            pass
        else:
            db.session.commit()
        

        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', form=form)

# TODO: Add forgot route and style it in forgot.html
@app.route('/forgot_password')
def forgot():
    return render_template("forgot.html")



if __name__ == '__main__':
    app.run(debug=True)