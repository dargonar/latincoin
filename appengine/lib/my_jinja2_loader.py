# -*- coding: utf-8 -*-

from google.appengine.api import memcache
from google.appengine.ext import db

from jinja2 import BaseLoader, TemplateNotFound
#from os.path import join, exists, getmtime

from models import JinjaTemplate

class MyJinjaLoader(BaseLoader):

  def __init__(self, path):
    self.path = path

  def get_source(self, environment, template):
    
    # memcacheado
    mTemplate = JinjaTemplate.get_by_key_name(template) 
    if mTemplate is None:
      raise TemplateNotFound(template)
    
    do_reload = False
    
    if mTemplate.updated_at != mTemplate.last_read:
      mTemplate.updated_at = mTemplate.last_read
      mTemplate.put()
      do_reload = True
    
    return mTemplate.source.decode('utf-8'), None, lambda: do_reload

def get_template(template):
    
  # memcacheado
  memcache_template_key = 'template_%s'%template
  source = memcache.get(memcache_template_key)
  if source is None:
    mTemplate = JinjaTemplate.get_by_key_name(template) 
    if mTemplate is None:
      raise TemplateNotFound(template)
  
    source = mTemplate.source #.decode('utf-8')
    memcache.add(memcache_template_key, source, 6000)
  return source, None, False