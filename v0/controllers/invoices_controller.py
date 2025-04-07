# controllers/invoices_controller.py
from models.invoices_model import InvoicesModel

class InvoicesController:
    """Controller for invoice-related operations."""
    
    def __init__(self, db_manager=None):
        self.model = InvoicesModel(db_manager)
    
    def get_all_invoices(self):
        """Get all invoices."""
        return self.model.get_all_invoices()
    
    def get_invoice(self, invoice_id):
        """Get an invoice by ID."""
        return self.model.get_invoice(invoice_id)
    
    def search_invoices(self, search_term):
        """Search for invoices."""
        return self.model.search_invoices(search_term)
    
    def add_invoice(self, invoice_data):
        """Add a new invoice."""
        # Validate required fields
        if not invoice_data.get('customer_id'):
            raise ValueError("Customer ID is required")
        
        if not invoice_data.get('date'):
            raise ValueError("Date is required")
        
        if not invoice_data.get('services'):
            raise ValueError("At least one service is required")
        
        if not invoice_data.get('payment_method'):
            raise ValueError("Payment method is required")
        
        if not invoice_data.get('invoice_creator'):
            raise ValueError("Invoice creator is required")
        
        if not invoice_data.get('service_provider'):
            raise ValueError("Service provider is required")
        
        # Calculate total amount if not provided
        if not invoice_data.get('total_amount'):
            total = 0
            for service in invoice_data.get('services', []):
                price = service.get('price', 0)
                quantity = service.get('quantity', 1)
                total += price * quantity
            invoice_data['total_amount'] = total
        
        # Ensure amount_paid does not exceed total_amount
        if invoice_data.get('amount_paid', 0) > invoice_data.get('total_amount', 0):
            invoice_data['amount_paid'] = invoice_data.get('total_amount', 0)
        
        # Calculate amount_remaining
        invoice_data['amount_remaining'] = invoice_data.get('total_amount', 0) - invoice_data.get('amount_paid', 0)
        
        return self.model.add_invoice(invoice_data)
    
    def update_invoice(self, invoice_id, invoice_data):
        """Update an invoice."""
        # Validate required fields
        if not invoice_data.get('customer_id'):
            raise ValueError("Customer ID is required")
        
        if not invoice_data.get('date'):
            raise ValueError("Date is required")
        
        if not invoice_data.get('services'):
            raise ValueError("At least one service is required")
        
        if not invoice_data.get('payment_method'):
            raise ValueError("Payment method is required")
        
        if not invoice_data.get('invoice_creator'):
            raise ValueError("Invoice creator is required")
        
        if not invoice_data.get('service_provider'):
            raise ValueError("Service provider is required")
        
        # Calculate total amount if not provided
        if not invoice_data.get('total_amount'):
            total = 0
            for service in invoice_data.get('services', []):
                price = service.get('price', 0)
                quantity = service.get('quantity', 1)
                total += price * quantity
            invoice_data['total_amount'] = total
        
        # Ensure amount_paid does not exceed total_amount
        if invoice_data.get('amount_paid', 0) > invoice_data.get('total_amount', 0):
            invoice_data['amount_paid'] = invoice_data.get('total_amount', 0)
        
        # Calculate amount_remaining
        invoice_data['amount_remaining'] = invoice_data.get('total_amount', 0) - invoice_data.get('amount_paid', 0)
        
        return self.model.update_invoice(invoice_id, invoice_data)
    
    def delete_invoice(self, invoice_id):
        """Delete an invoice."""
        return self.model.delete_invoice(invoice_id)
    
    def get_daily_revenue(self, date):
        """Get the total revenue for a specific date."""
        return self.model.get_daily_revenue(date)
    
    def get_weekly_revenue(self, start_date):
        """Get the total revenue for a week starting from a specific date."""
        return self.model.get_weekly_revenue(start_date)
    
    def get_monthly_revenue(self, year, month):
        """Get the total revenue for a specific month."""
        return self.model.get_monthly_revenue(year, month)

