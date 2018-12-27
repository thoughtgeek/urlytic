## Urlytic

Add a file '.env' in the root with the following information
```
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''
SECRET_KEY = ''
```
Migrate using

```
python manage.py migrate --run-syncdb
```
Create the user

```
python manage.py createsuperuser
```