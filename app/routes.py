from app import app
from flask import render_template, flash, redirect, url_for,request
from app.forms import LoginForm
from flask_login import current_user, login_user
from app.models import User, Izlet
from flask_login import logout_user, login_required
from flask import request
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename 
from app import db
from app.forms import RegistrationForm
from app.forms import EditProfileForm
from app.forms import CreateIzletForm
import os
from flask import Flask, render_template, request
from werkzeug import secure_filename



@app.route('/')
@app.route('/index')
@login_required
def index():
    broj_usera=User.query.count()
    broj_izleta=Izlet.query.count()
    return render_template ('index.html',title='Početna',broj_usera=broj_usera, broj_izleta=broj_izleta)

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
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.ime.data = current_user.ime
        form.prezime.data = current_user.prezime
        form.datum_rodjenja.data = current_user.datum_rodjenja
        form.broj_telefona.data = current_user.broj_telefona
        form.o_meni.data = current_user.o_meni
    return render_template('edit_profile.html', title='Edit Profile',form=form)



@app.route('/upload')
@login_required
def upload():
   return render_template('upload.html')
    
@app.route('/pp', methods = ['GET', 'POST'])
def pp():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
      return 'file uploaded successfully'


#Ovaj dio routova je dedicated za frendove itd
@app.route('/befriend/<username>')
@login_required
def befriend(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.befriend(user)
    user.befriend(current_user)
    db.session.commit()
    flash('You are friends with {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfriend/<username>')
@login_required
def unfriend(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfriend(user)
    user.unfriend(current_user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/prijatelji')
@login_required
def moji_prijatelji():
    frends=current_user.friends
    return render_template('friends.html', title='Home Page',frends=frends)

@app.route('/dodajizlet', methods=['GET', 'POST'])
@login_required
def dodajizlet():
    form = CreateIzletForm()
    if form.validate_on_submit():
        izlet=Izlet(naziv=form.naziv.data, lokacija=form.lokacija.data, opis=form.opis.data, datum_polaska=form.datum_polaska.data, datum_povratka=form.datum_povratka.data, cijena=form.cijena.data, creator_id=current_user.id)
        db.session.add(izlet)
        db.session.commit()
        flash('Kreirali ste novi izlet.')
        return redirect(url_for('index'))    
    return render_template('dodajizlet.html', title='Dodaj izlet',form=form)

