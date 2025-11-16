import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # AWS Configuration
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
    
    # LocalStack Configuration
    USE_LOCALSTACK = os.getenv("USE_LOCALSTACK", "False") == "True"
    LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT", "http://localhost:4566")
    
    # DynamoDB Tables
    BOOKINGS_TABLE = os.getenv("BOOKINGS_TABLE", "vehicle_bookings")
    VEHICLES_TABLE = os.getenv("VEHICLES_TABLE", "vehicles")
    CUSTOMERS_TABLE = os.getenv("CUSTOMERS_TABLE", "customers")
    SERVICE_CENTERS_TABLE = os.getenv("SERVICE_CENTERS_TABLE", "service_centers")
    
    # S3 Configuration
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "vehicle-service-documents")
    
    # SNS Configuration
    SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:000000000000:vehicle-service-notifications")
    
    # SQS Configuration
    SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL", "http://localhost:4566/000000000000/vehicle-service-queue")
    
    # EventBridge Configuration
    EVENTBRIDGE_RULE_NAME = os.getenv("EVENTBRIDGE_RULE_NAME", "vehicle-service-reminders")
    
    # Application Settings
    APP_NAME = "Vehicle Service Booking System"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "True") == "True"
    
    @classmethod
    def get_boto3_config(cls):
        """Get boto3 configuration based on environment"""
        config = {
            'region_name': cls.AWS_REGION,
        }
        
        if cls.USE_LOCALSTACK:
            config['endpoint_url'] = cls.LOCALSTACK_ENDPOINT
            config['aws_access_key_id'] = 'test'
            config['aws_secret_access_key'] = 'test'
        else:
            if cls.AWS_ACCESS_KEY_ID and cls.AWS_SECRET_ACCESS_KEY:
                config['aws_access_key_id'] = cls.AWS_ACCESS_KEY_ID
                config['aws_secret_access_key'] = cls.AWS_SECRET_ACCESS_KEY
        
        return config

config = Config()