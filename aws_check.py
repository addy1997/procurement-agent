import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def test_aws_connection():
    print("☁️ Testing AWS SSM Connection...")
    try:
        # Initialize the SSM client
        # Boto3 will automatically look for credentials in ~/.aws/credentials 
        # or environment variables.
        ssm = boto3.client('ssm')
        
        # Attempt to retrieve your test parameter.
        parameter = ssm.get_parameter(Name='TEST_GREETING', WithDecryption=True)
        
        print(f"✅ Success! AWS Parameter Store returned: {parameter['Parameter']['Value']}")
        print("Your environment is correctly 'talking' to AWS.")

    except NoCredentialsError:
        print("❌ Error: No AWS credentials found. Run 'aws configure' in your terminal.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ParameterNotFound':
            print("❌ Error: 'TEST_GREETING' parameter not found in Parameter Store.")
        else:
            print(f"❌ AWS Client Error: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_aws_connection()