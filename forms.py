from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, EmailField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired,EqualTo, Length, Email


class RegisterForm(FlaskForm):
    name = StringField("Userame", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign me up")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log me in")

class EditProfileForm(FlaskForm):
    username = StringField('Username')
    email = EmailField('Email')
    password = PasswordField('Password')
    profile_picture = SelectField('Profile Picture', choices=[
        ('/static/images/profile_pictures/astronaut.jpg', 'Astronaut'), 
        ('/static/images/profile_pictures/astro_female.jpg', 'Female Astronaut'),
        ('/static/images/profile_pictures/astro_king.jpg', 'King'),
        ('/static/images/profile_pictures/astro_cesar.jpg', 'Cesar'),
        ('/static/images/profile_pictures/astro_cowboy.jpg', 'Cowboy'),
        ('/static/images/profile_pictures/astro_pirat.jpg', 'Pirat'),
        ('/static/images/profile_pictures/astro_warrior.jpg', 'Warrior'),
        ('/static/images/profile_pictures/astro_samurai.jpg', 'Samurai'),
        ('/static/images/profile_pictures/astro_wizard.jpg', 'Wizard'),
        ('/static/images/profile_pictures/astro_witch.jpg', 'Witch'),
        ('/static/images/profile_pictures/astro_devil.jpg', 'Devil'),
        ('/static/images/profile_pictures/astro_reaper.jpg', 'Reaper'),
        ('/static/images/profile_pictures/astro_koala.jpg', 'Koala'),
        ('/static/images/profile_pictures/astro_fox.jpg', 'Fox'),
        ('/static/images/profile_pictures/astro_panda.jpg', 'Panda'),
    ])
    submit = SubmitField('Save Changes')


class ForgotForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    submit = SubmitField('Request reset')


# TODO: Make working reset password form
    
class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')