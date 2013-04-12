# -*- coding: utf-8 -*-
import logging
from google.appengine.ext import db

from config import config
from models import MailTemplate, JinjaTemplate

def init_mails():
    
  # ----------------------------------------------------------------------------------  
  # partial templates ----------------------------------------------------------------  
  # ----------------------------------------------------------------------------------  
  # trade_order_es
  name = 'trade_order_es'
  template_txt = """
    ID:         #{{order.key().id()|string}}
    Fecha:      {{order.created_at.strftime("%Y-%m-%d %H:%M:%S")}}
    Pesos/BTC:  ${{'%0.2f'|format(order.ppc|float)}}
    BTC:        {{'%0.5f'|format(order.amount|float)}}
    Total:      ${{'%0.2f'|format((order.ppc*order.amount)|float)}}
    --    
  """.decode('utf-8')
  
  jinja_prt_tpl1 = JinjaTemplate.get_or_insert(name
                                              , name      = name
                                              , language  = 'es'
                                              , source    = template_txt)
  jinja_prt_tpl1.put()
  
  # ----------------------------------------------------------------------------------  
  # oper_es
  name = 'oper_es'
  template_txt = """
    ID:         #{{oper.key().id()|string}}
    Fecha:      {{oper.created_at.strftime("%Y-%m-%d %H:%M:%S")}}
    Pesos/BTC:  ${{'%0.2f'|format(oper.ppc|float)}}
    BTC:        {{'%0.5f'|format(oper.traded_btc|float)}}
    Total:      ${{'%0.2f'|format((oper.ppc*oper.traded_btc)|float)}}
    --
  """.decode('utf-8')
  
  jinja_prt_tpl1_1 = JinjaTemplate.get_or_insert(name
                                              , name      = name
                                              , language  = 'es'
                                              , source    = template_txt)
  jinja_prt_tpl1_1.put()
  
  # ----------------------------------------------------------------------------------  
  # oper_list_es
  name = 'oper_list_es'
  template_txt = """
    {% for oper in opers %}
      {% include "oper_es" %}
    {% endfor %}
  """.decode('utf-8')
  
  jinja_prt_tpl2 = JinjaTemplate.get_or_insert(  name
                                                , name  = name
                                                , language  = 'es'
                                                , source    = template_txt)
  jinja_prt_tpl2.put()
  
  # ----------------------------------------------------------------------------------  
  # signature_es
  name = 'signature_es'
  template_txt = """
  
  Saludos cordiales,
  El equipo de LatinCoin.com
  info@latincoin.com
  https://latincoin.com/
  """.decode('utf-8')
  
  jinja_prt_tpl3 = JinjaTemplate.get_or_insert(name
                                              , name      = name
                                              , language  = 'es'
                                              , source    = template_txt)
  jinja_prt_tpl3.put()
  
  # ----------------------------------------------------------------------------------  
  # welcome
  name = 'welcome_es'
  template_txt = """
  ¡Bienvenido a LatinCoin!
  
  Gracias por crear su cuenta con nosotros.
  
  Su usuario: {{user_email}}
  
  Con el fin de habilitar su cuenta, tendrá que ingresar la siguiente dirección o copiarla en su navegador:
  {{confirm_link}}
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl0 = JinjaTemplate.get_or_insert(  name
                             , name      = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl0.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Confirmación de creación de cuenta""".decode('utf-8')
  mail_tpl0 = MailTemplate.get_or_insert(name
                          , name=name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl0)
  mail_tpl0.put()
  
  # ----------------------------------------------------------------------------------
  # cambió password
  
  name = 'password_changed_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  Le recordamos que ha modifcado su contraseña.
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl1 = JinjaTemplate.get_or_insert( name
                             , name      = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl1.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Modificación de contraseña""".decode('utf-8')
  mail_tpl1 = MailTemplate.get_or_insert(name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl1)
  mail_tpl1.put()
  
  
  # ----------------------------------------------------------------------------------
  # forgot password
  name = 'forgot_password_es'
  template_txt = """
  Estimado {{user_email}},
  
  Ha solicitado modificar su contraseña. Por favor siga el siguiente enlace para elegir una nueva contraseña:
  {{reset_link}}
  
  Si usted no ha solicitado recuperación alguna, por favor siga el siguiente enlace:
  {{cancel_reset_link}}
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl2 = JinjaTemplate.get_or_insert(  name
                                           , name  = name
                                           , language  = 'es'
                                           , source    = template_txt)
  jinja_tpl2.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Solicitud de modificación su contraseña""".decode('utf-8')
  mail_tpl2 = MailTemplate.get_or_insert(name
                                        , name  = name
                                        , language  = 'es'
                                                      , subject   = subject
                                        , body_txt  = jinja_tpl2)
  mail_tpl2.put()
  
  # ----------------------------------------------------------------------------------
  # creó orden de compra
  name = 'new_bid_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Usted ha creado una orden de compra de bitcoins.

  Detalle de la orden de compra (Bid)
  
  {% include "trade_order_es" %}
  
  Buenas compras!
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  
  jinja_tpl3 = JinjaTemplate.get_or_insert(name
                                           , name       = name
                                           , language   = 'es'
                                           , source     = template_txt)
  jinja_tpl3.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Nueva orden de compra""".decode('utf-8')
  mail_tpl3 = MailTemplate.get_or_insert(name
                                        , name  = name
                                        , language  = 'es'
                                                      , subject   = subject
                                        , body_txt  = jinja_tpl3)
  mail_tpl3.put()
  
  # ----------------------------------------------------------------------------------
  # creó orden de venta
  name = 'new_ask_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Usted ha creado una orden de venta de bitcoins.

  Detalle de la orden de venta (Ask)
  
  {% include "trade_order_es" %}
  
  Buenas ventas!
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  
  jinja_tpl4 = JinjaTemplate.get_or_insert(  name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl4.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Nueva orden de venta""".decode('utf-8')
  mail_tpl4 = MailTemplate.get_or_insert(name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl4)
  mail_tpl4.put()
  
  # ----------------------------------------------------------------------------------
  # canceló orden de compra
  name = 'cancel_bid_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Usted ha cancelado una orden de compra de bitcoins.

  Detalle de la orden de compra (Bid)
  
  {% include "trade_order_es" %}
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  
  jinja_tpl5 = JinjaTemplate.get_or_insert( name
                                         , name  = name
                                         , language  = 'es'
                                         , source    = template_txt)
  jinja_tpl5.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Cancelación de orden de compra""".decode('utf-8')
  mail_tpl5 = MailTemplate.get_or_insert(name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl5)
  mail_tpl5.put()
  
  # ----------------------------------------------------------------------------------
  # canceló orden de venta
  name = 'cancel_ask_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Usted ha cancelado una orden de venta de bitcoins.

  Detalle de la orden de venta (Ask)
  
  {% include "trade_order_es" %}
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl6 = JinjaTemplate.get_or_insert(  name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl6.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Cancelación de orden de venta""".decode('utf-8')
  mail_tpl6 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl6)
  mail_tpl6.put()
  
  # ----------------------------------------------------------------------------------
  # se completo parcialmente una orden de compra
  name = 'partially_completed_bid_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Se ha producido actividad en su cuenta LatinCoin.

  A continuación se detalla un resumen de sus operaciones recientes.
  
  Detalle de la orden de compra (Bid)
  
  {% include "trade_order_es" %}
  
  Operación(es):
  
  {% include "oper_list_es" %}
  
  Buenas compras!
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl7 = JinjaTemplate.get_or_insert(  name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl7.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Orden de compra parcialmente completada""".decode('utf-8')
  mail_tpl7 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl7)
  mail_tpl7.put()
  
  # ----------------------------------------------------------------------------------
  # se completo parcialmente una orden de venta
  name = 'partially_completed_ask_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Se ha producido actividad en su cuenta LatinCoin.

  A continuación se detalla un resumen de sus operaciones recientes.
  
  Detalle de la orden de venta (Ask)
  
  {% include "trade_order_es" %}
  
  Operación(es):
  
  {% include "oper_list_es" %}
  
  Buenas ventas!
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl8 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl8.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Orden de venta parcialmente completada""".decode('utf-8')
  mail_tpl8 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl8)
  mail_tpl8.put()
  
  # ----------------------------------------------------------------------------------
  # se completo una orden de compra
  name = 'completed_bid_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Se ha producido actividad en su cuenta LatinCoin.

  A continuación se detalla un resumen de sus operaciones recientes.
  
  Detalle de la orden de compra (Bid)
  
  {% include "trade_order_es" %}
  
  Operación(es):
  
  {% include "oper_list_es" %}
  
  Buenas compras!
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl9 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl9.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Orden de compra completada""".decode('utf-8')
  mail_tpl9 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl9)
  mail_tpl9.put()
  
  # ----------------------------------------------------------------------------------
  # se completo una orden de venta
  name = 'completed_ask_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Se ha producido actividad en su cuenta LatinCoin.

  A continuación se detalla un resumen de sus operaciones recientes.
  
  Detalle de la orden de venta (Ask)
  
  {% include "trade_order_es" %}
  
  Operación(es):
  
  {% include "oper_list_es" %}
  
  Buenas ventas!
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl10 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl10.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Orden de compra completada""".decode('utf-8')
  mail_tpl10 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl10)
  mail_tpl10.put()
  
  # ----------------------------------------------------------------------------------
  # se acreditaron ars
  name = 'deposit_received_ars_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Se han acreditado ${{'%0.5f'|format(deposit_amount)}} pesos argentinos en su cuenta LatinCoin. 
  
  Gracias por su paciencia.
  
  Buenas compras!
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl11 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl11.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Sus fondos se han acreditado""".decode('utf-8')
  mail_tpl11 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl11)
  mail_tpl11.put()
  
  # ----------------------------------------------------------------------------------
  # se acreditaron btc
  name = 'deposit_received_btc_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Se han acreditado {{'%0.5f'|format(deposit_amount)}} bitcoins en su cuenta LatinCoin. 
  Gracias por su paciencia.
  
  Buenas ventas!
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl12 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl12.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Sus bitcoins se han acreditado""".decode('utf-8')
  mail_tpl12 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl12)
  mail_tpl12.put()
  
  # ----------------------------------------------------------------------------------
  # solicitud de retiro de pesos
  name = 'withdraw_request_ars_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Ha solicitado un retiro de ${{'%0.5f'|format(withdraw_amount)}} pesos argentinos.
  
  En breve sus fondos se acreditarán en la cuenta cuyo CBU es {{withdraw_cbu}}.
  
  Gracias por su paciencia.
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl13 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl13.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Solicitud de retiro de fondos""".decode('utf-8')
  mail_tpl13 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl13)
  mail_tpl13.put()
  
  # ----------------------------------------------------------------------------------
  # solicitud de retiro de bitcoins
  name = 'withdraw_request_btc_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Ha solicitado un retiro de {{'%0.7f'|format(withdraw_amount)}} bitcoins.
  
  En breve se acreditarán en la dirección {{withdraw_address}}.
  
  Gracias por su paciencia.
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl14 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl14.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Solicitud de retiro de bitcoins""".decode('utf-8')
  mail_tpl14 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl14)
  mail_tpl14.put()
  