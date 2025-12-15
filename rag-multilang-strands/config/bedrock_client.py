
import boto3
import os
from dotenv import load_dotenv
from config.settings import AWS_REGION

def bedrock_runtime():
    load_dotenv()
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")
    region = os.getenv("AWS_DEFAULT_REGION", AWS_REGION)

    session_args = {"region_name": region}
    if aws_access_key and aws_secret_key:
        session_args["aws_access_key_id"] = aws_access_key
        session_args["aws_secret_access_key"] = aws_secret_key
        if aws_session_token:
            session_args["aws_session_token"] = aws_session_token

    return boto3.client("bedrock-runtime", **session_args)

def translate_client():
    load_dotenv()
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")
    region = os.getenv("AWS_DEFAULT_REGION", AWS_REGION)

    session_args = {"region_name": region}
    if aws_access_key and aws_secret_key:
        session_args["aws_access_key_id"] = aws_access_key
        session_args["aws_secret_access_key"] = aws_secret_key
        if aws_session_token:
            session_args["aws_session_token"] = aws_session_token

    return boto3.client("translate", **session_args)
