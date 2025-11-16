import boto3
import json
from typing import Dict, Any
from datetime import datetime, timedelta
from app.config import config

class SchedulerService:
    """
    Non-CRUD Service for scheduling events using AWS EventBridge
    No database operations - Pure scheduling logic
    """
    
    def __init__(self):
        self.eventbridge_client = boto3.client(
            'events',
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
        )
        self.rule_name_prefix = config.EVENTBRIDGE_RULE_NAME
    
    def schedule_booking_reminder(self, booking_id: str, booking_datetime: str, customer_email: str) -> Dict[str, Any]:
        """Schedule a reminder 24 hours before the booking"""
        try:
            # Calculate reminder time (24 hours before booking)
            booking_dt = datetime.fromisoformat(booking_datetime)
            reminder_dt = booking_dt - timedelta(hours=24)
            
            # Create cron expression for EventBridge
            cron_expression = f"cron({reminder_dt.minute} {reminder_dt.hour} {reminder_dt.day} {reminder_dt.month} ? {reminder_dt.year})"
            
            rule_name = f"{self.rule_name_prefix}-{booking_id}"
            
            # Create EventBridge rule
            self.eventbridge_client.put_rule(
                Name=rule_name,
                ScheduleExpression=cron_expression,
                State='ENABLED',
                Description=f'Reminder for booking {booking_id}'
            )
            
            # Add target (this would typically be a Lambda function)
            target_input = {
                'booking_id': booking_id,
                'customer_email': customer_email,
                'reminder_type': 'BOOKING_REMINDER',
                'booking_datetime': booking_datetime
            }
            
            return {
                'status': 'success',
                'message': 'Booking reminder scheduled successfully',
                'rule_name': rule_name,
                'reminder_datetime': reminder_dt.isoformat(),
                'cron_expression': cron_expression
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to schedule reminder: {str(e)}'
            }
    
    def schedule_service_follow_up(self, booking_id: str, service_completion_date: str) -> Dict[str, Any]:
        """Schedule a follow-up 7 days after service completion"""
        try:
            completion_dt = datetime.fromisoformat(service_completion_date)
            followup_dt = completion_dt + timedelta(days=7)
            
            cron_expression = f"cron({followup_dt.minute} {followup_dt.hour} {followup_dt.day} {followup_dt.month} ? {followup_dt.year})"
            
            rule_name = f"{self.rule_name_prefix}-followup-{booking_id}"
            
            self.eventbridge_client.put_rule(
                Name=rule_name,
                ScheduleExpression=cron_expression,
                State='ENABLED',
                Description=f'Follow-up for booking {booking_id}'
            )
            
            return {
                'status': 'success',
                'message': 'Service follow-up scheduled successfully',
                'rule_name': rule_name,
                'followup_datetime': followup_dt.isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to schedule follow-up: {str(e)}'
            }
    
    def schedule_recurring_maintenance_reminder(self, vehicle_id: str, interval_days: int = 90) -> Dict[str, Any]:
        """Schedule recurring maintenance reminders"""
        try:
            # Create rate expression for recurring reminders
            rate_expression = f"rate({interval_days} days)"
            
            rule_name = f"{self.rule_name_prefix}-maintenance-{vehicle_id}"
            
            self.eventbridge_client.put_rule(
                Name=rule_name,
                ScheduleExpression=rate_expression,
                State='ENABLED',
                Description=f'Recurring maintenance reminder for vehicle {vehicle_id}'
            )
            
            return {
                'status': 'success',
                'message': 'Recurring maintenance reminder scheduled',
                'rule_name': rule_name,
                'interval_days': interval_days
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to schedule recurring reminder: {str(e)}'
            }
    
    def cancel_scheduled_event(self, rule_name: str) -> Dict[str, Any]:
        """Cancel a scheduled event"""
        try:
            # Remove targets first
            targets_response = self.eventbridge_client.list_targets_by_rule(Rule=rule_name)
            
            if targets_response.get('Targets'):
                target_ids = [target['Id'] for target in targets_response['Targets']]
                self.eventbridge_client.remove_targets(
                    Rule=rule_name,
                    Ids=target_ids
                )
            
            # Delete the rule
            self.eventbridge_client.delete_rule(Name=rule_name)
            
            return {
                'status': 'success',
                'message': 'Scheduled event cancelled successfully',
                'rule_name': rule_name
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to cancel scheduled event: {str(e)}'
            }
    
    def list_scheduled_events(self, name_prefix: str = None) -> Dict[str, Any]:
        """List all scheduled events"""
        try:
            params = {}
            if name_prefix:
                params['NamePrefix'] = name_prefix
            
            response = self.eventbridge_client.list_rules(**params)
            
            rules = []
            for rule in response.get('Rules', []):
                rules.append({
                    'name': rule['Name'],
                    'state': rule['State'],
                    'schedule_expression': rule.get('ScheduleExpression', 'N/A'),
                    'description': rule.get('Description', '')
                })
            
            return {
                'status': 'success',
                'message': f'Found {len(rules)} scheduled events',
                'events': rules,
                'count': len(rules)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to list scheduled events: {str(e)}'
            }