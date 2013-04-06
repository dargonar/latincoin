# -*- coding: utf-8 -*-
import logging
from webapp2 import uri_for as url_for
from datetime import datetime, timedelta

from google.appengine.ext import db

from models import Ticker, Operation
from re import *

_slugify_strip_re = compile(r'[^\w\s-]')
_slugify_hyphenate_re = compile(r'[-\s]+')

def do_slugify(value):
  """
  Normalizes string, converts to lowercase, removes non-alpha characters,
  and converts spaces to hyphens.
  
  From Django's "django/template/defaultfilters.py".
  """
  import unicodedata
  
  if not isinstance(value, unicode):
      value = unicode(value)
  value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
  value = unicode(_slugify_strip_re.sub('', value).strip().lower())
  return _slugify_hyphenate_re.sub('-', value)

def do_marketarrowfy(value):
  if value>0:
    return 'maket_arrow_up'
  if value<0:
    return 'maket_arrow_down'
  return '' #'maket_arrow_even'
  
def do_time_distance_in_words(from_date, since_date = None, target_tz=None, include_seconds=False):
  '''
  Returns the age as a string
  '''
  if since_date is None:
    since_date = datetime.now(target_tz)

  distance_in_time = since_date - from_date
  distance_in_seconds = int(round(abs(distance_in_time.days * 86400 + distance_in_time.seconds)))
  distance_in_minutes = int(round(distance_in_seconds/60))

  if distance_in_minutes <= 1:
    if include_seconds:
      for remainder in [5, 10, 20]:
        if distance_in_seconds < remainder:
          return "menos de %s seconds" % remainder
      if distance_in_seconds < 40:
        return "medio minuto"
      elif distance_in_seconds < 60:
        return "menos de un minuto"
      else:
        return "1 minuto"
    else:
      if distance_in_minutes == 0:
        return "menos de un minuto"
      else:
        return "1 minuto"
  elif distance_in_minutes < 45:
    return "%s minutos" % distance_in_minutes
  elif distance_in_minutes < 90:
    return "cerca de 1 hora"
  elif distance_in_minutes < 1440:
    return "cerca de %d hora" % (round(distance_in_minutes / 60.0))
  elif distance_in_minutes < 2880:
    return "1 d&iacute;a"
  elif distance_in_minutes < 43220:
    return "%d dias" % (round(distance_in_minutes / 1440))
  elif distance_in_minutes < 86400:
    return "cerca de 1 mes"
  elif distance_in_minutes < 525600:
    return "%d meses" % (round(distance_in_minutes / 43200))
  elif distance_in_minutes < 1051200:
    return "cerca de 1 a&ntilde;o"
  else:
    return "mas de %d a&ntilde;os" % (round(distance_in_minutes / 525600))

    