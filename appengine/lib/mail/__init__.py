# -*- coding: utf-8 -*-

import logging
from google.appengine.ext import db

from config import config
from models import MailTemplate, JinjaTemplate

def init_mails():
    
  # ----------------------------------------------------------------------------------  
  # partial templates ----------------------------------------------------------------  
  
  # ----------------------------------------------------------------------------------  
  # user_btc_address_es
  name = 'user_btc_address_es'
  template_txt = """
    ID:           #{{user_btc_address.key().id()|string}}
    Address:      {{user_btc_address.address}}
    Descripción:  {{user_btc_address.description)}}
    Fecha:        {{user_btc_address.created_at.strftime("%Y-%m-%d %H:%M:%S")}}
    --    
  """.decode('utf-8')
  
  jinja_prt_tpl6 = JinjaTemplate.get_or_insert(name
                                              , name      = name
                                              , language  = 'es'
                                              , source    = template_txt)
  jinja_prt_tpl6.put()
  
  # ----------------------------------------------------------------------------------  
  # bank_account_es
  name = 'bank_account_es'
  template_txt = """
    ID:           #{{bank_account.key().id()|string}}
    CBU:          {{bank_account.cbu}}
    Descripción:  {{bank_account.description)}}
    Fecha:        {{bank_account.created_at.strftime("%Y-%m-%d %H:%M:%S")}}
    --    
  """.decode('utf-8')
  
  jinja_prt_tpl5 = JinjaTemplate.get_or_insert(name
                                              , name      = name
                                              , language  = 'es'
                                              , source    = template_txt)
  jinja_prt_tpl5.put()
  
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
  # money_out_operation //account_operation_es
  name = 'money_inout_operation_es'
  template_txt = """
    ID:         #{{account_operation.key().id()|string}}
    Fecha:      {{account_operation.updated_at.strftime("%Y-%m-%d %H:%M:%S")}}
    Monto en {{'Pesos' if account_operation.currency=='ARS' else 'BTC'}}:  {{'%0.5f'|format(account_operation.amount|float)}}
    {{'Dirección' if account_operation.bank_account is None else 'CBU'}} {{'destino' if account_operation == account_operation.MONEY_OUT else 'origen'}}:      ${{account_operation.address if account_operation.bank_account is None else account_operation.bank_account}}
    --    
  """.decode('utf-8')
  
  jinja_prt_tpl4 = JinjaTemplate.get_or_insert(name
                                              , name      = name
                                              , language  = 'es'
                                              , source    = template_txt)
  jinja_prt_tpl4.put()
  
  
  # ----------------------------------------------------------------------------------  
  # final templates ------------------------------------------------------------------
  
  # ----------------------------------------------------------------------------------  
  # welcome
  name = 'welcome_es'
  template_txt = """
  ¡Bienvenido a LatinCoin!
  
  Gracias por crear su cuenta con nosotros.
  
  Su usuario: {{user_email}}
  
  Con el fin de habilitar su cuenta, tendrá que ingresar la siguiente dirección:
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
  
  Ha solicitado crear una nueva contraseña. Por favor siga el siguiente enlace para elegir una nueva contraseña:
  {{reset_link}}
  
  Si usted no ha solicitado este pedido, por favor ignore este email.
  
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
  
  # ----------------------------------------------------------------------------------
  # cancela solicitud de retiro de pesos
  name = 'cancel_withdraw_request_ars_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Ha cancelado su solicitud de retiro de pesos argentinos.
  
  Detalle de la solicitud cancelada: 
  
  {% include "money_inout_operation_es" %}
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl15 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl13.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Solicitud de retiro de fondos cancelada""".decode('utf-8')
  mail_tpl15 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl15)
  mail_tpl15.put()
  
  # ----------------------------------------------------------------------------------
  # cancela solicitud de retiro de bitcoins
  name = 'cancel_withdraw_request_btc_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Ha cancelado su solicitud de retiro de bitcoins.
  
  Detalle de la solicitud cancelada: 
  
  {% include "money_inout_operation_es" %}
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl16 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl16.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Solicitud de retiro de bitcoins cancelada""".decode('utf-8')
  mail_tpl16 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl16)
  mail_tpl16.put()
  
  # ----------------------------------------------------------------------------------
  # solicitud de retiro de pesos aceptada
  name = 'accept_withdraw_request_ars_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Su solicitud de retiro de pesos argentinos ha sido aceptada.
  
  Detalle de la solicitud: 
  
  {% include "money_inout_operation_es" %}
  
  Los pesos se transferirán a la brevedad en la cuenta indicada.
  
  Gracias por su paciencia.
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl17 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl17.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Solicitud de retiro de fondos aceptada""".decode('utf-8')
  mail_tpl17 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl17)
  mail_tpl17.put()
  
  # ----------------------------------------------------------------------------------
  # solicitud de retiro de bitcoins aceptada
  name = 'accept_withdraw_request_btc_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Su solicitud de retiro de bitcoins ha sido aceptada.
  
  Detalle de la solicitud: 
  
  {% include "money_inout_operation_es" %}
  
  Los bitcoins se transferirán a la brevedad a la dirección indicada.
  
  Gracias por su paciencia.
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl18 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl18.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Solicitud de retiro de bitcoins aceptada""".decode('utf-8')
  mail_tpl18 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl18)
  mail_tpl18.put()
  
  # ----------------------------------------------------------------------------------
  # solicitud de retiro de pesos aceptada
  name = 'done_withdraw_request_ars_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Los pesos argentinos solicitados para retiro fueron enviados a la cuenta destino.
  
  Detalle de la operación: 
  
  {% include "money_inout_operation_es" %}
  
  Los pesos se acreditarán a la brevedad en la cuenta indicada.
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl19 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl19.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Retiro de fondos finalizado""".decode('utf-8')
  mail_tpl19 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl19)
  mail_tpl19.put()
  
  # ----------------------------------------------------------------------------------
  # solicitud de retiro de bitcoins aceptada
  name = 'done_withdraw_request_btc_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Los bitcoins solicitados para retiro fueron enviados a la dirección destino.
  
  Detalle de la operación: 
  
  {% include "money_inout_operation_es" %}
  
  Los bitcoins se acreditarán a la brevedad en la dirección indicada.
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl20 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl20.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Retiro de bitcoins finalizado""".decode('utf-8')
  mail_tpl20 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl20)
  mail_tpl20.put()
  
  # ----------------------------------------------------------------------------------
  # modificacion de info personal
  name = 'personal_info_changed_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Su información personal ha sido modificada satisfactoriamente.
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl21 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl21.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Información personal modificada""".decode('utf-8')
  mail_tpl21 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl21)
  mail_tpl21.put()
  
  # ----------------------------------------------------------------------------------
  # archivo subido
  name = 'validation_file_uploaded_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  El(Los) archivo(s) para validar su identidad y su domicilio fue(ron) recibido(s) satisfactoriamente.
  
  Será notificado cuando nuestro equipo finalice la verificación.
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl22 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl22.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Archivo(s) para validar identidad recibido(s)""".decode('utf-8')
  mail_tpl22 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl22)
  mail_tpl22.put()
  
  # ----------------------------------------------------------------------------------
  # identificación validada
  name = 'identity_validated_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Su identificación ha sido validada.
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl23 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl23.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Identificación validada""".decode('utf-8')
  mail_tpl23 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl23)
  mail_tpl23.put()
  
  
  # ----------------------------------------------------------------------------------
  # identificación no validada
  name = 'identity_not_validated_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Su identificación no ha podido ser validada.
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl24 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl24.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Identificación no validada""".decode('utf-8')
  mail_tpl24 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl24)
  mail_tpl24.put()
  
  # ----------------------------------------------------------------------------------
  # bank_account_added
  name = 'bank_account_added_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Usted ha agregado una cuenta bancaria.
  
  Detalle de cuenta:
  {% bank_account_es %}
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl25 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl25.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Nueva cuenta bancaria""".decode('utf-8')
  mail_tpl25 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl25)
  mail_tpl25.put()
  
  # ----------------------------------------------------------------------------------
  # bank_account_validated
  name = 'bank_account_validated_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Su cuenta bancaria ha sido validada.
  
  Detalle de cuenta:
  {% bank_account_es %}
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl26 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl26.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Cuenta bancaria validada""".decode('utf-8')
  mail_tpl26 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl26)
  mail_tpl26.put()
  
  # ----------------------------------------------------------------------------------
  # bank_account_deleted
  name = 'bank_account_deleted_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Su cuenta bancaria ha sido eliminada.
  
  Detalle de cuenta:
  {% bank_account_es %}
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl27 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl27.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Cuenta bancaria eliminada""".decode('utf-8')
  mail_tpl27 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl27)
  mail_tpl27.put()
  
  # ----------------------------------------------------------------------------------
  # btc_address_added
  name = 'btc_address_added_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  Usted ha agregado una dirección de bitcoin.
  
  Detalle de la dirección:
  {% user_btc_address_es %}
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl28 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl28.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Nueva dirección bitcoin""".decode('utf-8')
  mail_tpl28 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl28)
  mail_tpl28.put()
  
  # ----------------------------------------------------------------------------------
  # bank_account_deleted
  name = 'btc_address_deleted_es'
  template_txt = """
  Estimado {{user_email}},
  
  Este mail no requiere respuesta.
  
  La dirección bitcoin ha sido eliminada.
  
  Detalle de la direccion:
  {% user_btc_address_es %}
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  jinja_tpl29 = JinjaTemplate.get_or_insert( name
                             , name  = name
                             , language  = 'es'
                             , source    = template_txt)
  jinja_tpl29.put()
  
  name = 'mail_' + name
  subject = """[LatinCoin] Dirección bitcoin eliminada""".decode('utf-8')
  mail_tpl29 = MailTemplate.get_or_insert(  name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = jinja_tpl27)
  mail_tpl29.put()
  