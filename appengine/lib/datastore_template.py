# -*- coding: utf-8 -*-

from jinja2 import BaseLoader, TemplateNotFound

from models import JinjaTemplate

class MyJinjaLoader(BaseLoader):

  def __init__(self, path):
    self.path = path

  def get_source(self, environment, template):
    
    # memcacheado
    template = JinjaTemplate.get_by_key_name(template) 
    if not template:
      raise TemplateNotFound(template)
    
    do_reload = False
    
    if template.updated_at != template.last_read:
      template.updated_at = template.last_read
      template.put()
      do_reload = True
    
    return template.source.decode('utf-8'), None, lambda: do_reload

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