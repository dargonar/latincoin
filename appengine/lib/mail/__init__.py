# -*- coding: utf-8 -*-

import logging
from google.appengine.ext import db

from config import config
from models import MailTemplate, JinjaTemplate

def init_mails():
  # ----------------------------------------------------------------------------------  
  # partial templates ----------------------------------------------------------------  
    
  # ----------------------------------------------------------------------------------  
  # account_information_es
  name = 'account_information_es'
  template_txt = """
    <div class="well" style="font-size:16px;">
      <address>
        <i>Beneficiario:</i><br />
        <strong>Diventi SRL.</strong><br />
        Avda. Mosconi 3223 Piso 7 Oficina C, CABA<br />
        Argentina, CP 1419<br />
      </address>
      <address>
        <i>CUIT:</i><br />
        <strong>30-71041292-4</strong><br />
      </address>
      <address>
        <i>Número de cuenta:</i><br />
        <strong>097-9977/8</strong><br />
      </address>
      <address>
        <i>Tipo de cuenta:</i><br />
        <strong>Cuenta corriente en pesos</strong><br />
      </address>
      <address>
        <i>Banco:</i><br />
        <strong>Banco Santander Río SA.</strong><br />
      </address>
      <h4>Para transferencia bancaria 24hs.</h4>
      <address>
        <i>CBU:</i><br />
        <strong>0720097720000000997786</strong><br />
      </address>
    </div>
  """.decode('utf-8')
  
  jinja_template = JinjaTemplate(key_name=name
                                              , name      = name
                                              , language  = 'es'
                                              , source    = template_txt)
  jinja_template.put()
                            
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
  
  jinja_template = JinjaTemplate(key_name=name
                                              , name      = name
                                              , language  = 'es'
                                              , source    = template_txt)
  jinja_template.put()
  
  # ----------------------------------------------------------------------------------  
  # bank_account_es
  name = 'bank_account_es'
  template_txt = """
    ID:           #{{bank_account.key().id()|string}}
    CBU:          {{bank_account.cbu}}
    Descripción:  {{bank_account.description}}
    Fecha:        {{bank_account.created_at.strftime("%Y-%m-%d %H:%M:%S")}}
    --    
  """.decode('utf-8')
  
  jinja_template = JinjaTemplate(key_name=name
                                              , name      = name
                                              , language  = 'es'
                                              , source    = template_txt)
  jinja_template.put()
  
  # ----------------------------------------------------------------------------------  
  # trade_order_es
  name = 'trade_order_es'
  template_txt = """
    
    Orden de {{'compra' if order.is_bid() else 'venta'}}
    -------------------

    ID:         #{{order.key().id()|string}}
    Fecha:      {{order.created_at.strftime("%Y-%m-%d %H:%M:%S")}}
    Pesos/BTC:  ${{'%0.2f'|format(order.ppc|float)}}
    BTC:        {{'%0.5f'|format(order.amount|float)}}
    Total:      ${{'%0.2f'|format((order.ppc*order.amount)|float)}}
    --    
  """.decode('utf-8')
  
  jinja_template = JinjaTemplate(key_name=name
                                              , name      = name
                                              , language  = 'es'
                                              , source    = template_txt)
  jinja_template.put()
  
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
  
  jinja_template = JinjaTemplate(key_name=name
                                              , name      = name
                                              , language  = 'es'
                                              , source    = template_txt)
  jinja_template.put()
  
  # ----------------------------------------------------------------------------------  
  # oper_list_es
  name = 'oper_list_es'
  template_txt = """
    {% for oper in opers %}
      {% include "oper_es" %}
    {% endfor %}
  """.decode('utf-8')
  
  jinja_template = JinjaTemplate(key_name=name
                                                , name  = name
                                                , language  = 'es'
                                                , source    = template_txt)
  jinja_template.put()
  
  # ----------------------------------------------------------------------------------  
  # signature_es
  name = 'signature_es'
  template_txt = """
  
  Saludos cordiales,
  El equipo de LatinCoin.com
  info@latincoin.com
  https://latincoin.com/
  """.decode('utf-8')
  
  jinja_template = JinjaTemplate(key_name=name
                                              , name      = name
                                              , language  = 'es'
                                              , source    = template_txt)
  jinja_template.put()
  
  # ----------------------------------------------------------------------------------  
  name = 'money_inout_operation_es'
  template_txt = """
    ID:         #{{account_operation.key().id()|string}}
    Fecha:      {{account_operation.updated_at.strftime("%Y-%m-%d %H:%M:%S")}}
    Monto:      {{account_operation.format()}}
    --    
  """.decode('utf-8')
  
  jinja_template = JinjaTemplate(key_name=name
                                              , name      = name
                                              , language  = 'es'
                                              , source    = template_txt)
  jinja_template.put()
  
  
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
  

  subject = """[LatinCoin] Confirmación de creación de cuenta""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name=name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
  
  # ----------------------------------------------------------------------------------
  # cambió password
  
  name = 'password_changed_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  Le recordamos que ha modifcado su contraseña.
  
  {% include "signature_es" %}
  """.decode('utf-8')
  

  subject = """[LatinCoin] Modificación de contraseña""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
  
  
  # ----------------------------------------------------------------------------------
  # forgot password
  name = 'forgot_password_es'
  template_txt = """
  Estimado {{user_name}},
  
  Ha solicitado crear una nueva contraseña.
  Por favor siga el siguiente enlace para elegir una nueva contraseña:
  {{reset_link}}
  
  Si usted no ha solicitado este pedido, por favor ignore este email.
  
  {% include "signature_es" %}
  """.decode('utf-8')
  
  

  subject = """[LatinCoin] Solicitud de modificación su contraseña""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                                        , name  = name
                                        , language  = 'es'
                                        , subject   = subject
                                        , body_txt  = template_txt)
  mail_template.put()
  
  # ----------------------------------------------------------------------------------
  # creó orden de compra
  name = 'new_order_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  Usted ha creado una nueva orden de {{'compra' if order.is_bid() else 'venta'}}.

  {% include "trade_order_es" %}
    
  {% include "signature_es" %}
  """.decode('utf-8')
  
  

  subject = """[LatinCoin] Nueva orden de {{'compra' if order.is_bid() else 'venta'}} #{{order.key().id()|string}}""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                                        , name  = name
                                        , language  = 'es'
                                        , subject   = subject
                                        , body_txt  = template_txt)
  mail_template.put()  
  # ----------------------------------------------------------------------------------
  # canceló orden
  name = 'cancel_order_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  Usted ha cancelado una orden de {{'compra' if order.is_bid() else 'venta'}}.

  {% include "trade_order_es" %}
  
  {% include "signature_es" %}
  """.decode('utf-8')

  

  subject = """[LatinCoin] Cancelación de orden de {{'compra' if order.is_bid() else 'venta'}} #{{order.key().id()|string}}""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
  
  # ----------------------------------------------------------------------------------
  # se completo parcialmente una orden
  name = 'partially_completed_order_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  Se ha producido actividad en su cuenta LatinCoin.

  A continuación se detalla un resumen de sus operaciones recientes.
  
  {% include "trade_order_es" %}
  
  Operación(es):
  
  {% include "oper_list_es" %}
    
  {% include "signature_es" %}
  """.decode('utf-8')


  subject = """[LatinCoin] Orden de {{'compra' if order.is_bid() else 'venta'}} #{{order.key().id()|string}} parcialmente completada""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
  
  # ----------------------------------------------------------------------------------
  # se completo una orden
  name = 'completed_order_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  Se ha producido actividad en su cuenta LatinCoin.
  
  La orden de {{'compra' if order.is_bid() else 'venta'}} se ha completado.
  
  {% include "trade_order_es" %}
    
  {% include "signature_es" %}
  """.decode('utf-8')
  

  subject = """[LatinCoin] Orden de {{'compra' if order.is_bid() else 'venta'}} #{{order.key().id()|string}} completada""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
  
  # ----------------------------------------------------------------------------------
  # se acreditaron ars
  name = 'deposit_received_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  Se han acreditado {{account_operation.format()}} en su cuenta. 
    
  {% include "signature_es" %}
  """.decode('utf-8')


  subject = """[LatinCoin] Se han acreditado fondos a su cuenta #{{account_operation.key().id()|string}}""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
    
  # ----------------------------------------------------------------------------------
  # solicitud de retiro de fondos
  name = 'withdraw_request_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  Usted ha solicitado un retiro de fondos.
  
  Detalle de la solicitud: 
  
  {% include "money_inout_operation_es" %}

  El pedido sera procesado el próximo dia habil.
    
  {% include "signature_es" %}
  """.decode('utf-8')
  

  subject = """[LatinCoin] Solicitud de retiro de fondos #{{account_operation.key().id()|string}}""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
  
  
  # ----------------------------------------------------------------------------------
  # cancela solicitud de retiro
  name = 'cancel_withdraw_request_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  Ha cancelado una solicitud de retiro de fondos.
  
  Detalle de la solicitud cancelada: 
  
  {% include "money_inout_operation_es" %}
  
  {% include "signature_es" %}
  """.decode('utf-8')
  

  subject = """[LatinCoin] Solicitud de retiro de fondos #{{account_operation.key().id()|string}} cancelada""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
    
  # ----------------------------------------------------------------------------------
  # solicitud de retiro aceptada
  name = 'accept_withdraw_request_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  Su solicitud de retiro de ha sido aceptada.
  
  Detalle de la solicitud: 
  
  {% include "money_inout_operation_es" %}
  
  {% include "signature_es" %}
  """.decode('utf-8')

  

  subject = """[LatinCoin] Solicitud de retiro de fondos #{{account_operation.key().id()|string}} aceptada""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
  
  # ----------------------------------------------------------------------------------
  # solicitud de retiro de pesos aceptada
  name = 'done_withdraw_request_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
    
  Se han enviado los fondos requeridos a la cuenta destino.
  
  Detalle de la operación: 
  
  {% include "money_inout_operation_es" %}
    
  {% include "signature_es" %}
  """.decode('utf-8')

  

  subject = """[LatinCoin] Fondos transferidos #{{account_operation.key().id()|string}}""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
  
  # ----------------------------------------------------------------------------------
  # modificacion de info personal
  name = 'personal_info_changed_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  Su información personal ha sido modificada satisfactoriamente.
  
  {% include "signature_es" %}
  """.decode('utf-8')
  

  subject = """[LatinCoin] Información personal modificada""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
  
  # ----------------------------------------------------------------------------------
  # archivo subido
  name = 'validation_file_uploaded_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  El(Los) archivo(s) para validar su identidad y su domicilio fue(ron) recibido(s) satisfactoriamente.
  
  Será notificado cuando nuestro equipo finalice la verificación.
  
  {% include "signature_es" %}
  """.decode('utf-8')
  

  subject = """[LatinCoin] Archivo(s) para validar identidad recibido(s)""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
  
  # ----------------------------------------------------------------------------------
  # archivo evaluado
  name = 'validation_file_validated_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  El archivo "{{file.filename}}" ha sido {{'validado' if file.is_valid else 'invalidado'}}.
  {% if file.is_valid == False %}
  
  Motivo de rechazo: {{file.not_valid_reason}}.
  
  {% endif %}
  {% include "signature_es" %}
  """.decode('utf-8')
  
  subject = """[LatinCoin] Archivo para validar identidad evaluado""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
  
  
  # ----------------------------------------------------------------------------------
  # identificación validada
  name = 'identity_validated_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  {% if user.identity_is_validated %}
    Su identidad ha sido validada.
  {% else %}
    Su identidad no ha podido ser validada.
    Por favor revise los correos de evaluación de archivos de validación previamente recibidos.
  {% endif %}
  
  {% include "signature_es" %}
  """.decode('utf-8')
  

  subject = """[LatinCoin] Identificación validada""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
  
  
  # ----------------------------------------------------------------------------------
  # bank_account_added
  name = 'bank_account_added_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  Usted ha {{'modificado' if edit else 'agregado'}} una cuenta bancaria.
  
  Detalle de cuenta:
  {% include "bank_account_es" %}
  
  {% include "signature_es" %}
  """.decode('utf-8')


  subject = """[LatinCoin] {{'Modificación de' if edit else 'Nueva'}} cuenta bancaria ({{bank_account.cbu}})""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
  
  # ----------------------------------------------------------------------------------
  # bank_account_validated
  name = 'bank_account_validated_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  Su cuenta bancaria ha sido validada.
  
  Detalle de cuenta:
  {% include "bank_account_es" %}
  
  {% include "signature_es" %}
  """.decode('utf-8')
  

  subject = """[LatinCoin] Cuenta bancaria ({{bank_account.cbu}}) validada""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
  
  # ----------------------------------------------------------------------------------
  # bank_account_deleted
  name = 'bank_account_deleted_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  Su cuenta bancaria ha sido eliminada.
  
  Detalle de cuenta:
  {% include "bank_account_es" %}
  
  {% include "signature_es" %}
  """.decode('utf-8')
  

  subject = """[LatinCoin] Cuenta bancaria ({{bank_account.cbu}}) eliminada""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
  
  # ----------------------------------------------------------------------------------
  # btc_address_added
  name = 'btc_address_added_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  Usted ha {{'modificado' if edit else 'agregado'}} una dirección de bitcoin.
  
  Detalle de la dirección:
  {% include "user_btc_address_es" %}
  
  {% include "signature_es" %}
  """.decode('utf-8')


  subject = """[LatinCoin] {{'Modificación de' if edit else 'Nueva'}} dirección bitcoin""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()
  
  # ----------------------------------------------------------------------------------
  # bank_account_deleted
  name = 'btc_address_deleted_es'
  template_txt = """
  Estimado {{user_name}},
  
  Este mail no requiere respuesta.
  
  La dirección bitcoin ha sido eliminada.
  
  Detalle de la direccion:
  {% include "user_btc_address_es" %}
  
  {% include "signature_es" %}
  """.decode('utf-8')
  

  subject = """[LatinCoin] Dirección bitcoin eliminada""".decode('utf-8')
  mail_template = MailTemplate(key_name=name
                          , name  = name
                          , language  = 'es'
                          , subject   = subject
                          , body_txt  = template_txt)
  mail_template.put()