from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, EditProfileForm, ForgotForm, ResetPasswordForm

from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_mail import Mail, Message
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_app_super_secret_key'
# Mail config
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')

# Connect to db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy()
db.init_app(app)
# Initializing flask-mail
mail = Mail(app)



# Configure tables
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    profile_picture = db.Column(db.String(255), default="/static/images/astro.png")

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id})
    

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        
        return User.query.get(user_id) 
    #try db.session.execute(db.select(User).where(User.id == id))

print(User.get_reset_token)

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
        
        # Checking if new email field is not empty
        if new_email:
            current_user.email = new_email


        if new_password:
            # Password hashing
            hashed_password = generate_password_hash(
                new_password,
                method="pbkdf2:sha256",
                salt_length=8
            )
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


def send_reset_email(user):
    s = Serializer(app.config['SECRET_KEY'])
    token = s.dumps({'user_id': user.id})
    msg = Message(
        "Password reset request",
        sender="noreply@gmail.com",
        recipients=[user.email]
    )
    reset_url = url_for('reset_token', token=token, _external=True)
    msg.body = f'''To reset your password please click on the following link:
{reset_url}

If you did not request this then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

#TODO: Complete work with password reset routes
@app.route('/reset_password', methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = ForgotForm()
    if form.validate_on_submit():
        email = form.email.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        send_reset_email(user)
        flash("An email has been sent", category="success")
        return redirect(url_for('login'))
    return render_template("forgot.html", form=form)


@app.route('/reset_password/<token>', methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)

    if not user:
        flash("That is an invalid or expired token", category="danger")
        return redirect(url_for('reset_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():

        # Hashing and salting password
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method="pbkdf2:sha256",
            salt_length=8
        )

        # Creating new password
        user.password = hash_and_salted_password
        db.session.commit()
        flash("Your password has been changed. You are now able to log in.", category="success")
        return redirect(url_for('login'))
    return render_template("reset-password.html", form=form)



if __name__ == '__main__':
    app.run(debug=True)