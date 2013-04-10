# -*- coding: utf-8 -*-
import re

from config import config

from models import Account
from wtforms import Form, BooleanField, SelectField, TextField, FloatField , PasswordField, FileField, DateField
from wtforms import HiddenField, TextAreaField, IntegerField, validators, ValidationError
from utils import is_valid_cbu, is_valid_bitcoin_address

class UserBitcoinAddressForm(Form):

  def validate_address(self, field):
    if not is_valid_bitcoin_address(field.data):
      raise ValidationError(u'La dirección es invalida.')
  
  address     = TextField(u'', [validators.Required(message=u'Debe ingresar una dirección.')] )
  description = TextField(u'', [validators.Required(message=u'Debe ingresar una descripción.'), 
                                validators.Length(message='La descripción no puede superar los %(max)d caracteres.', max=100),
                                validators.Regexp(message='La descripción solo puede contener letras y numeros.', regex='\w')
                                ])
  key         = HiddenField()

class BankAccountForm(Form):

  def validate_cbu(self, field):
    if not is_valid_cbu(field.data):
      raise ValidationError(u'El CBU es invalido.')
  
  cbu         = TextField(u'', [validators.Required(message=u'Debe ingresar un CBU.')] )
  description = TextField(u'', [validators.Required(message=u'Debe ingresar una descripción.'), 
                                validators.Length(message='La descripción no puede superar los %(max)d caracteres.', max=100),
                                validators.Regexp(message='La descripción solo puede contener letras y numeros.', regex='\w')
                                ])
  key         = HiddenField()

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
  
  def validate_cuit(self, field):
    value = field.data.strip()
    if re.match(r"^[0-9]{2}-[0-9]{8}-[0-9]$", value) is None:
      raise ValidationError(u'El CUIL/CUIT no es válido.')
  
  def update_object(self, obj):
    obj.name         = self.name.data
    obj.email        = self.email.data
    obj.last_name    = self.last_name.data
    obj.telephone    = self.telephone.data
    obj.cuit         = self.cuit.data
    return obj
  
  email               = TextField('E-mail',[validators.email(message=u'Debe ingresar un correo válido.')], default='')
  name                = TextField(u'Nombre')
  last_name           = TextField(u'Apellido')
  telephone           = TextField(u'Teléfono')
  cuit                = TextField(u'CUIT/CUIL')
  
class ChangePasswordForm(Form):
  def __repr__(self):
    return 'ChangePasswordForm'

  def update_object(self, obj):
    obj.password                  = self.new_password.data
    return obj
    
  password            = PasswordField(u'Contraseña', [
                            validators.Required(message=u'Debe ingresar la contraseña actual.'),
                        ])
  new_password        = PasswordField('Nueva contraseña', [
                            validators.Length(message=u'La contraseña debe tener al menos %(min)d caracteres.', min=6),
                            validators.Required(message=u'Debe ingresar una contraseña.'),
                            validators.EqualTo('confirm', message=u'Las contraseñas deben ser iguales.')
                        ])
  confirm             = PasswordField(u'Repetir nueva contraseña')
