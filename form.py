from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, URLField, SelectField, TextAreaField
from wtforms.validators import DataRequired, URL, Regexp


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Regexp(r'^(?=.*[A-Za-z])(?=.*[\d])(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
            message="Password must contain at least one letter, one digit, and one special character.")])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddCafes(FlaskForm):
    name = StringField('Cafe', validators=[DataRequired()])
    image = URLField('Image Link', validators=[DataRequired(), URL()])
    location = StringField('Location', validators=[DataRequired()])
    map = URLField('Google Link', validators=[DataRequired(), URL()])
    wifi = SelectField('Wifi', validators=[DataRequired()], choices=[('✅', 'Yes'), ('❌', 'No')])
    socket = SelectField('Socket', validators=[DataRequired()], choices=[('✅', 'Yes'), ('❌', 'No')])
    toilet = SelectField('Toilet', validators=[DataRequired()], choices=[('✅', 'Yes'), ('❌', 'No')])
    price = StringField('Approx Price', validators=[DataRequired()])
    timing = StringField('Timings', validators=[DataRequired()])
    submit = SubmitField('Submit Cafe')


class CommentAndRating(FlaskForm):
    comment = TextAreaField()
    ratings = SelectField('Ratings(out of 5)', validators=[DataRequired()],
                          choices=[('⭐', 1), ('⭐⭐', 2), ('⭐⭐⭐', 3), ('⭐⭐⭐⭐', 4), ('⭐⭐⭐⭐⭐', 5)])
    submit = SubmitField('Post')

