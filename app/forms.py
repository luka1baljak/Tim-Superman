from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField, FileField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class

from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])
    remember_me=BooleanField('Remember Me')
    submit=SubmitField('Sign In')



class RegistrationForm(FlaskForm):
    ime=StringField('Ime',validators=[DataRequired()])
    prezime=StringField('Prezime',validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password=PasswordField('Lozinka',validators=[DataRequired()])
    password2=PasswordField('Ponovi lozinku',validators=[DataRequired(),EqualTo('password')])
    datum_rodjenja=DateField('Datum rođenja',format='%d/%m/%Y')
    broj_telefona=StringField('Broj telefona')
    o_meni=TextAreaField('O meni')
    submit=SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username se vec koristi. Molimo unesite drugi username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email se vec koristi. Molimo unesite drugi email.')



class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    ime = StringField('Ime', validators=[DataRequired()])
    prezime = StringField('Prezime', validators=[DataRequired()])
    datum_rodjenja=DateField('Datum rođenja',format='%d/%m/%Y')
    broj_telefona=StringField('Broj telefona')
    o_meni=TextAreaField('O meni',validators=[Length(min=0, max=399)])
    submit=SubmitField('Save')

class CreateIzletForm(FlaskForm):
    naziv = StringField('Naziv izleta', validators=[DataRequired()])
    lokacija = StringField('Destinacija', validators=[DataRequired()])
    opis=TextAreaField('Opis izleta', validators=[DataRequired(),Length(min=0, max=500)])
    datum_polaska=DateField('Datum polaska',id='datepick', format='%d/%m/%Y')
    datum_povratka=DateField('Datum povratka', format='%d/%m/%Y')
    cijena=DecimalField('cijena', places=2)
    submit=SubmitField('Kreiraj izlet')

class ProfilePictureForm(FlaskForm):
    url=FileField('url')
    submit=SubmitField('Upload picture')