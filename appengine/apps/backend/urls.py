# -*- coding: utf-8 -*-
from webapp2 import Route

def get_rules():
    
    rules = [
      Route('/download/eldia'   ,  name='backend/download'        , handler='apps.backend.download.ElDia:download'),
      Route('/download/feed'    ,  name='backend/download_feed'   , handler='apps.backend.download.ElDia:download_feed'),
      Route('/download/article' ,  name='backend/download_article', handler='apps.backend.download.ElDia:download_article'),
      
      Route('/download/ivc'         ,  name='backend/ivc/download'        , handler='apps.backend.download.IVC:download'),
      Route('/download/ivc/feed'    ,  name='backend/ivc/download_feed'   , handler='apps.backend.download.IVC:download_feed'),
      Route('/download/ivc/article' ,  name='backend/ivc/download_article', handler='apps.backend.download.IVC:download_article'),
      
      Route('/check/eldia_gallery'         ,  name='backend/eldia_gallery/download'        , handler='apps.backend.download.ElDiaRSS:download'),
      Route('/check/eldia_gallery/feed'    ,  name='backend/eldia_gallery/download_feed'   , handler='apps.backend.download.ElDiaRSS:download_feed'),
      #Route('/check/eldia_gallery/article' ,  name='backend/eldia_gallery/download_article', handler='apps.backend.download.ElDiaRSS:download_article'),
    ]
    
    return rules
