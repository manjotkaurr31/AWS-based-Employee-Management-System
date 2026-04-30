from sqlalchemy import create_engine
import boto3
import json

def get_database_url():
    client = boto3.client("secretsmanager", region_name="ap-south-1")
    response = client.get_secret_value(SecretId="employee-db-secret")
    secret = json.loads(response["SecretString"])
    return secret["DATABASE_URL"]

DATABASE_URL = get_database_url()
print("DB URL:", DATABASE_URL)
engine = create_engine(DATABASE_URL, echo=True)
