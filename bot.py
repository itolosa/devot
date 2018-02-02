#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from telegram.ext import (Updater, CommandHandler, MessageHandler,
              Filters, CallbackQueryHandler, ConversationHandler)

import pymongo
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram
import logging
import connvars
import pika
import ujson
from bson.objectid import ObjectId
import copy
import mailer


adminchat_set = False
bot = None
admin_chat_id = None
post_chat_id = None

IGNORE_OFFER = 'I'
ACCEPT_OFFER = 'A'
REJECT_OFFER = 'R'

mongocli = pymongo.MongoClient('localhost', 27017)
db = mongocli.devot_database

def build_menu(
  buttons,
  n_cols,
  header_buttons=None,
  footer_buttons=None):
  menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
  if header_buttons:
    menu.insert(0, header_buttons)
  if footer_buttons:
    menu.append(footer_buttons)
  return menu

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
          level=logging.INFO)

log = logging.getLogger(__name__)


def error(bot, update, error):
  """Log Errors caused by Updates."""
  log.warning('Update "%s" caused error "%s"', update, error)

def set_post_chat_callback(bot, update):
  global post_chat_id
  post_chat_id = update.message.chat_id
  update.message.reply_text('post_chat_id updated!')

def set_admin_chat_callback(bot, update, args):
  global admin_chat_id
  global adminchat_set
  if not adminchat_set and len(args) > 0 and args[0] == connvars.secret_passwd:
    adminchat_set = True
    admin_chat_id = update.message.chat_id
    update.message.reply_text('✅ admin_chat_id updated!')
  else:
    update.message.reply_text('❌ Access denied!')

def start_callback(bot, update):
  msg = "Use /shipping to get an invoice for shipping-payment, "
  msg += "or /noshipping for an invoice without shipping."
  update.message.reply_text(msg)

def format_offer(offer, tab='  '):
  msg = ''
  for field_name in offer['response']:
    if offer['response'][field_name]:
      msg += tab + str(field_name) + ': ' + str(offer['response'][field_name]) + '\n'
  return msg

def handle_offer(bot, update):
  query = update.callback_query
  query_data = query.data
  callback_data = ujson.loads(query_data)
  if callback_data['opt'] == ACCEPT_OFFER:
    offer_id = ObjectId(callback_data['oid'])
    job_offer = db.job_offers.update(
      { '_id': offer_id },
      {'$set': {'status': 'accepted'}}
    )

    job_offer = db.job_offers.find_one({ '_id': offer_id })
    to_email = job_offer['response']['Email de respuesta']
    job_offer.pop('_id', None)
    mailer.send_mail.delay(to_email, job_offer)
    msg = '*Oferta de trabajo*\n'
    cleaned_offer = copy.deepcopy(job_offer)
    cleaned_offer['response'].pop('Email de respuesta', None)
    msg += format_offer(cleaned_offer)
    bot.sendMessage(
      chat_id='@canalChileDevs',
      text=msg,
      parse_mode=telegram.ParseMode.MARKDOWN,
      disable_web_page_preview=True
    )
    bot.edit_message_text(
      text="Oferta aceptada!",
      chat_id=query.message.chat_id,
      message_id=query.message.message_id
    )
  elif callback_data['opt'] == IGNORE_OFFER:
    offer_id = ObjectId(callback_data['oid'])
    job_offer = db.job_offers.update(
      { '_id': offer_id },
      {'$set': {'status': 'ignored'}}
    )
    bot.edit_message_text(
      text="Oferta ignorada!",
      chat_id=query.message.chat_id,
      message_id=query.message.message_id
    )
  elif callback_data['opt'] == REJECT_OFFER:
    offer_id = ObjectId(callback_data['oid'])
    job_offer = db.job_offers.update(
      { '_id': offer_id },
      {'$set': {'status': 'rejected'}}
    )
    job_offer = db.job_offers.find_one({ '_id': offer_id })
    job_offer.pop('_id', None)
    to_email = job_offer['response']['Email de respuesta']
    mailer.send_mail.delay(to_email, job_offer)
    bot.edit_message_text(
      text="Oferta rechazada!",
      chat_id=query.message.chat_id,
      message_id=query.message.message_id
    )
  else:
    bot.edit_message_text(
      text="Comando desconocido!",
      chat_id=query.message.chat_id,
      message_id=query.message.message_id
    )

def unseen_offers(bot, update):
  undefined_offers = db.job_offers.find(
    { 'status': 'undefined' }
  )
  empty = True

  for undef_offer in undefined_offers:
    empty = False
    button_list = [
      InlineKeyboardButton(
        "Aceptar",
        callback_data=ujson.dumps({ 
          'opt': ACCEPT_OFFER, 
          'oid': str(undef_offer['_id'])
        })
      ),
      InlineKeyboardButton(
        "Ignorar", 
        callback_data=ujson.dumps({
          'opt': IGNORE_OFFER,
          'oid': str(undef_offer['_id'])
        })
      ),
      InlineKeyboardButton(
        "Rechazar",
        callback_data=ujson.dumps({
          'opt': REJECT_OFFER,
          'oid': str(undef_offer['_id'])
        })
      )
    ]
    
    reply_markup = InlineKeyboardMarkup(
      build_menu(button_list, n_cols=3)
    )
    
    msg = '*Oferta de trabajo*\n'
    msg += format_offer(undef_offer)
    bot.send_message(
      chat_id=admin_chat_id,
      text=msg,
      reply_markup=reply_markup,
      parse_mode=telegram.ParseMode.MARKDOWN,
      disable_web_page_preview=True
    )

  if empty:
    bot.send_message(
      chat_id=admin_chat_id,
      text="No hay mas ofertas por revisar!"
    )

def callback(ch, method, properties, body):
  global admin_chat_id
  global bot
  
  offer_data = ujson.loads(body)
  offer_data['status'] = 'undefined'
  db.job_offers.insert_one(offer_data)
  if admin_chat_id:
    bot.send_message(
      chat_id=admin_chat_id,
      text='🍺 Nueva oferta de trabajo!'
    )

def main():
  global bot

  # Create the EventHandler and pass it your bot's token.
  updater = Updater(token=connvars.BOT_TOKEN)

  bot = updater.bot

  connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
  )
  channel = connection.channel()
  channel.queue_declare(queue='jobform_submits')

  channel.basic_consume(
    callback,
    queue='jobform_submits',
    no_ack=True
  )

  # Get the dispatcher to register handlers
  dp = updater.dispatcher

  # simple start function
  dp.add_handler(CommandHandler("start", start_callback))
  dp.add_handler(CommandHandler("setadminchat", set_admin_chat_callback, pass_args=True))
  dp.add_handler(CommandHandler("setpostchat", set_post_chat_callback))
  dp.add_handler(CommandHandler("review", unseen_offers))
  dp.add_handler(CallbackQueryHandler(handle_offer))

  # log all errors
  dp.add_error_handler(error)

  # Start the Bot
  updater.start_polling()

  # Run the bot until you press Ctrl-C or the process receives SIGINT,
  # SIGTERM or SIGABRT. This should be used most of the time, since
  # start_polling() is non-blocking and will stop the bot gracefully.
  
  print(' [*] Waiting for messages. To exit press CTRL+C')

  try:
    channel.start_consuming()
  except KeyboardInterrupt:
    channel.stop_consuming()
  connection.close()
  updater.stop()


if __name__ == '__main__':
  main()

  