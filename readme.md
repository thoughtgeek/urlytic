# Urlytic
A file uploader with feature to generate multiple urls and set the number of times it can be used and the expirydate/lifespan of the link.

#### Project Specific Settings:
Store these settings in a .env file at the project root
_(How to obtain the social keys described below in deployment)_
```
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''
SECRET_KEY = ''
SOCIAL_AUTH_GITHUB_KEY = ''
SOCIAL_AUTH_GITHUB_SECRET = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''
SOCIAL_AUTH_FACEBOOK_KEY = ''
SOCIAL_AUTH_FACEBOOK_SECRET = ''
```
To set domain name:
Set `DOMAIN_NAME` in settings

For testing webhook:
Set `WEBHOOK_LINK` in settings/test.py and use `--settings=settings.test`

## Deployment
The standard process of deployment of any django app can be followed. Below explained deployment instructions with the following stack -
1. NGINX
2. Gunicorn
3. Supervisor
4. **PosgreSQL

** (Instructions if you wish to use postgreSQL database server on same instance) 
Install the dependencies to use PostgreSQL with Python/Django:
```
sudo apt-get -y install build-essential libpq-dev python-dev
```
**Install the PostgreSQL Server:
```
sudo apt-get -y install postgresql postgresql-contrib
```
Install NGINX, which will be used to serve static assets (css, js, images) and also to run the application behind a proxy server:
```
sudo apt-get -y install nginx
```
Supervisor will start the application server and manage it in case of server crash or restart:
```
sudo apt-get -y install supervisor
```
Enable and start the Supervisor:
```
sudo systemctl enable supervisor
sudo systemctl start supervisor
```
The application will be deployed inside a Python Virtualenv, isolating the python environment for application from system python:
```
sudo apt-get -y install python-virtualenv
```
##### Configure PostgreSQL Database
Switch users:
```
su - postgres
```
Create a database user and the application database:
```
createuser <USERNAME>
createdb <DATABASE NAME> --owner <USERNAME>
psql -c "ALTER USER <USERNAME> WITH PASSWORD '<PASSWORD>'"
```
##### Configure The Application User
_(Considering we are using root user)_
Create a new user without a password(press ent_er):
```
adduser <USERNAME>
```
Add user to sudoers file and configure to be able to be used without password:
```
visudo
```
Add to /etc/sudoers.tmp at the bottom
```
myuser ALL=(ALL) NOPASSWD:ALL 
```
Add SSH keys to user:
```
mkdir -p /home/<USERNAME>/.ssh
vi /home/<USERNAME>/authorized_keys
```
Lock user to disable password login
```
usermod -L <USERNAME>
```
Switch to the recently created user:
```
su  <USERNAME>
```
##### Configure the Python Virtualenv
Initiate virtualenv and activate it:
```
virtualenv -p python3 venv
source venv/bin/activate
```
Clone the repository and install requirements:
```
git clone <REPO URL>
cd <REPO NAME>
pip install -r requirements.txt
```
At this point we will need to set the database credentials in the settings.py file:

_**If you want to set the database from postgres server running on the same instance_
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '<DB NAME>',
        'USER': '<DB USER>',
        'PASSWORD': '<DB PASSWORD>',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```
Migrate the database:
```
python manage.py migrate
```
##### Configure Gunicorn
First install Gunicorn inside the virtualenv:
```
pip install gunicorn
```
Create a file named gunicorn_start inside the application folder:
```
vi gunicorn_start
```
Enter the following replacing the information in the gunicorn_start file:
```
#!/bin/bash
source ~/venv/bin/activate
cd ~/<REPO NAME>/
exec ~/venv/bin/gunicorn config.wsgi:application \
--name urlytic \
--workers 3 \
--user=<USERNAME> \
--group=<USERNAME> \
--bind=unix:/home/<USERNAME>/<REPO NAME>/run/gunicorn.sock \
--log-level=error \
--log-file=-
```
Make the gunicorn_start file is executable:
```
chmod u+x gunicorn_start
```
Create run directory inside project directory
```
cd <REPO NAME>
mkdir run
```
##### Configure Supervisor

Create a folder named logs:
```
mkdir logs
```
Create a file to be used to log the application errors:
```
touch logs/gunicorn-error.log
```
Create a new Supervisor configuration file:
```
sudo vim /etc/supervisor/conf.d/urlytic.conf
```
Create urlyic configuration using `vi etc/supervisor/conf.d/urlytic.conf`
```
[program:urban-train]
command=/home/urban/bin/gunicorn_start
user=urban
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/<USERNAME>/logs/gunicorn-error.log
```
Reread Supervisor configuration files and make the new program available:
```
sudo supervisorctl reread
sudo supervisorctl update
```
If everything has gone correctly, it should show `RUNNING`:
```
sudo supervisorctl status urlytic
urlytic                      RUNNING   pid 23381, uptime 0:00:15
```
**If you want to update the source code of your application with a new version, you can pull the code and then restart the process:**
```
sudo supervisorctl restart urlytic
```

##### Installing SSL certificate
Install certbot
```
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get install python-certbot-nginx
```
Installing SSL certificate from Let's Encript _(where example.com would be your domain)_
```
sudo certbot --nginx -d example.com -d www.example.com
```
More information about certbot: https://certbot.eff.org/

### Obtaining keys for Social Authentication
##### GitHub ClientID and ClientSecret:
To get GitHub key: https://github.com/settings/applications/new
Enter the following information:
1. Application name
2. Homepage URL
3. Application Description
4. Authorization callback URL

The important step here is the Authorization callback URL. Put the URL as follow: `https://<domain name>/oauth/complete/github/`

##### Facebook Key and Secret:
To get Facebook key: http://developers.facebook.com
Click on My Apps and then Add a New App. Pick website and Create App ID.
Grab the App ID and App Secret (click on the Show button to get it as plain text)
Enter site URL.

##### Google OAUTH key:
To get Google oauth key: https://bit.ly/2TMNZhE
Follow the steps:
1. Create a new application.
2. Create a new credential
3. Select website. If you require for testing select other client.
4. Authorized redirect url should be: https://<domain>/oauth/complete/google-oauth2/
