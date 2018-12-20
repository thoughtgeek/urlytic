# s3Metafora - README
### A simple S3 file uploader
---
#### Instructions to run on localhost or EC2 instance:

Add a file '.env' in the root with the following information
```python
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''
SECRET_KEY = ''
```
# Zappa Deployment Steps

#### Install required packages and zappa:
Required packages to be installed first as Zappa requires specific versions of the required packages
```sh
pip install -r requirements.txt
pip install zappa
```

#### Instructions to edit settings.py before 'zappa init':

In settings.py add this line:
```python
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```
Replace the following lines in settings.py:
```python
SECRET_KEY = config('SECRET_KEY')
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
```

By,
```python
SECRET_KEY = os.environ.get('SECRET_KEY')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
```
Set permissions for IAM user, by adding following policies to the user:

```
* AmazonAPIGatewayAdministrator
    * AWS managed policy
* AmazonCloudDirectoryFullAccess
    * AWS managed policy
* AmazonEC2FullAccess
    * AWS managed policy
* AmazonS3FullAccess
    * AWS managed policy
* AWSLambdaFullAccess
    * AWS managed policy
* IAMFullAccess
    * AWS managed policy
* AmazonVPCFullAccess
    * AWS managed policy
* AWSCloud9Administrator
    * AWS managed policy
* SecurityAudit
```
Add custom policy to give IAM user full access to Cloudformation:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "cloudformation:*",
            "Resource": "*"
        }
    ]
}
```
#### Initialize zappa deployment:
After following instructions to edit settings.py and deploy 1st time:
```sh
zappa init
zappa deploy <deployment name>
```


#### Setting up Lambda Environment variables:
Use the web portal to set up the environment variables to the lambda function 's3metafora-<deployment_name>' or use AWS CLI.
Set the following variables: `SECRET_KEY, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME`using aws portal(Recommended) or aws cli like this:
```sh
pip install awscli
aws lambda update-function-configuration --function-name <s3metafora-<deployment_name>> --environment Variables={SECRET_KEY=<value>,AWS_ACCESS_KEY_ID=<value>,AWS_SECRET_ACCESS_KEY=<value>,AWS_STORAGE_BUCKET_NAME=<value>}
```




# AWS Aurora Serverless - Interfacing with Lambda deployment

#### Create new VPC for RDS and Lambda:

Create a new VPC. Create 2 subnets with 2 different region selection(Preferably same region, different subregions) using AWS Web Portal. Note down the subnet ids and security group ids.

#### Create Serverless Aurora RDS:

```sh
pip install awscli
aws configure
```

Run the following to create db subnet group: (Remember there must be atleast 2 subnets in 2 different regions)
```sh
aws rds create-db-subnet-group --db-subnet-group-name <DB Subnet Group Name> --db-subnet-group-description <Subnet Group Description> --subnet-ids <Subnet Id 1> <Subnet Id 2>..
```
Run the following to finally create the Aurora Serverless RDS with the database initialized:
```sh
aws rds create-db-cluster --db-cluster-identifier <Cluster Name> --engine aurora --engine-version 5.6.10a --engine-mode serverless --scaling-configuration MinCapacity=4,MaxCapacity=8,SecondsUntilAutoPause=1000,AutoPause=true --master-username <Username> --master-user-password <Password> --database-name <DB name> --db-subnet-group-name <DB Subnet Group Name> --vpc-security-group-ids <Security Group ID>
```
#### Change settings.py to connect to serverless RDS:
Change the following lines
```sh
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```
to 
```sh
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': <RDS name>,
        'USER': <RDS username>,
        'PASSWORD': <RDS password>,
        'HOST': <RDS endpoint>,
        'PORT': '3306',
    }
}
```
And install mySQL client: `pip install mysqlclient`
####  Add VPC information in zappa_settings.json:
Add the following entry in the zappa_settings.json:
```
        "vpc_config": {
            "SubnetIds": [<subnetvalue1>, <subnetvalue2>],
            "SecurityGroupIds": [ <SgGroupIdvalue> ],}
```            

#### Use Zappa to initialize DB after it is deployed:
```sh
zappa manage dev "migrate --run-syncdb"
```
And for creating the first user:
```sh
zappa manage dev create_admin_user <auth_token> <email> <auth_token>
```
If using SQLite on localhost
** Set the database in settings.py and run 'python manage.py migrate --run-syncdb' **

# Deploy!

Add AWS credentials - (In case AWS CLI not installed and configured)
Create a new directory and file ~.aws/credentials and add the following lines:
```python
[default]
aws_access_key_id = YOUR ACCESS KEY
aws_secret_access_key = YOUR SECRET ACCESS KEY
```
To deploy, run:  
```sh
python manage.py collectstatic
zappa init
```
In zappa_settings.json replace 'dev' with the name of your deployment and setting its corrosponding values:

```json
{
    "dev": {
        ...
        "environment_variables": {
            "AWS_ACCESS_KEY_ID": "your_value",
            "SECRET_KEY" : "your_value",
            "AWS_SECRET_ACCESS_KEY" : "your_value",
            "AWS_STORAGE_BUCKET_NAME" : "your_value",

        }
    },
    ...
}
```

Finally,
```sh
zappa deploy
```
