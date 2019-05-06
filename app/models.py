from app import db
from datetime import datetime


tablica_povezivanja=db.Table('tablica_povezivanja',
    db.Column('izlet_id', db.Integer, db.ForeignKey('izlet.id')),
    db.Column('user_id',db.Integer, db.ForeignKey('user.id'))
    )

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64), index=True, unique=True)
    email=db.Column(db.String(120), index=True, unique=True)
    password_hash=db.Column(db.String(128))
    ime=db.Column(db.String(50))
    prezime=db.Column(db.String(64))
    datum_rodjenja=db.Column(db.Date, nullable=True)
    broj_telefona=db.Column(db.String(20), nullable=True)
    o_meni=db.Column(db.String(400), nullable=True)
    izleti = db.relationship('Izlet', backref='creator', lazy='dynamic')

    def __repr__(self):
        return '<User {}, a moje ime je {}>'.format(self.username, self.ime)




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



