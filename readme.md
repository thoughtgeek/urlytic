## Urlytic
A file uploader with feature to generate multiple urls and set the number of times it can be used and the expirydate/lifespan of the link.


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

Webhook request format 

```
content-type : application/json

{
            'document':DOCUMENT NAME,
            'shortlink':GENERATED LINK,
            'usage_count':NUMBER OF TIMES LINK ACCESSED,
            'max_count':MAX NUMBER OF TIMES LINK CAN BE ACCESSED,
    }
```