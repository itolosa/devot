# Devot

Bot de telegram para revisar ofertas de trabajo enviadas por Google Forms.

# Instalación

Se clona el repositorio y se corren los siguientes comandos:

```bash
$ git clone git@github.com:ChileDevs/devot.git
$ cd devot
```
Los siguientes comandos se corren en sesiones separadas ya que toman la terminal.

Levantar mongodb:
```bash
$ mongod
```

Levantar rabbitmq server:
```bash
$ rabbitmq-server start
```

Levantar Celery para manejar el envio de mails:
```bash
$ celery -A mailer worker --loglevel=info
```

Correr el bot de telegram (@DevotBot)
```bash
$ python bot.py
```

Correr el servidor de redireccionamiento
```bash
$ gunicorn -w 2 server:app
```

## En deploy
```bash
$ cd $HOME
$ virtualenv -p python3 devot
$ cd devot
$ git clone git@github.com:ChileDevs/devot.git
$ source bin/activate
$ cd devot 
$ sudo service mongodb start
$ sudo service rabbitmq-server start
$ celery multi start worker1 -A mailer --pidfile="$HOME/devot/devot/%n.pid" --logfile="$HOME/devot/devot/%n.log"
$ nohup python bot.py > $HOME/devot/devot/production.log 2>&1 &
$ nohup gunicorn -w 1 server:app < /dev/null > $HOME/devot/devot/gunicorn.log 2>&1 &
```

# Configuracion

Se debe crear el archivo connvars.py en el directorio raíz del proyecto usando connvars.example.py como referencia.

```bash
$ cp connvars.example.py connvars.py
```

Se debe configurar el Google Form asignandole un trigger `onSubmit` a una funcion que haga push de los datos hacia gunicorn. Para esto se facilita el script en `utils/submits.gs`

Se recomienda usar alguna herramienta de monitoreo como `monitd`.

# Colaboradores
* @itolosa