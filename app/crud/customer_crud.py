import boto3
from boto3.dynamodb.conditions import Attr
from typing import List, Optional
from datetime import datetime
import uuid
from app.config import config
from app.models.customer import Customer, CustomerCreate, CustomerUpdate

class CustomerCRUD:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
        )
        self.table = self.dynamodb.Table(config.CUSTOMERS_TABLE)
    
    def create_customer(self, customer_data: CustomerCreate) -> Customer:
        """Create a new customer"""
        customer_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        customer = Customer(
            customer_id=customer_id,
            **customer_data.dict(),
            created_at=timestamp,
            updated_at=timestamp
        )
        
        self.table.put_item(Item=customer.dict())
        return customer
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID"""
        response = self.table.get_item(Key={'customer_id': customer_id})
        
        if 'Item' in response:
            return Customer(**response['Item'])
        return None
    
    def get_all_customers(self) -> List[Customer]:
        """Get all customers"""
        response = self.table.scan()
        customers = [Customer(**item) for item in response.get('Items', [])]
        
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            customers.extend([Customer(**item) for item in response.get('Items', [])])
        
        return customers
    
    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Get customer by email"""
        response = self.table.scan(
            FilterExpression=Attr('email').eq(email)
        )
        items = response.get('Items', [])
        return Customer(**items[0]) if items else None
    
    def update_customer(self, customer_id: str, customer_data: CustomerUpdate) -> Optional[Customer]:
        """Update an existing customer"""
        current_customer = self.get_customer(customer_id)
        if not current_customer:
            return None
        
        update_data = customer_data.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in update_data.keys()])
        expression_attribute_names = {f"#{k}": k for k in update_data.keys()}
        expression_attribute_values = {f":{k}": v for k, v in update_data.items()}
        
        response = self.table.update_item(
            Key={'customer_id': customer_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"
        )
        
        return Customer(**response['Attributes'])
    
    def delete_customer(self, customer_id: str) -> bool:
        """Delete a customer"""
        try:
            self.table.delete_item(Key={'customer_id': customer_id})
            return True
        except Exception as e:
            print(f"Error deleting customer: {e}")
            return False