from flask import Flask, render_template, url_for, flash, redirect, abort
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user
from form import RegisterForm, LoginForm, AddCafes, CommentAndRating
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from functools import wraps


date = datetime.now().year
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cafes.db"

bootstrap = Bootstrap5(app)

db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(Users, user_id)


def admin_only(func):
    @wraps(func)
    def decorated_function(*arg, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return func(*arg, **kwargs)

    return decorated_function


class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    comment_id = relationship('CommentRate', back_populates='admin_id')


class CafeDetails(db.Model):
    __tablename__ = "cafes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    map = db.Column(db.String(250), nullable=False)
    wifi = db.Column(db.String(10))
    socket = db.Column(db.String(10))
    toilet = db.Column(db.String(10))
    price = db.Column(db.String(100))
    timing = db.Column(db.String(100))
    id_comment = relationship('CommentRate', back_populates='id_cafe')


class CommentRate(db.Model):
    __tablename__ = "opinion"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    cafe_id = db.Column(db.Integer, db.ForeignKey('cafes.id'))
    comment = db.Column(db.Text)
    ratings = db.Column(db.String(10), nullable=False)
    admin_id = relationship('Users', back_populates='comment_id')
    id_cafe = relationship('CafeDetails', back_populates='id_comment')


if not os.path.exists('cafes.db'):
    with app.app_context():
        db.create_all()


@app.route('/')
def home():
    all_cafes = db.session.execute(db.select(CafeDetails)).scalars().all()
    return render_template('home.html', all_cafes=all_cafes, date=date)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_present = db.session.execute(db.select(Users).where(Users.email == form.email.data)).scalar()
        if user_present:
            if check_password_hash(user_present.password, form.password.data):
                login_user(user_present)
                return redirect(url_for('home'))
            else:
                flash('You have entered wrong password. Please enter it again.')
                return redirect(url_for('login'))
        else:
            flash('This email is incorrect. Either you entered your email wrong or you are not a registered user,'
                  '\n Please register! by browsing to register page')
            redirect(url_for('login'))
    return render_template('login.html', form=form, date=date)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        result = db.session.execute(db.select(Users).where(Users.email == form.email.data)).scalar()
        if result:
            flash('You have already registered!!!!\n Please Login')
            return redirect(url_for('login'))
        else:
            new_user = Users(username=form.username.data, email=form.email.data,
                             password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template('register.html', form=form, date=date)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/add_cafes', methods=['POST', 'GET'])
@admin_only
def add_cafes():
    form = AddCafes()
    if form.validate_on_submit():
        new_cafe = CafeDetails(name=form.name.data, image=form.image.data, location=form.location.data, map=form.map.data,
                               wifi=form.wifi.data, socket=form.socket.data, toilet=form.toilet.data, price=form.price.data,
                               timing=form.timing.data)
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_cafes.html', form=form, date=date)


@app.route('/delete/<int:cafe_id>')
@admin_only
def delete_cafe(cafe_id):
    cafe = db.get_or_404(CafeDetails, cafe_id)
    db.session.delete(cafe)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/edit/<int:cafe_id>', methods=['POST', 'GET'])
@admin_only
def edit_cafe(cafe_id):
    cafe = db.get_or_404(CafeDetails, cafe_id)
    form = AddCafes(name=cafe.name, image=cafe.image, location=cafe.location, map=cafe.map, wifi=cafe.wifi,
                    socket=cafe.socket, toilet=cafe.toilet, price=cafe.price, timing=cafe.timing)
    if form.validate_on_submit():
        cafe.name = form.name.data
        cafe.image = form.image.data
        cafe.location = form.location.data
        cafe.map = form.map.data
        cafe.wifi = form.wifi.data
        cafe.socket = form.socket.data
        cafe.toilet = form.toilet.data
        cafe.price = form.price.data
        cafe.timing = form.timing.data
        db.session.commit()
        return redirect(url_for('cafe_details', cafe_id=cafe.id))
    return render_template('add_cafes.html', form=form, is_edit=True, date=date)


@app.route('/cafe/<int:cafe_id>', methods=['POST', 'GET'])
def cafe_details(cafe_id):
    cafe = db.get_or_404(CafeDetails, cafe_id)
    form = CommentAndRating()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You need to be logged in to comment')
            return redirect(url_for('login'))
        else:
            opinion = CommentRate(comment=form.comment.data, ratings=form.ratings.data, admin_id=current_user, id_cafe=cafe)
            db.session.add(opinion)
            db.session.commit()
            form.comment.data = ''
            form.ratings.data = 1
    return render_template('cafe_details.html', date=date, cafe=cafe, form=form)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
