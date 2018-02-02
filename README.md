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

# Configuracion

Se debe crear el archivo connvars.py en el directorio raíz del proyecto usando connvars.example.py como referencia.

```bash
$ cp connvars.example.py connvars.py
```

Se debe configurar el Google Form asignandole un trigger `onSubmit` a una funcion que haga push de los datos hacia gunicorn. Para esto se facilita el script en `utils/submits.gs`

Se recomienda usar alguna herramienta de monitoreo como `monitd`.

# Colaboradores
* @itolosa