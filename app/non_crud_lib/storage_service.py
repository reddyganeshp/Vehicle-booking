import boto3
from typing import Dict, Any, Optional
import io
from datetime import datetime, timedelta
from app.config import config

class StorageService:
    """
    Non-CRUD Service for managing documents in AWS S3
    No database operations - Pure file storage logic
    """
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = config.S3_BUCKET_NAME
    
    def upload_service_report(self, booking_id: str, file_content: bytes, file_name: str) -> Dict[str, Any]:
        """Upload service report to S3"""
        try:
            key = f"service-reports/{booking_id}/{file_name}"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                ContentType=self._get_content_type(file_name),
                Metadata={
                    'booking_id': booking_id,
                    'upload_date': datetime.utcnow().isoformat()
                }
            )
            
            return {
                'status': 'success',
                'message': 'Service report uploaded successfully',
                'file_key': key,
                'bucket': self.bucket_name
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to upload service report: {str(e)}'
            }
    
    def upload_invoice(self, booking_id: str, invoice_content: bytes, file_name: str) -> Dict[str, Any]:
        """Upload invoice to S3"""
        try:
            key = f"invoices/{booking_id}/{file_name}"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=invoice_content,
                ContentType='application/pdf',
                Metadata={
                    'booking_id': booking_id,
                    'document_type': 'invoice',
                    'upload_date': datetime.utcnow().isoformat()
                }
            )
            
            return {
                'status': 'success',
                'message': 'Invoice uploaded successfully',
                'file_key': key,
                'bucket': self.bucket_name
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to upload invoice: {str(e)}'
            }
    
    def upload_vehicle_image(self, vehicle_id: str, image_content: bytes, image_name: str) -> Dict[str, Any]:
        """Upload vehicle image to S3"""
        try:
            key = f"vehicle-images/{vehicle_id}/{image_name}"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_content,
                ContentType=self._get_content_type(image_name),
                Metadata={
                    'vehicle_id': vehicle_id,
                    'upload_date': datetime.utcnow().isoformat()
                }
            )
            
            return {
                'status': 'success',
                'message': 'Vehicle image uploaded successfully',
                'file_key': key,
                'bucket': self.bucket_name
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to upload vehicle image: {str(e)}'
            }
    
    def download_document(self, file_key: str) -> Dict[str, Any]:
        """Download document from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            
            file_content = response['Body'].read()
            
            return {
                'status': 'success',
                'message': 'Document downloaded successfully',
                'content': file_content,
                'content_type': response.get('ContentType', 'application/octet-stream'),
                'metadata': response.get('Metadata', {})
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to download document: {str(e)}'
            }
    
    def generate_presigned_url(self, file_key: str, expiration: int = 3600) -> Dict[str, Any]:
        """Generate presigned URL for temporary access to document"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expiration
            )
            
            return {
                'status': 'success',
                'message': 'Presigned URL generated successfully',
                'url': url,
                'expires_in': expiration
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to generate presigned URL: {str(e)}'
            }
    
    def list_documents_for_booking(self, booking_id: str) -> Dict[str, Any]:
        """List all documents associated with a booking"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"service-reports/{booking_id}/"
            )
            
            documents = []
            for obj in response.get('Contents', []):
                documents.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                })
            
            return {
                'status': 'success',
                'message': 'Documents listed successfully',
                'documents': documents,
                'count': len(documents)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to list documents: {str(e)}'
            }
    
    def delete_document(self, file_key: str) -> Dict[str, Any]:
        """Delete document from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            
            return {
                'status': 'success',
                'message': 'Document deleted successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to delete document: {str(e)}'
            }
    
    def _get_content_type(self, file_name: str) -> str:
        """Determine content type based on file extension"""
        extension = file_name.split('.')[-1].lower()
        content_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'txt': 'text/plain',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        return content_types.get(extension, 'application/octet-stream')