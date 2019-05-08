from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import login
from flask_login import UserMixin


friends=db.Table('friends',
    db.Column('befriender_id',db.Integer,db.ForeignKey('user.id')),
    db.Column('befriended_id',db.Integer,db.ForeignKey('user.id'))
    )



tablica_povezivanja=db.Table('tablica_povezivanja',
    db.Column('izlet_id', db.Integer, db.ForeignKey('izlet.id')),
    db.Column('user_id',db.Integer, db.ForeignKey('user.id'))
    )

class User(UserMixin, db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64), index=True, unique=True)
    email=db.Column(db.String(120), index=True, unique=True)
    password_hash=db.Column(db.String(128))
    ime=db.Column(db.String(50))
    prezime=db.Column(db.String(64))
    datum_rodjenja=db.Column(db.Date, nullable=True)
    broj_telefona=db.Column(db.String(20), nullable=True)
    o_meni=db.Column(db.String(400), nullable=True)
    profilna_slika=db.Column(db.String(300), nullable=True)
    izleti = db.relationship('Izlet', backref='creator', lazy='dynamic')
    befriended=db.relationship(
        'User',secondary=friends,
        primaryjoin=(friends.c.befriender_id==id),
        secondaryjoin=(friends.c.befriended_id==id),
        backref=db.backref('friends',lazy='dynamic'),lazy='dynamic')


    def __repr__(self):
        return '<User {}, a moje ime je {}, i ja imam profilnu naziva {}.>'.format(self.username, self.ime,self.profilna_slika)

    def set_password(self,password):
        self.password_hash=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    def befriend(self, user):
        if not self.is_friends(user):
            self.befriended.append(user)

    def unfriend(self, user):
        if self.is_friends(user):
            self.befriended.remove(user)

    def is_friends(self, user):
        return self.befriended.filter(
            friends.c.befriended_id == user.id).count() > 0

    def izleti_prijatelja(self): #uključuje moje izlete, izlete od befriendera, i izlete befriendeda
        i_befriended=Izlet.query.join(friends,(friends.c.befriended_id==Izlet.creator_id)).filter(friends.c.befriender_id==self.id)
        own=Izlet.query.filter_by(creator_id=self.id)
        prvi_dio=i_befriended.union(own)
        befriended_me=Izlet.query.join(friends,(friends.c.befriended_id==self.id)).filter(friends.c.befriender_id==Izlet.creator_id)
        return prvi_dio.union(befriended_me).order_by(Izlet.timestamp.desc())

    #def moji_prijatelji(self):
        #prijatelji=User.query.filter(friends.c.befriender_id==self.id)
        #prijatelji2=User.query.filter(friends.c.befriender_id==self.id)
        #return prijatelji
    
        

class Izlet(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    naziv=db.Column(db.String(100),index=True)
    cijena=db.Column(db.Float,nullable=True)
    lokacija=db.Column(db.String(100),nullable=True)
    datum_polaska=db.Column(db.DateTime,nullable=True)
    datum_povratka=db.Column(db.DateTime,nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    opis=db.Column(db.String(500), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    sudionici=db.relationship("User", secondary=tablica_povezivanja)

    def __repr__(self):
        return '<Izlet {}>'.format(self.naziv)



@login.user_loader
def load_user(id):
    return User.query.get(int(id))


