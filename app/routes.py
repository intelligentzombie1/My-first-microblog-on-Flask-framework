from app import app
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User
from app import db
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Aisha'}
    posts = [
        {
            "author": {'username': 'Aisha'},
            "body": "You guys need eat too much eba!"
        },
        {
            "author": {'username': 'Bolaji'},
            "body": 'I kuku watch game of thrones and I am fine yet.'
        },
    ]
    return render_template('index.html', title='Home Page', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect (url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page= url_for('index')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign in', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/registration', methods=['GET','POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user=User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you have successfully registered!')
        return redirect(url_for('login'))
    return render_template('registration.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()#first is used when we expecting only one variation
    posts=[
        {'author':user, 'body': 'I am a new user'},
        {'author': user, 'body': 'I love to blog'}
    ]
    return render_template('user.html',user=user, posts=posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile.html', methods=['Get', 'post'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username=form.username.data
        current_user.about_me=form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)
@app.route('/follow/<username>')
@login_required
def follow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('user () not found'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('Please you cannot follow yourself')
        return redirect(url_for('user', username=user))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following {} '.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = user.query.filter_by(username=username).first()
    if user is None:
        flash('user {} not found'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('Please you cannot unfollow yourself')
        return redirect(url_for('user', username=user))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are no longer following {}'.format(username))
    return redirect(url_for('user', username=username))