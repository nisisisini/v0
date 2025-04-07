# controllers/clients_controller.py
from models.clients_model import ClientsModel

class ClientsController:
    """Controller for client-related operations."""
    
    def __init__(self, db_manager=None):
        self.model = ClientsModel(db_manager)
    
    def get_all_clients(self):
        """Get all clients."""
        return self.model.get_all_clients()
    
    def get_client(self, client_id):
        """Get a client by ID."""
        return self.model.get_client(client_id)
    
    def search_clients(self, search_term):
        """Search for clients."""
        return self.model.search_clients(search_term)
    
    def add_client(self, client_data):
        """Add a new client."""
        # Validate required fields
        if not client_data.get('name'):
            raise ValueError("Client name is required")
        
        if not client_data.get('phone'):
            raise ValueError("Client phone is required")
        
        return self.model.add_client(client_data)
    
    def update_client(self, client_id, client_data):
        """Update a client."""
        # Validate required fields
        if not client_data.get('name'):
            raise ValueError("Client name is required")
        
        if not client_data.get('phone'):
            raise ValueError("Client phone is required")
        
        return self.model.update_client(client_id, client_data)
    
    def delete_client(self, client_id):
        """Delete a client."""
        return self.model.delete_client(client_id)

