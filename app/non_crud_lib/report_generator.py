from typing import Dict, Any, List
from datetime import datetime
import json

class ReportGenerator:
    """
    Non-CRUD Service for generating various reports
    No database operations - Pure report generation logic
    """
    
    def generate_booking_summary_report(self, bookings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary report for bookings"""
        if not bookings:
            return {
                'status': 'success',
                'message': 'No bookings to generate report',
                'report': {}
            }
        
        total_bookings = len(bookings)
        status_counts = {}
        service_type_counts = {}
        total_revenue = 0.0
        
        for booking in bookings:
            # Count by status
            status = booking.get('status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by service type
            service_type = booking.get('service_type', 'UNKNOWN')
            service_type_counts[service_type] = service_type_counts.get(service_type, 0) + 1
            
            # Calculate total revenue
            if booking.get('actual_cost'):
                total_revenue += booking['actual_cost']
            elif booking.get('estimated_cost'):
                total_revenue += booking['estimated_cost']
        
        return {
            'status': 'success',
            'message': 'Booking summary report generated',
            'report': {
                'summary': {
                    'total_bookings': total_bookings,
                    'total_revenue': round(total_revenue, 2),
                    'average_booking_value': round(total_revenue / total_bookings, 2) if total_bookings > 0 else 0
                },
                'by_status': status_counts,
                'by_service_type': service_type_counts,
                'generated_at': datetime.utcnow().isoformat()
            }
        }
    
    def generate_customer_service_history(self, customer_bookings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate service history report for a customer"""
        if not customer_bookings:
            return {
                'status': 'success',
                'message': 'No service history found',
                'report': {}
            }
        
        total_services = len(customer_bookings)
        total_spent = sum(
            booking.get('actual_cost', booking.get('estimated_cost', 0))
            for booking in customer_bookings
        )
        
        services_by_type = {}
        for booking in customer_bookings:
            service_type = booking.get('service_type', 'UNKNOWN')
            services_by_type[service_type] = services_by_type.get(service_type, 0) + 1
        
        most_frequent_service = max(services_by_type, key=services_by_type.get) if services_by_type else 'N/A'
        
        return {
            'status': 'success',
            'message': 'Customer service history generated',
            'report': {
                'total_services': total_services,
                'total_amount_spent': round(total_spent, 2),
                'average_service_cost': round(total_spent / total_services, 2) if total_services > 0 else 0,
                'services_by_type': services_by_type,
                'most_frequent_service': most_frequent_service,
                'generated_at': datetime.utcnow().isoformat()
            }
        }
    
    def generate_service_center_performance(self, service_center_bookings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate performance report for a service center"""
        if not service_center_bookings:
            return {
                'status': 'success',
                'message': 'No bookings found for service center',
                'report': {}
            }
        
        total_bookings = len(service_center_bookings)
        completed_bookings = sum(1 for b in service_center_bookings if b.get('status') == 'COMPLETED')
        cancelled_bookings = sum(1 for b in service_center_bookings if b.get('status') == 'CANCELLED')
        
        completion_rate = (completed_bookings / total_bookings * 100) if total_bookings > 0 else 0
        cancellation_rate = (cancelled_bookings / total_bookings * 100) if total_bookings > 0 else 0
        
        total_revenue = sum(
            booking.get('actual_cost', 0)
            for booking in service_center_bookings
            if booking.get('status') == 'COMPLETED'
        )
        
        return {
            'status': 'success',
            'message': 'Service center performance report generated',
            'report': {
                'total_bookings': total_bookings,
                'completed_bookings': completed_bookings,
                'cancelled_bookings': cancelled_bookings,
                'completion_rate': round(completion_rate, 2),
                'cancellation_rate': round(cancellation_rate, 2),
                'total_revenue': round(total_revenue, 2),
                'average_revenue_per_booking': round(total_revenue / completed_bookings, 2) if completed_bookings > 0 else 0,
                'generated_at': datetime.utcnow().isoformat()
            }
        }
    
    def generate_monthly_report(self, month: int, year: int, all_bookings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate monthly performance report"""
        # Filter bookings for the specified month and year
        monthly_bookings = [
            booking for booking in all_bookings
            if self._is_in_month(booking.get('booking_date', ''), month, year)
        ]
        
        if not monthly_bookings:
            return {
                'status': 'success',
                'message': f'No bookings found for {month}/{year}',
                'report': {}
            }
        
        total_bookings = len(monthly_bookings)
        total_revenue = sum(
            booking.get('actual_cost', booking.get('estimated_cost', 0))
            for booking in monthly_bookings
        )
        
        return {
            'status': 'success',
            'message': f'Monthly report generated for {month}/{year}',
            'report': {
                'month': month,
                'year': year,
                'total_bookings': total_bookings,
                'total_revenue': round(total_revenue, 2),
                'average_booking_value': round(total_revenue / total_bookings, 2) if total_bookings > 0 else 0,
                'generated_at': datetime.utcnow().isoformat()
            }
        }
    
    def _is_in_month(self, date_string: str, month: int, year: int) -> bool:
        """Helper to check if date is in specified month/year"""
        try:
            date = datetime.fromisoformat(date_string)
            return date.month == month and date.year == year
        except:
            return False