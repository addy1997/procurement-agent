import os
import boto3
from botocore.exceptions import ClientError

# Initialize the client ONCE outside the function (Global Scope)
# This improves performance during Lambda "warm starts"
ssm = boto3.client('ssm', region_name='us-east-1') # Ensure region matches image_a55137.png

def get_config(setting_name):
    # 1. Check for Environment Variables (Set in Lambda Console)
    # This is faster than an SSM network call
    val = os.getenv(setting_name)
    if val:
        return val

    # 2. Fallback to AWS SSM Parameter Store
    try:
        parameter = ssm.get_parameter(Name=setting_name, WithDecryption=True)
        return parameter['Parameter']['Value']
    except ClientError as e:
        # ClientError is more specific than Exception for AWS issues
        print(f"AWS SSM Error fetching {setting_name}: {e.response['Error']['Message']}")
        return None
    except Exception as e:
        print(f"General Error fetching {setting_name}: {e}")
        return None