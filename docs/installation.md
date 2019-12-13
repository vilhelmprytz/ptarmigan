# Installation

This guide will cover the basics of installing ptarmigan.

## MySQL

Ptarmigan uses MySQL as database. This guide will not cover on how to install MySQL. Once you have MySQL configured, create a database and an user account for ptarmigan.

## Redis

Ptarmigan uses Redis for session management. Redis can be installed using `apt`.

```bash
apt install -y redis
```

## Cloning ptarmigan

First we need to install Git and Python 3 (and vim, you can use other text editors such as nano if it suits you better).

```
apt install python3 python3-pip git vim
```

Select a base directory for the ptarmigan installation, i.e: `/opt`.

```
cd /opt
```

Clone the Git repository from the base directory. This will create the ptarmigan application directory and extract the repository into it.

```
git clone https://github.com/VilhelmPrytz/ptarmigan.git
```

Once the repository has been cloned, you can `cd` into the newly cloned repository.

```
cd ptarmigan
```

## Python Packages

After that, the required dependencies must be installed.

```
pip3 install -r requirements.txt
```

## Configuration

Open up the main configuration in your editor of choice.

```
vim config.json
```

The configuration should look something like this.

```
{
    "settings": {
        "name": "Ptarmigan"
    },
    "mysql": {
        "host": "127.0.0.1",
        "username": "ptarmigan",
        "password": "password",
        "database": "ptarmigan"
    },
    "redis": {
        "host": "127.0.0.1",
        "port": 6379
    },
    "mail": {
        "smtp_host": "",
        "smtp_user": "",
        "smtp_password": "",
        "smtp_port": "",
        "smtp_ssl": true
    }
}
```

Modify the variables according to your needs.

## Create a new admin

You can create an admin account using the script.

```
python3 create_admin.py
```

## Test the application

You can test if the application boots by running Flask's built-in development server.

```
python3 app.py
```

## Serving ptarmigan using gunicorn and supervisor

Install gunicorn.

```
pip3 install gunicorn
```

Create a `gunicorn_config.py` file with the following configuration.

```
command = '/usr/local/bin/gunicorn'
pythonpath = '/opt/ptarmigan'
bind = '127.0.0.1:8001'
workers = 4
timeout = 300
user = 'www-data'
```

Install supervisord.

```
apt install supervisor
```

Create a configuration file `/etc/supervisor/conf.d/ptarmigan.conf` with the following configuration.

```
[program:ptarmigan]
directory = /opt/ptarmigan/
command = gunicorn -c /opt/peering-manager/ptarmigan/gunicorn_config.py ptarmigan.wsgi
user = www-data
```

Restart supervisord.

```
systemctl restart supervisor
```

## Nginx configuration

You can use Nginx's `proxy_pass` functionality in order to serve the gunicorn application through nginx.

Create a new VirtualHost in your `/etc/nginx/sites-available` (e.g. `ptarmigan`).

```
server {
	listen 80;
	listen [::]:80;

	root /var/www/html;

	index index.html index.htm index.nginx-debian.html index.php;

	server_name <servername>;

	location / {
		proxy_pass http://127.0.0.1:8001;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header Host $host;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	}

}
```

Replace `<servername>` with the hostname of your installation. It is also recommended to use HTTPS (can be installed with Let's Encrypt).

Activate your VirtualHost.

```
ln -s /etc/nginx/sites-available/ptarmigan /etc/nginx/sites-enabled/ptarmigan
```

Restart nginx.

```
systemctl restart nginx
```