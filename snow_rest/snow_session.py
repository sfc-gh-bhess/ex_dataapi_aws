import boto3
import os
import json
from snowflake.snowpark import Session

session = None
db_secret_name = os.environ['DB_SECRET_NAME']
db_warehouse = os.environ['DB_WAREHOUSE']

## SNOWFLAKE CREDENTIALS
def get_credentials():
    """Retrieve credentials from the Secrets Manager service."""
    boto_session = boto3.session.Session()
    try:
        secrets_client = boto_session.client(service_name='secretsmanager', region_name=boto_session.region_name)
        secret_value = secrets_client.get_secret_value(SecretId=db_secret_name)
        secret = secret_value['SecretString']
        secret_json = json.loads(secret)
        return secret_json
    except Exception as ex:
        raise

## SNOWFLAKE CONNECTION
def get_db_client():
    """Connect to Snowflake"""
    # Use a global variable so Lambda can reuse the persisted client on future invocations
    global session
    if session is None:
        try:
            creds = get_credentials()
            creds['warehouse'] = db_warehouse
            session = Session.builder.configs(creds).create()
            print("Connection established")
        except Exception as ex:
            raise
    return session