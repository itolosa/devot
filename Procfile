mongod: mongod
rabbitmq: rabbitmq-server start
celery: celery -A mailer worker --loglevel=info
bot: python bot.py
server: gunicorn -w 2 server:app