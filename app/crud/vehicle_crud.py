import boto3
from boto3.dynamodb.conditions import Attr
from typing import List, Optional
from datetime import datetime
import uuid
from app.config import config
from app.models.vehicle import Vehicle, VehicleCreate, VehicleUpdate

class VehicleCRUD:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
        )
        self.table = self.dynamodb.Table(config.VEHICLES_TABLE)
    
    def create_vehicle(self, vehicle_data: VehicleCreate) -> Vehicle:
        """Create a new vehicle"""
        vehicle_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        vehicle = Vehicle(
            vehicle_id=vehicle_id,
            **vehicle_data.dict(),
            created_at=timestamp,
            updated_at=timestamp
        )
        
        self.table.put_item(Item=vehicle.dict())
        return vehicle
    
    def get_vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        """Get vehicle by ID"""
        response = self.table.get_item(Key={'vehicle_id': vehicle_id})
        
        if 'Item' in response:
            return Vehicle(**response['Item'])
        return None
    
    def get_all_vehicles(self) -> List[Vehicle]:
        """Get all vehicles"""
        response = self.table.scan()
        vehicles = [Vehicle(**item) for item in response.get('Items', [])]
        
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            vehicles.extend([Vehicle(**item) for item in response.get('Items', [])])
        
        return vehicles
    
    def get_vehicles_by_customer(self, customer_id: str) -> List[Vehicle]:
        """Get all vehicles for a customer"""
        response = self.table.scan(
            FilterExpression=Attr('customer_id').eq(customer_id)
        )
        return [Vehicle(**item) for item in response.get('Items', [])]
    
    def update_vehicle(self, vehicle_id: str, vehicle_data: VehicleUpdate) -> Optional[Vehicle]:
        """Update an existing vehicle"""
        current_vehicle = self.get_vehicle(vehicle_id)
        if not current_vehicle:
            return None
        
        update_data = vehicle_data.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in update_data.keys()])
        expression_attribute_names = {f"#{k}": k for k in update_data.keys()}
        expression_attribute_values = {f":{k}": v for k, v in update_data.items()}
        
        response = self.table.update_item(
            Key={'vehicle_id': vehicle_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"
        )
        
        return Vehicle(**response['Attributes'])
    
    def delete_vehicle(self, vehicle_id: str) -> bool:
        """Delete a vehicle"""
        try:
            self.table.delete_item(Key={'vehicle_id': vehicle_id})
            return True
        except Exception as e:
            print(f"Error deleting vehicle: {e}")
            return False