from typing import Dict, Any
from datetime import datetime
from app.models.booking import ServiceType

class CostCalculator:
    """
    Non-CRUD Service for calculating service costs
    No database operations - Pure calculation logic
    """
    
    # Base prices for different service types
    BASE_PRICES = {
        ServiceType.OIL_CHANGE: 50.00,
        ServiceType.TIRE_ROTATION: 40.00,
        ServiceType.BRAKE_SERVICE: 150.00,
        ServiceType.ENGINE_DIAGNOSTIC: 100.00,
        ServiceType.FULL_SERVICE: 300.00,
        ServiceType.GENERAL_REPAIR: 80.00
    }
    
    # Additional charges
    LABOR_RATE_PER_HOUR = 75.00
    WEEKEND_SURCHARGE_PERCENT = 15.0
    URGENT_SERVICE_SURCHARGE = 50.00
    TAX_RATE = 0.08  # 8% tax
    
    def calculate_service_cost(
        self,
        service_type: ServiceType,
        estimated_hours: float = 1.0,
        is_weekend: bool = False,
        is_urgent: bool = False,
        additional_parts_cost: float = 0.0
    ) -> Dict[str, Any]:
        """Calculate total service cost with breakdown"""
        
        # Base service cost
        base_cost = self.BASE_PRICES.get(service_type, 100.00)
        
        # Labor cost
        labor_cost = estimated_hours * self.LABOR_RATE_PER_HOUR
        
        # Subtotal before surcharges
        subtotal = base_cost + labor_cost + additional_parts_cost
        
        # Calculate surcharges
        weekend_surcharge = 0.0
        if is_weekend:
            weekend_surcharge = subtotal * (self.WEEKEND_SURCHARGE_PERCENT / 100)
        
        urgent_surcharge = 0.0
        if is_urgent:
            urgent_surcharge = self.URGENT_SERVICE_SURCHARGE
        
        # Calculate total before tax
        total_before_tax = subtotal + weekend_surcharge + urgent_surcharge
        
        # Calculate tax
        tax = total_before_tax * self.TAX_RATE
        
        # Calculate final total
        final_total = total_before_tax + tax
        
        return {
            'service_type': service_type.value,
            'breakdown': {
                'base_service_cost': round(base_cost, 2),
                'labor_cost': round(labor_cost, 2),
                'estimated_hours': estimated_hours,
                'labor_rate_per_hour': self.LABOR_RATE_PER_HOUR,
                'additional_parts_cost': round(additional_parts_cost, 2),
                'weekend_surcharge': round(weekend_surcharge, 2),
                'urgent_surcharge': round(urgent_surcharge, 2),
                'subtotal': round(subtotal, 2),
                'tax': round(tax, 2),
                'tax_rate': f"{self.TAX_RATE * 100}%"
            },
            'estimated_total': round(final_total, 2),
            'currency': 'USD'
        }
    
    def calculate_bulk_discount(self, total_cost: float, num_services: int) -> Dict[str, Any]:
        """Calculate discount for multiple services"""
        discount_rate = 0.0
        
        if num_services >= 5:
            discount_rate = 0.15  # 15% discount
        elif num_services >= 3:
            discount_rate = 0.10  # 10% discount
        elif num_services >= 2:
            discount_rate = 0.05  # 5% discount
        
        discount_amount = total_cost * discount_rate
        final_cost = total_cost - discount_amount
        
        return {
            'original_cost': round(total_cost, 2),
            'num_services': num_services,
            'discount_rate': f"{discount_rate * 100}%",
            'discount_amount': round(discount_amount, 2),
            'final_cost': round(final_cost, 2),
            'savings': round(discount_amount, 2)
        }
    
    def calculate_membership_discount(self, total_cost: float, membership_tier: str) -> Dict[str, Any]:
        """Calculate discount based on membership tier"""
        discount_rates = {
            'BRONZE': 0.05,   # 5% discount
            'SILVER': 0.10,   # 10% discount
            'GOLD': 0.15,     # 15% discount
            'PLATINUM': 0.20  # 20% discount
        }
        
        discount_rate = discount_rates.get(membership_tier.upper(), 0.0)
        discount_amount = total_cost * discount_rate
        final_cost = total_cost - discount_amount
        
        return {
            'original_cost': round(total_cost, 2),
            'membership_tier': membership_tier.upper(),
            'discount_rate': f"{discount_rate * 100}%",
            'discount_amount': round(discount_amount, 2),
            'final_cost': round(final_cost, 2)
        }
    
    def estimate_service_duration(self, service_type: ServiceType) -> Dict[str, Any]:
        """Estimate service duration in hours"""
        durations = {
            ServiceType.OIL_CHANGE: 0.5,
            ServiceType.TIRE_ROTATION: 0.75,
            ServiceType.BRAKE_SERVICE: 2.0,
            ServiceType.ENGINE_DIAGNOSTIC: 1.5,
            ServiceType.FULL_SERVICE: 4.0,
            ServiceType.GENERAL_REPAIR: 2.0
        }
        
        duration = durations.get(service_type, 1.0)
        
        return {
            'service_type': service_type.value,
            'estimated_duration_hours': duration,
            'estimated_duration_minutes': int(duration * 60)
        }