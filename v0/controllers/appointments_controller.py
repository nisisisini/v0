# controllers/appointments_controller.py
from models.appointments_model import AppointmentsModel

class AppointmentsController:
    """Controller for appointment-related operations."""
    
    def __init__(self, db_manager=None):
        self.model = AppointmentsModel(db_manager)
    
    def get_all_appointments(self):
        """Get all appointments."""
        return self.model.get_all_appointments()
    
    def get_appointment(self, appointment_id):
        """Get an appointment by ID."""
        return self.model.get_appointment(appointment_id)
    
    def get_appointments_by_date(self, date):
        """Get appointments for a specific date."""
        return self.model.get_appointments_by_date(date)
    
    def get_appointments_by_customer(self, customer_id):
        """Get appointments for a specific customer."""
        return self.model.get_appointments_by_customer(customer_id)
    
    def search_appointments(self, search_term):
        """Search for appointments."""
        return self.model.search_appointments(search_term)
    
    def add_appointment(self, appointment_data):
        """Add a new appointment."""
        # Validate required fields
        if not appointment_data.get('customer_id'):
            raise ValueError("Customer ID is required")
        
        if not appointment_data.get('date_time'):
            raise ValueError("Date and time are required")
        
        if not appointment_data.get('services'):
            raise ValueError("At least one service is required")
        
        if not appointment_data.get('service_provider'):
            raise ValueError("Service provider is required")
        
        if not appointment_data.get('status'):
            appointment_data['status'] = 'unconfirmed'
        
        return self.model.add_appointment(appointment_data)
    
    def update_appointment(self, appointment_id, appointment_data):
        """Update an appointment."""
        # Validate required fields
        if not appointment_data.get('customer_id'):
            raise ValueError("Customer ID is required")
        
        if not appointment_data.get('date_time'):
            raise ValueError("Date and time are required")
        
        if not appointment_data.get('services'):
            raise ValueError("At least one service is required")
        
        if not appointment_data.get('service_provider'):
            raise ValueError("Service provider is required")
        
        if not appointment_data.get('status'):
            appointment_data['status'] = 'unconfirmed'
        
        return self.model.update_appointment(appointment_id, appointment_data)
    
    def delete_appointment(self, appointment_id):
        """Delete an appointment."""
        return self.model.delete_appointment(appointment_id)
    
    def get_upcoming_appointments(self, days=7):
        """Get upcoming appointments for the next X days."""
        return self.model.get_upcoming_appointments(days)

