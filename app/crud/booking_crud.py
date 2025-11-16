import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import List, Optional
from datetime import datetime
import uuid
from app.config import config
from app.models.booking import Booking, BookingCreate, BookingUpdate

class BookingCRUD:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
        )
        self.table = self.dynamodb.Table(config.BOOKINGS_TABLE)
    
    def create_booking(self, booking_data: BookingCreate) -> Booking:
        """Create a new booking"""
        booking_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        booking = Booking(
            booking_id=booking_id,
            **booking_data.dict(),
            created_at=timestamp,
            updated_at=timestamp
        )
        
        self.table.put_item(Item=booking.dict())
        return booking
    
    def get_booking(self, booking_id: str) -> Optional[Booking]:
        """Get booking by ID"""
        response = self.table.get_item(Key={'booking_id': booking_id})
        
        if 'Item' in response:
            return Booking(**response['Item'])
        return None
    
    def get_all_bookings(self) -> List[Booking]:
        """Get all bookings"""
        response = self.table.scan()
        bookings = [Booking(**item) for item in response.get('Items', [])]
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            bookings.extend([Booking(**item) for item in response.get('Items', [])])
        
        return bookings
    
    def get_bookings_by_customer(self, customer_id: str) -> List[Booking]:
        """Get all bookings for a customer"""
        response = self.table.scan(
            FilterExpression=Attr('customer_id').eq(customer_id)
        )
        return [Booking(**item) for item in response.get('Items', [])]
    
    def get_bookings_by_vehicle(self, vehicle_id: str) -> List[Booking]:
        """Get all bookings for a vehicle"""
        response = self.table.scan(
            FilterExpression=Attr('vehicle_id').eq(vehicle_id)
        )
        return [Booking(**item) for item in response.get('Items', [])]
    
    def update_booking(self, booking_id: str, booking_data: BookingUpdate) -> Optional[Booking]:
        """Update an existing booking"""
        # Get current booking
        current_booking = self.get_booking(booking_id)
        if not current_booking:
            return None
        
        # Update fields
        update_data = booking_data.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Build update expression
        update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in update_data.keys()])
        expression_attribute_names = {f"#{k}": k for k in update_data.keys()}
        expression_attribute_values = {f":{k}": v for k, v in update_data.items()}
        
        response = self.table.update_item(
            Key={'booking_id': booking_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"
        )
        
        return Booking(**response['Attributes'])
    
    def delete_booking(self, booking_id: str) -> bool:
        """Delete a booking"""
        try:
            self.table.delete_item(Key={'booking_id': booking_id})
            return True
        except Exception as e:
            print(f"Error deleting booking: {e}")
            return False