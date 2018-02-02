#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from celery import Celery
import sendgrid
import sendgrid.helpers.mail as sgm
import connvars
import dateutil.parser

app = Celery('tasks', broker='pyamqp://guest@localhost//')

def format_offer(offer, tab='  '):
  msg = ''
  for field_name in offer['response']:
    if offer['response'][field_name]:
      msg += tab + str(field_name) + ': ' + str(offer['response'][field_name]) + '\n'
  return msg

@app.task(ignore_result=True)
def send_mail(to_email_str, offer):
  stat2str = { 'accepted': 'Aceptada', 'ignored': 'Ignorada', 'rejected': 'Rechazada' }
  sg = sendgrid.SendGridAPIClient(apikey=connvars.sendgrid_apikey)
  from_email = sgm.Email("offers-no-reply@chiledevs.com")
  to_email = sgm.Email(to_email_str)
  subject = "Su oferta de trabajo ha sido %s" % stat2str[offer['status']]
  date_str = dateutil.parser.parse(offer['timestamp']).strftime('%d/%m/%Y %H:%M:%S')
  msg = 'Le informamos que su oferta de trabajo publicada el ' + date_str
  msg += ' ha sido '+ stat2str[offer['status']] +'. Usted envió los siguientes datos:\n'
  msg += format_offer(offer)
  msg += '\nSe despide cordialmente,\n\nEquipo de ChileDevs\n\nhola@chiledevs.com\n'
  content = sgm.Content("text/plain", msg)
  mail = sgm.Mail(from_email, subject, to_email, content)
  response = sg.client.mail.send.post(request_body=mail.get())
