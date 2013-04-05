# -*- coding: utf-8 -*-

import decimal
import copy
import pickle

from google.appengine.ext import db

class DecimalProperty(db.Property):
  """Stores a decimal value."""
  data_type = decimal.Decimal

  def get_value_for_datastore(self, model_instance):
  	return str(super(DecimalProperty, self).get_value_for_datastore(
    	model_instance))

  def make_value_from_datastore(self, value):
    return decimal.Decimal(value)

  def validate(self, value):
    
    value = super(DecimalProperty, self).validate(str(value))

    if value is None or isinstance(value, decimal.Decimal):
      return value
    elif isinstance(value, basestring):
      return decimal.Decimal(value)
    
    raise db.BadValueError("Property %s must be a Decimal or string" % self.name)


class PickleProperty(db.Property):
  """A property for storing complex objects in the datastore in pickled form.

  Example usage:

  >>> class PickleModel(db.Model):
  ...   data = PickleProperty()

  >>> model = PickleModel()
  >>> model.data = {"foo": "bar"}
  >>> model.data
  {'foo': 'bar'}
  >>> model.put() # doctest: +ELLIPSIS
  datastore_types.Key.from_path(u'PickleModel', ...)

  >>> model2 = PickleModel.all().get()
  >>> model2.data
  {'foo': 'bar'}
  """

  data_type = db.Blob

  def get_value_for_datastore(self, model_instance):
    value = self.__get__(model_instance, model_instance.__class__)
    if value is not None:
      return db.Blob(pickle.dumps(value).encode('zlib'))

  def make_value_from_datastore(self, value):
    if value is not None:
      return pickle.loads(str(value).decode('zlib'))

  def default_value(self):
    """If possible, copy the value passed in the default= keyword argument.
    This prevents mutable objects such as dictionaries from being shared across
    instances."""
    return copy.copy(self.default)