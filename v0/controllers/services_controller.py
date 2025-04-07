# controllers/services_controller.py
from models.services_model import ServicesModel

class ServicesController:
    """Controller for service-related operations."""
    
    def __init__(self, db_manager=None):
        self.model = ServicesModel(db_manager)
    
    def get_all_services(self):
        """Get all services."""
        return self.model.get_all_services()
    
    def get_service(self, service_id):
        """Get a service by ID."""
        return self.model.get_service(service_id)
    
    def search_services(self, search_term):
        """Search for services."""
        return self.model.search_services(search_term)
    
    def add_service(self, name, price):
        """Add a new service."""
        # Validate required fields
        if not name:
            raise ValueError("Service name is required")
        
        if price < 0:
            raise ValueError("Price cannot be negative")
        
        return self.model.add_service(name, price)
    
    def update_service(self, service_id, name, price):
        """Update a service."""
        # Validate required fields
        if not name:
            raise ValueError("Service name is required")
        
        if price < 0:
            raise ValueError("Price cannot be negative")
        
        return self.model.update_service(service_id, name, price)
    
    def delete_service(self, service_id):
        """Delete a service."""
        return self.model.delete_service(service_id)

