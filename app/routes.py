from app import app
from flask import render_template, flash, redirect, url_for,request
from app.forms import LoginForm
from flask_login import current_user, login_user
from app.models import User
from flask_login import logout_user, login_required
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm
from app.forms import UploadForm
from app import photos
from app.forms import EditProfileForm
from app.models import Profilepicture


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template ('index.html',title='Početna')

@app.route('/login',methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Unijeli ste pogrešno korisničko ime ili lozinku')
            return redirect(url_for('login'))
        login_user(user,remember=form.remember_me.data)
        next_page=request.args.get('next')
        if not next_page or url_parse(next_page).netloc !='':
            next_page=url_for('index')
        return redirect(url_for('index'))
    return render_template('login.html', title='Ulogiraj se',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, ime=form.ime.data, prezime= form.prezime.data,datum_rodjenja=form.datum_rodjenja.data,broj_telefona=form.broj_telefona.data,o_meni=form.o_meni.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    return render_template('user.html', user=user)



@app.route('/upload', methods=['POST'])
def upload():
    file=request.files['inputFile']

    pic=Profilepicture(name=file.filename)

    db.session.add(pic)
    db.session.commit()

    return 'Saved' + file.filename + 'to the db'



@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.ime = form.ime.data
        current_user.prezime = form.prezime.data
        current_user.datum_rodjenja = form.datum_rodjenja.data
        current_user.broj_telefona = form.broj_telefona.data
        current_user.o_meni = form.o_meni.data
        db.session.commit()
        flash('Vaše promijene su spremljene.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.ime.data = current_user.ime
        form.prezime.data = current_user.prezime
        form.datum_rodjenja.data = current_user.datum_rodjenja
        form.broj_telefona.data = current_user.broj_telefona
        form.o_meni.data = current_user.o_meni
    return render_template('edit_profile.html', title='Edit Profile',form=form)


