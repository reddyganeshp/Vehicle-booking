import boto3
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import config

def create_dynamodb_tables():
    """Create all required DynamoDB tables"""
    
    boto_config = config.get_boto3_config()
    dynamodb = boto3.resource('dynamodb', **boto_config)
    
    tables_config = [
        {
            'TableName': config.BOOKINGS_TABLE,
            'KeySchema': [{'AttributeName': 'booking_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'booking_id', 'AttributeType': 'S'}],
        },
        {
            'TableName': config.VEHICLES_TABLE,
            'KeySchema': [{'AttributeName': 'vehicle_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'vehicle_id', 'AttributeType': 'S'}],
        },
        {
            'TableName': config.CUSTOMERS_TABLE,
            'KeySchema': [{'AttributeName': 'customer_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'customer_id', 'AttributeType': 'S'}],
        },
        {
            'TableName': config.SERVICE_CENTERS_TABLE,
            'KeySchema': [{'AttributeName': 'service_center_id', 'KeyType': 'HASH'}],
            'AttributeDefinitions': [{'AttributeName': 'service_center_id', 'AttributeType': 'S'}],
        },
    ]
    
    for table_config in tables_config:
        try:
            table = dynamodb.create_table(
                TableName=table_config['TableName'],
                KeySchema=table_config['KeySchema'],
                AttributeDefinitions=table_config['AttributeDefinitions'],
                BillingMode='PAY_PER_REQUEST'
            )
            print(f"✅ Creating table: {table_config['TableName']}")
            
            if not config.USE_LOCALSTACK:
                table.wait_until_exists()
                print(f"✅ Table created: {table_config['TableName']}")
        except dynamodb.meta.client.exceptions.ResourceInUseException:
            print(f"ℹ️  Table already exists: {table_config['TableName']}")
        except Exception as e:
            print(f"❌ Error creating table {table_config['TableName']}: {str(e)}")

def create_s3_bucket():
    """Create S3 bucket"""
    boto_config = config.get_boto3_config()
    s3 = boto3.client('s3', **boto_config)
    
    try:
        s3.create_bucket(Bucket=config.S3_BUCKET_NAME)
        print(f"✅ Created S3 bucket: {config.S3_BUCKET_NAME}")
    except Exception as e:
        if 'BucketAlreadyOwnedByYou' in str(e) or 'BucketAlreadyExists' in str(e):
            print(f"ℹ️  S3 bucket already exists: {config.S3_BUCKET_NAME}")
        else:
            print(f"❌ Error creating S3 bucket: {str(e)}")

def create_sns_topic():
    """Create SNS topic"""
    boto_config = config.get_boto3_config()
    sns = boto3.client('sns', **boto_config)
    
    try:
        response = sns.create_topic(Name='vehicle-service-notifications')
        print(f"✅ Created SNS topic: {response['TopicArn']}")
        return response['TopicArn']
    except Exception as e:
        print(f"❌ Error creating SNS topic: {str(e)}")
        return None

def create_sqs_queue():
    """Create SQS queue"""
    boto_config = config.get_boto3_config()
    sqs = boto3.client('sqs', **boto_config)
    
    try:
        response = sqs.create_queue(QueueName='vehicle-service-queue')
        print(f"✅ Created SQS queue: {response['QueueUrl']}")
        return response['QueueUrl']
    except Exception as e:
        if 'QueueAlreadyExists' in str(e):
            print(f"ℹ️  SQS queue already exists")
        else:
            print(f"❌ Error creating SQS queue: {str(e)}")
        return None

def main():
    print("🚀 Creating AWS resources...\n")
    
    print("1️⃣  Creating DynamoDB tables...")
    create_dynamodb_tables()
    
    print("\n2️⃣  Creating S3 bucket...")
    create_s3_bucket()
    
    print("\n3️⃣  Creating SNS topic...")
    create_sns_topic()
    
    print("\n4️⃣  Creating SQS queue...")
    create_sqs_queue()
    
    print("\n✅ All AWS resources created successfully!")
    print("\n📝 Note: If using LocalStack, make sure it's running on http://localhost:4566")

if __name__ == "__main__":
    main()