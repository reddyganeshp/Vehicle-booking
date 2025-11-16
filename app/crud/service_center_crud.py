import boto3
from boto3.dynamodb.conditions import Attr
from typing import List, Optional
from datetime import datetime
import uuid
from app.config import config
from app.models.service_center import ServiceCenter, ServiceCenterCreate, ServiceCenterUpdate

class ServiceCenterCRUD:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
        )
        self.table = self.dynamodb.Table(config.SERVICE_CENTERS_TABLE)
    
    def create_service_center(self, service_center_data: ServiceCenterCreate) -> ServiceCenter:
        """Create a new service center"""
        service_center_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        service_center = ServiceCenter(
            service_center_id=service_center_id,
            **service_center_data.dict(),
            created_at=timestamp,
            updated_at=timestamp
        )
        
        self.table.put_item(Item=service_center.dict())
        return service_center
    
    def get_service_center(self, service_center_id: str) -> Optional[ServiceCenter]:
        """Get service center by ID"""
        response = self.table.get_item(Key={'service_center_id': service_center_id})
        
        if 'Item' in response:
            return ServiceCenter(**response['Item'])
        return None
    
    def get_all_service_centers(self) -> List[ServiceCenter]:
        """Get all service centers"""
        response = self.table.scan()
        service_centers = [ServiceCenter(**item) for item in response.get('Items', [])]
        
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            service_centers.extend([ServiceCenter(**item) for item in response.get('Items', [])])
        
        return service_centers
    
    def get_service_centers_by_city(self, city: str) -> List[ServiceCenter]:
        """Get service centers by city"""
        response = self.table.scan(
            FilterExpression=Attr('city').eq(city)
        )
        return [ServiceCenter(**item) for item in response.get('Items', [])]
    
    def update_service_center(self, service_center_id: str, service_center_data: ServiceCenterUpdate) -> Optional[ServiceCenter]:
        """Update an existing service center"""
        current_service_center = self.get_service_center(service_center_id)
        if not current_service_center:
            return None
        
        update_data = service_center_data.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in update_data.keys()])
        expression_attribute_names = {f"#{k}": k for k in update_data.keys()}
        expression_attribute_values = {f":{k}": v for k, v in update_data.items()}
        
        response = self.table.update_item(
            Key={'service_center_id': service_center_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"
        )
        
        return ServiceCenter(**response['Attributes'])
    
    def delete_service_center(self, service_center_id: str) -> bool:
        """Delete a service center"""
        try:
            self.table.delete_item(Key={'service_center_id': service_center_id})
            return True
        except Exception as e:
            print(f"Error deleting service center: {e}")
            return False