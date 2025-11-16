import boto3
import json
from typing import Dict, Any, List
from app.config import config

class QueueService:
    """
    Non-CRUD Service for managing message queue via AWS SQS
    No database operations - Pure queue management logic
    """
    
    def __init__(self):
        self.sqs_client = boto3.client(
            'sqs',
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
        )
        self.queue_url = config.SQS_QUEUE_URL
    
    def enqueue_booking_request(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add booking request to queue for asynchronous processing"""
        try:
            message_body = {
                'message_type': 'BOOKING_REQUEST',
                'data': booking_data,
                'timestamp': str(datetime.utcnow())
            }
            
            response = self.sqs_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_body),
                MessageAttributes={
                    'MessageType': {
                        'StringValue': 'BOOKING_REQUEST',
                        'DataType': 'String'
                    },
                    'Priority': {
                        'StringValue': booking_data.get('priority', 'NORMAL'),
                        'DataType': 'String'
                    }
                }
            )
            
            return {
                'status': 'success',
                'message': 'Booking request queued successfully',
                'message_id': response['MessageId']
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to queue booking request: {str(e)}'
            }
    
    def enqueue_service_completion(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add service completion notification to queue"""
        try:
            message_body = {
                'message_type': 'SERVICE_COMPLETION',
                'data': service_data,
                'timestamp': str(datetime.utcnow())
            }
            
            response = self.sqs_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_body),
                MessageAttributes={
                    'MessageType': {
                        'StringValue': 'SERVICE_COMPLETION',
                        'DataType': 'String'
                    }
                }
            )
            
            return {
                'status': 'success',
                'message': 'Service completion queued successfully',
                'message_id': response['MessageId']
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to queue service completion: {str(e)}'
            }
    
    def enqueue_payment_processing(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add payment processing request to queue"""
        try:
            message_body = {
                'message_type': 'PAYMENT_PROCESSING',
                'data': payment_data,
                'timestamp': str(datetime.utcnow())
            }
            
            response = self.sqs_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_body),
                MessageAttributes={
                    'MessageType': {
                        'StringValue': 'PAYMENT_PROCESSING',
                        'DataType': 'String'
                    }
                }
            )
            
            return {
                'status': 'success',
                'message': 'Payment processing queued successfully',
                'message_id': response['MessageId']
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to queue payment processing: {str(e)}'
            }
    
    def receive_messages(self, max_messages: int = 10) -> Dict[str, Any]:
        """Receive messages from queue"""
        try:
            response = self.sqs_client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                MessageAttributeNames=['All'],
                WaitTimeSeconds=10
            )
            
            messages = []
            for message in response.get('Messages', []):
                messages.append({
                    'message_id': message['MessageId'],
                    'receipt_handle': message['ReceiptHandle'],
                    'body': json.loads(message['Body']),
                    'attributes': message.get('MessageAttributes', {})
                })
            
            return {
                'status': 'success',
                'message': f'Received {len(messages)} messages',
                'messages': messages,
                'count': len(messages)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to receive messages: {str(e)}'
            }
    
    def delete_message(self, receipt_handle: str) -> Dict[str, Any]:
        """Delete processed message from queue"""
        try:
            self.sqs_client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            
            return {
                'status': 'success',
                'message': 'Message deleted successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to delete message: {str(e)}'
            }
    
    def get_queue_attributes(self) -> Dict[str, Any]:
        """Get queue statistics and attributes"""
        try:
            response = self.sqs_client.get_queue_attributes(
                QueueUrl=self.queue_url,
                AttributeNames=['All']
            )
            
            attributes = response.get('Attributes', {})
            
            return {
                'status': 'success',
                'message': 'Queue attributes retrieved successfully',
                'attributes': {
                    'approximate_messages': attributes.get('ApproximateNumberOfMessages', '0'),
                    'approximate_messages_not_visible': attributes.get('ApproximateNumberOfMessagesNotVisible', '0'),
                    'approximate_messages_delayed': attributes.get('ApproximateNumberOfMessagesDelayed', '0'),
                    'created_timestamp': attributes.get('CreatedTimestamp', '0'),
                    'last_modified_timestamp': attributes.get('LastModifiedTimestamp', '0')
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to get queue attributes: {str(e)}'
            }