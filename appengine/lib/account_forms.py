# -*- coding: utf-8 -*-

from config import config

from models import Account
from wtforms import Form, BooleanField, SelectField, TextField, FloatField , PasswordField, FileField, DateField
from wtforms import HiddenField, TextAreaField, IntegerField, validators, ValidationError

class ResetPasswordForm(Form):
  def __repr__(self):
    return 'ResetPasswordForm'

  password            = PasswordField(u'Contraseña', [
                            validators.Length(message=u'La contraseña debe tener al menos %(min)d caracteres.', min=6),
                            validators.Required(message=u'Debe ingresar una contraseña.'),
                            validators.EqualTo('confirm', message=u'Las contraseñas deben ser iguales.')
                        ])

  confirm             = PasswordField(u'Repetir Contraseña')

class ForgetPasswordForm(Form):
  def __repr__(self):
    return 'ForgetPasswordForm'

  email  = TextField('E-mail',[validators.email(message=u'Debe ingresar un correo válido.')], default='')

class SignUpForm(Form):
  def __repr__(self):
    return 'SignUpForm'

  def validate_accept_terms(self, field):
    if not field.data:
      raise ValidationError(u'Debe aceptar los términos y condiciones.')
      
  def validate_email(self, field):
    # Chequeo que el correo no este repetido
    user = Account.all().filter('email =', field.data).get()

    if user:
      raise ValidationError(u'Ese correo ya esta siendo utilizado.')

  email               = TextField('E-mail',[validators.email(message=u'Debe ingresar un correo válido.')], default='')
  password            = PasswordField(u'Contraseña', [
                            validators.Length(message=u'La contraseña debe tener al menos %(min)d caracteres.', min=6),
                            validators.Required(message=u'Debe ingresar una contraseña.'),
                            validators.EqualTo('confirm', message=u'Las contraseñas deben ser iguales.')
                        ])

  confirm             = PasswordField(u'Repetir Contraseña')
  accept_terms        = BooleanField(u'')
