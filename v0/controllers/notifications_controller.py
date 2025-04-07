# controllers/notifications_controller.py
import datetime
from models.appointments_model import AppointmentsModel
from utils.whatsapp_sender import NotificationManager

class NotificationsController:
    """Controller for notification-related operations."""
    
    def __init__(self, db_manager=None, notification_manager=None):
        self.appointments_model = AppointmentsModel(db_manager)
        self.notification_manager = notification_manager or NotificationManager()
    
    def check_upcoming_appointments(self, hours_before=24):
        """Check for upcoming appointments and send notifications."""
        # Get current time
        now = datetime.datetime.now()
        
        # Calculate the time window for notifications
        notification_time = now + datetime.timedelta(hours=hours_before)
        
        # Get all appointments
        appointments = self.appointments_model.get_all_appointments()
        
        # Filter appointments that are within the notification window
        upcoming_appointments = []
        for appointment in appointments:
            appointment_time = datetime.datetime.fromisoformat(appointment['date_time'].replace('Z', '+00:00'))
            time_diff = (appointment_time - now).total_seconds() / 3600  # Convert to hours
            
            if 0 <= time_diff <= hours_before:
                upcoming_appointments.append(appointment)
        
        # Send notifications for upcoming appointments
        for appointment in upcoming_appointments:
            self.send_appointment_reminder(appointment)
        
        return len(upcoming_appointments)
    
    def send_appointment_reminder(self, appointment):
        """Send a reminder notification for an appointment."""
        # Format appointment time
        appointment_time = datetime.datetime.fromisoformat(appointment['date_time'].replace('Z', '+00:00'))
        formatted_time = appointment_time.strftime('%Y-%m-%d %H:%M')
        
        # Format services
        services = ', '.join([service['name'] for service in appointment['services']])
        
        # Create notification message
        message = f"تذكير بموعدك في {formatted_time} للخدمات التالية: {services}"
        
        # Send notification
        return self.notification_manager.send_notification(
            appointment['customer_name'],
            appointment['customer_phone'],
            message
        )
    
    def send_custom_notification(self, customer_name, customer_phone, message):
        """Send a custom notification to a customer."""
        return self.notification_manager.send_notification(
            customer_name,
            customer_phone,
            message
        )

