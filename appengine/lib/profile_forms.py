# -*- coding: utf-8 -*-

from config import config

from models import Account
from wtforms import Form, BooleanField, SelectField, TextField, FloatField , PasswordField, FileField, DateField
from wtforms import HiddenField, TextAreaField, IntegerField, validators, ValidationError

class ProfileForm(Form):
  def __repr__(self):
    return 'ProfileForm'

  def validate_email(self, field):
    # Chequeo que el correo sea válido.
    account = Account.all().filter('email =', field.data).get()
    
    if account:
      if str(account.key()) == self.user_key:
        return
      raise ValidationError(u'Este correo ya esta siendo utilizado.')
  
  def update_object(self, obj):
    obj.name         = self.name.data
    obj.email        = self.email.data
    obj.last_name    = self.last_name.data
    obj.telephone    = self.telephone.data
    return obj
  
  email               = TextField('E-mail',[validators.email(message=u'Debe ingresar un correo válido.')], default='')
  name                = TextField(u'Nombre')
  last_name           = TextField(u'Apellido')
  telephone           = TextField(u'Teléfono')
  
class ChangePasswordForm(Form):
  def __repr__(self):
    return 'ChangePasswordForm'

  def update_object(self, obj):
    obj.password     = self.new_password.data
    
  password            = PasswordField(u'Contraseña', [
                            validators.Length(message=u'La contraseña debe tener al menos %(min)d caracteres.', min=6),
                            validators.Required(message=u'Debe ingresar una contraseña.'),
                            validators.EqualTo('confirm', message=u'Las contraseñas deben ser iguales.')
                        ])
  
  confirm             = PasswordField(u'Repetir Contraseña')
  new_password        = PasswordField('Nuevo Password', [validators.Required(message=u'Debe ingresar una contraseña.')])
  
