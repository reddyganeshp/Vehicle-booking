import re
from typing import Dict, Any
from datetime import datetime

class Validator:
    """
    Non-CRUD Service for validation logic
    No database operations - Pure validation logic
    """
    
    def validate_vehicle_registration(self, registration_number: str) -> Dict[str, Any]:
        """Validate vehicle registration number format"""
        # Example format: ABC-1234 or AB12-3456
        pattern = r'^[A-Z]{2,3}-?\d{4,6}$'
        
        is_valid = bool(re.match(pattern, registration_number.upper()))
        
        return {
            'is_valid': is_valid,
            'registration_number': registration_number.upper(),
            'message': 'Valid registration number' if is_valid else 'Invalid registration number format'
        }
    
    def validate_vin(self, vin: str) -> Dict[str, Any]:
        """Validate Vehicle Identification Number (VIN)"""
        # VIN is typically 17 characters, alphanumeric (excluding I, O, Q)
        pattern = r'^[A-HJ-NPR-Z0-9]{17}$'
        
        is_valid = bool(re.match(pattern, vin.upper())) if vin else False
        
        return {
            'is_valid': is_valid,
            'vin': vin.upper() if vin else '',
            'message': 'Valid VIN' if is_valid else 'Invalid VIN format (must be 17 characters, alphanumeric)'
        }
    
    def validate_phone_number(self, phone: str) -> Dict[str, Any]:
        """Validate phone number format"""
        # Remove common separators
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check if it's a valid 10-digit US phone number
        pattern = r'^\+?1?(\d{10})$'
        match = re.match(pattern, cleaned_phone)
        
        is_valid = bool(match)
        
        return {
            'is_valid': is_valid,
            'phone': phone,
            'cleaned_phone': cleaned_phone if is_valid else '',
            'message': 'Valid phone number' if is_valid else 'Invalid phone number format'
        }
    
    def validate_booking_date(self, booking_date: str, scheduled_time: str) -> Dict[str, Any]:
        """Validate that booking date is in the future"""
        try:
            booking_datetime = datetime.fromisoformat(f"{booking_date}T{scheduled_time}")
            current_datetime = datetime.now()
            
            is_future = booking_datetime > current_datetime
            
            if not is_future:
                return {
                    'is_valid': False,
                    'message': 'Booking date/time must be in the future',
                    'booking_datetime': booking_datetime.isoformat()
                }
            
            # Check if booking is at least 1 hour in advance
            hours_difference = (booking_datetime - current_datetime).total_seconds() / 3600
            
            if hours_difference < 1:
                return {
                    'is_valid': False,
                    'message': 'Booking must be at least 1 hour in advance',
                    'booking_datetime': booking_datetime.isoformat()
                }
            
            return {
                'is_valid': True,
                'message': 'Valid booking date/time',
                'booking_datetime': booking_datetime.isoformat(),
                'hours_until_booking': round(hours_difference, 2)
            }
        except Exception as e:
            return {
                'is_valid': False,
                'message': f'Invalid date/time format: {str(e)}'
            }
    
    def validate_service_eligibility(self, vehicle_mileage: int, last_service_mileage: int, service_type: str) -> Dict[str, Any]:
        """Validate if vehicle is eligible for service based on mileage"""
        mileage_requirements = {
            'OIL_CHANGE': 3000,
            'TIRE_ROTATION': 5000,
            'BRAKE_SERVICE': 10000,
            'ENGINE_DIAGNOSTIC': 0,  # Can be done anytime
            'FULL_SERVICE': 10000,
            'GENERAL_REPAIR': 0  # Can be done anytime
        }
        
        required_mileage = mileage_requirements.get(service_type, 0)
        mileage_since_last_service = vehicle_mileage - last_service_mileage
        
        is_eligible = mileage_since_last_service >= required_mileage
        
        return {
            'is_eligible': is_eligible,
            'service_type': service_type,
            'current_mileage': vehicle_mileage,
            'last_service_mileage': last_service_mileage,
            'mileage_since_last_service': mileage_since_last_service,
            'required_mileage': required_mileage,
            'message': 'Vehicle is eligible for service' if is_eligible else f'Vehicle needs {required_mileage - mileage_since_last_service} more miles before next service'
        }