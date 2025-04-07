import webbrowser
import urllib.parse

class WhatsAppSender:
    """Sends WhatsApp messages to customers."""
    
    def __init__(self):
        pass
    
    def send_message(self, phone, message):
        """Send a WhatsApp message using the web API."""
        # Clean the phone number (remove spaces, dashes, etc.)
        phone = ''.join(filter(str.isdigit, phone))
        
        # Ensure the phone number has the country code
        if not phone.startswith('+'):
            # Add Syria country code if not present
            if not phone.startswith('963'):
                phone = '963' + phone
        
        # URL encode the message
        encoded_message = urllib.parse.quote(message)
        
        # Create the WhatsApp URL
        url = f"https://wa.me/{phone}?text={encoded_message}"
        
        # Open the URL in the default browser
        webbrowser.open(url)
        
        return True
    
    def send_appointment_reminder(self, customer_name, customer_phone, appointment_date, services):
        """Send an appointment reminder to a customer."""
        message = f"مرحباً {customer_name}،\n\nهذا تذكير بموعدك في {appointment_date} للخدمات التالية: {services}.\n\nنتطلع لرؤيتك!\n\nمركز جوزيل للتجميل"
        return self.send_message(customer_phone, message)
    
    def send_invoice(self, customer_name, customer_phone, invoice_id, amount, payment_method):
        """Send an invoice notification to a customer."""
        message = f"مرحباً {customer_name}،\n\nتم إنشاء فاتورة جديدة برقم {invoice_id} بمبلغ {amount:,.0f} ل.س.\n\nطريقة الدفع: {payment_method}.\n\nشكراً لك!\n\nمركز جوزيل للتجميل"
        return self.send_message(customer_phone, message)
    
    def send_custom_message(self, customer_name, customer_phone, message_text):
        """Send a custom message to a customer."""
        message = f"مرحباً {customer_name}،\n\n{message_text}\n\nمركز جوزيل للتجميل"
        return self.send_message(customer_phone, message)

