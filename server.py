#!/usr/bin/env python
import pika
import bot

def app(environ, start_response):
  data = b""
  
  if environ['REQUEST_METHOD'].upper() != 'POST':
    status = '500 Internal Server Error'
  else:
    status = '200 OK'
    body = environ['wsgi.input'].read()
    connection = pika.BlockingConnection(
      pika.ConnectionParameters(host='localhost')
    )
    channel = connection.channel()
    channel.queue_declare(queue='jobform_submits')
    channel.basic_publish(exchange='',
                          routing_key='jobform_submits',
                          body=body)
    connection.close()
    print(" [x] Redirected form response")
  
  start_response(status, [
    ("Content-Type", "text/plain"),
    ("Content-Length", str(len(data)))
  ])

  return iter([data])