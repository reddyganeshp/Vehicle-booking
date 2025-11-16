import boto3
import json
from typing import Dict, Any, List
from app.config import config

class NotificationService:
    """
    Non-CRUD Service for sending notifications via AWS SNS
    No database operations - Pure business logic
    """
    
    def __init__(self):
        self.sns_client = boto3.client(
            'sns',
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
        )
        self.topic_arn = config.SNS_TOPIC_ARN
    
    def send_booking_confirmation(self, customer_email: str, booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send booking confirmation notification"""
        message = self._format_booking_confirmation_message(booking_details)
        
        try:
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject="Booking Confirmation - Vehicle Service",
                Message=json.dumps({
                    'default': message,
                    'email': message,
                    'customer_email': customer_email,
                    'notification_type': 'BOOKING_CONFIRMATION'
                }),
                MessageStructure='json'
            )
            return {
                'status': 'success',
                'message_id': response['MessageId'],
                'message': 'Booking confirmation sent successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to send notification: {str(e)}'
            }
    
    def send_booking_reminder(self, customer_email: str, booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send booking reminder notification"""
        message = self._format_booking_reminder_message(booking_details)
        
        try:
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject="Reminder: Upcoming Vehicle Service",
                Message=json.dumps({
                    'default': message,
                    'email': message,
                    'customer_email': customer_email,
                    'notification_type': 'BOOKING_REMINDER'
                }),
                MessageStructure='json'
            )
            return {
                'status': 'success',
                'message_id': response['MessageId'],
                'message': 'Booking reminder sent successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to send reminder: {str(e)}'
            }
    
    def send_service_completion(self, customer_email: str, service_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send service completion notification"""
        message = self._format_service_completion_message(service_details)
        
        try:
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject="Service Completed - Vehicle Service",
                Message=json.dumps({
                    'default': message,
                    'email': message,
                    'customer_email': customer_email,
                    'notification_type': 'SERVICE_COMPLETION'
                }),
                MessageStructure='json'
            )
            return {
                'status': 'success',
                'message_id': response['MessageId'],
                'message': 'Service completion notification sent successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to send notification: {str(e)}'
            }
    
    def send_cancellation_notification(self, customer_email: str, booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send booking cancellation notification"""
        message = self._format_cancellation_message(booking_details)
        
        try:
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject="Booking Cancelled - Vehicle Service",
                Message=json.dumps({
                    'default': message,
                    'email': message,
                    'customer_email': customer_email,
                    'notification_type': 'BOOKING_CANCELLATION'
                }),
                MessageStructure='json'
            )
            return {
                'status': 'success',
                'message_id': response['MessageId'],
                'message': 'Cancellation notification sent successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to send notification: {str(e)}'
            }
    
    def _format_booking_confirmation_message(self, booking_details: Dict[str, Any]) -> str:
        """Format booking confirmation message"""
        return f"""
Dear Customer,

Your vehicle service booking has been confirmed!

Booking Details:
- Booking ID: {booking_details.get('booking_id', 'N/A')}
- Service Type: {booking_details.get('service_type', 'N/A')}
- Date: {booking_details.get('booking_date', 'N/A')}
- Time: {booking_details.get('scheduled_time', 'N/A')}
- Service Center: {booking_details.get('service_center_name', 'N/A')}
- Estimated Cost: ${booking_details.get('estimated_cost', '0.00')}

We look forward to serving you!

Best regards,
Vehicle Service Team
        """
    
    def _format_booking_reminder_message(self, booking_details: Dict[str, Any]) -> str:
        """Format booking reminder message"""
        return f"""
Dear Customer,

This is a reminder about your upcoming vehicle service appointment.

Appointment Details:
- Booking ID: {booking_details.get('booking_id', 'N/A')}
- Service Type: {booking_details.get('service_type', 'N/A')}
- Date: {booking_details.get('booking_date', 'N/A')}
- Time: {booking_details.get('scheduled_time', 'N/A')}
- Service Center: {booking_details.get('service_center_name', 'N/A')}

Please arrive 10 minutes before your scheduled time.

Best regards,
Vehicle Service Team
        """
    
    def _format_service_completion_message(self, service_details: Dict[str, Any]) -> str:
        """Format service completion message"""
        return f"""
Dear Customer,

Your vehicle service has been completed!

Service Details:
- Service Type: {service_details.get('service_type', 'N/A')}
- Total Cost: ${service_details.get('actual_cost', '0.00')}
- Completion Date: {service_details.get('completion_date', 'N/A')}

Your vehicle is ready for pickup. Thank you for choosing our service!

Best regards,
Vehicle Service Team
        """
    
    def _format_cancellation_message(self, booking_details: Dict[str, Any]) -> str:
        """Format cancellation message"""
        return f"""
Dear Customer,

Your vehicle service booking has been cancelled.

Cancelled Booking Details:
- Booking ID: {booking_details.get('booking_id', 'N/A')}
- Service Type: {booking_details.get('service_type', 'N/A')}
- Original Date: {booking_details.get('booking_date', 'N/A')}
- Original Time: {booking_details.get('scheduled_time', 'N/A')}

If you'd like to reschedule, please create a new booking.

Best regards,
Vehicle Service Team
        """