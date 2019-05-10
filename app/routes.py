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
from app.forms import CreateIzletForm, EditIzletForm
import os
from flask import Flask, render_template, request
from werkzeug import secure_filename
from sqlalchemy import distinct
from sqlalchemy import func



@app.route('/index')
@login_required
def index():
    broj_usera=User.query.count()
    broj_izleta=Izlet.query.count()
    #broj_jedinstvenih_lokacija=Izlet.query.distinct(Izlet.lokacija).count() Izlet.query.order_by(Izlet.timestamp.desc())
    broj_jedinstvenih_lokacija=Izlet.query.distinct(Izlet.lokacija).group_by(Izlet.lokacija).count()
    #db.s.query(core.Paper.title, func.count(core.Author.id)).join(core.Paper.authors).group_by(core.Paper.id).all()
    popular= db.session.query(Izlet, func.count(User.id)).join(Izlet.sudionici).group_by(Izlet.id).limit(3).all()
    return render_template ('index.html',title='Početna',broj_usera=broj_usera, broj_izleta=broj_izleta, broj_jedinstvenih_lokacija=broj_jedinstvenih_lokacija,popular=popular)

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
    return redirect(url_for('pocetna'))


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
    izleti=Izlet.query.filter(Izlet.creator_id==user.id)
    return render_template('user.html', user=user, izleti=izleti)


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


#Upload i pp sluze za uploadanje slika ua usere
@app.route('/upload')
@login_required
def upload():
   return render_template('upload.html')
    

@app.route('/pp', methods = ['GET', 'POST'])
@login_required
def pp():
    if request.method == 'POST':
        f = request.files['file']
        current_user.profilna_slika=f.filename
        db.session.commit()
        filename=secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('edit_profile'))

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
#Svi korisnici i izleti te moji prijatelji i moji izleti
@app.route('/svi_korisnici')
@login_required
def svi_korisnici():
    page = request.args.get('page', 1, type=int)
    korisnici=User.query.filter(User.id!=current_user.id).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('svi_korisnici', page=korisnici.next_num) if korisnici.has_next else None
    prev_url = url_for('svi_korisnici', page=korisnici.prev_num) if korisnici.has_prev else None
    return render_template('svi_korisnici.html', title='Korisnici',korisnici=korisnici.items,next_url=next_url,prev_url=prev_url)

@app.route('/svi_izleti')
@login_required
def svi_izleti():
    page = request.args.get('page', 1, type=int)
    izleti=Izlet.query.paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('svi_izleti', page=izleti.next_num) if izleti.has_next else None
    prev_url = url_for('svi_izleti', page=izleti.prev_num) if izleti.has_prev else None
    return render_template('svi_izleti.html', title='Izleti',izleti=izleti.items,next_url=next_url,prev_url=prev_url)

@app.route('/moji_izleti')
@login_required
def moji_izleti():
    page = request.args.get('page', 1, type=int)
    izleti=Izlet.query.filter(Izlet.creator_id==current_user.id).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('moji_izleti', page=izleti.next_num) if izleti.has_next else None
    prev_url = url_for('moji_izleti', page=izleti.prev_num) if izleti.has_prev else None
    return render_template('moji_izleti.html', title='Izleti',izleti=izleti.items,next_url=next_url,prev_url=prev_url)

@app.route('/moji_prijatelji')
@login_required
def moji_prijatelji():
    page = request.args.get('page', 1, type=int)
    frends=current_user.friends.paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('moji_prijatelji', page=frends.next_num) if frends.has_next else None
    prev_url = url_for('moji_prijatelji', page=frends.prev_num) if frends.has_prev else None
    return render_template('friends.html', title='Home Page',frends=frends.items)

#Izleti
@app.route('/izlet/<id>')
@login_required
def izlet(id):
    izlet = Izlet.query.filter_by(id=id).first_or_404()

    return render_template('izlet.html', izlet=izlet)


#Upload i pp sluze za uploadanje slika ua izlete
'''@app.route('/upload_izlet_picture')
@login_required
def upload_izlet_picture():
   return render_template('upload_izlet_pic.html')
    
'''
@app.route('/slika_izleta/<id>', methods = ['GET', 'POST'])
@login_required
def slika_izleta(id):
    izlet = Izlet.query.filter_by(id=id).first_or_404()
    if request.method == 'POST':
        f = request.files['slikai']
        izlet.slika_izleta=f.filename
        db.session.commit()
        filename=secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER2'], filename))
        return redirect(url_for('izlet', id=id)) 


#Ovaj dio routova je dedicated za sudionike izleta itd
@app.route('/postani_sudionik/<id>')
@login_required
def postani_sudionik(id):
    izlet = Izlet.query.filter_by(id=id).first()
    if izlet is None:
        flash('Izlet {} not found.'.format(izlet.naziv))
        return redirect(url_for('index'))
    if izlet.creator_id == current_user.id:
        flash('To je tvoj izlet')
        return redirect(url_for('izlet', id=id))
    izlet.postani_sudionik(current_user)
    db.session.commit()
    flash('Ti si sada sudionik {}!'.format(izlet.naziv))
    return redirect(url_for('izlet', id=id))

@app.route('/prestani_sudionik/<id>')
@login_required
def prestani_sudionik(id):
    izlet = Izlet.query.filter_by(id=id).first()
    if izlet is None:
        flash('Izlet {} not found.'.format(izlet.naziv))
        return redirect(url_for('index'))
    if izlet.creator_id == current_user.id:
        flash('Ne možeš se odjaviti sa svoga izleta')
        return redirect(url_for('izlet', id=id))
    izlet.prestani_sudionik(current_user)
    db.session.commit()
    flash('Odjavio si se sa {}.'.format(izlet.naziv))
    return redirect(url_for('izlet', id=id))


@app.route('/delete_izlet/<id>')
@login_required
def delete_izlet(id):
    izlet=Izlet.query.filter_by(id=id).first()
    if izlet is None:
        return redirect(url_for('index'))
    if izlet.creator_id == current_user.id:
        db.session.delete(izlet)
        db.session.commit()
        return redirect(url_for('moji_izleti'))




@app.route('/edit_izlet/<id>', methods=['GET', 'POST'])
@login_required
def edit_izlet(id):
    form = EditIzletForm()
    izlet=Izlet.query.filter_by(id=id).first()

    if form.validate_on_submit():
        izlet.naziv= form.naziv.data
        izlet.lokacija= form.lokacija.data
        izlet.opis = form.opis.data
        izlet.datum_polaska = form.datum_polaska.data
        izlet.datum_povratka = form.datum_povratka.data
        izlet.cijena = form.cijena.data
        db.session.commit()
        flash('Vaše promijene su spremljene.')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.naziv.data = izlet.naziv
        form.lokacija.data = izlet.lokacija
        form.opis.data = izlet.opis
        form.datum_polaska.data = izlet.datum_polaska
        form.datum_povratka.data = izlet.datum_povratka
        form.cijena.data = izlet.cijena
    return render_template('edit_izlet.html', title='Edit Izlet',form=form,id=id)

@app.route('/delete_user/<id>')
@login_required
def delete_user(id):
    user=User.query.filter_by(id=id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('deleted'))

@app.route('/delete_user')
def deleted():
    return render_template('deleted.html')

@app.route('/')
@app.route('/pocetna')
def pocetna():
    broj_usera=User.query.count()
    broj_izleta=Izlet.query.count()
    #broj_jedinstvenih_lokacija=Izlet.query.distinct(Izlet.lokacija).count() Izlet.query.order_by(Izlet.timestamp.desc())
    broj_jedinstvenih_lokacija=Izlet.query.distinct(Izlet.lokacija).group_by(Izlet.lokacija).count()
    #db.s.query(core.Paper.title, func.count(core.Author.id)).join(core.Paper.authors).group_by(core.Paper.id).all()
    popular= db.session.query(Izlet, func.count(User.id)).join(Izlet.sudionici).group_by(Izlet.id).limit(3).all()
    return render_template ('pocetna.html',title='Početna',broj_usera=broj_usera, broj_izleta=broj_izleta, broj_jedinstvenih_lokacija=broj_jedinstvenih_lokacija,popular=popular)
    