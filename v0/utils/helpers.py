import os
import datetime
import re
import hashlib
import random
import string

def ensure_directory(directory):
    """Ensure a directory exists."""
    os.makedirs(directory, exist_ok=True)

def format_date(date_str, output_format="%Y-%m-%d"):
    """Format a date string."""
    if isinstance(date_str, datetime.date) or isinstance(date_str, datetime.datetime):
        return date_str.strftime(output_format)
    
    # Try to parse the date string
    if "T" in date_str:
        date_str = date_str.split("T")[0]
    
    try:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return date.strftime(output_format)
    except ValueError:
        return date_str

def format_currency(amount, currency="ل.س"):
    """Format a currency amount."""
    return f"{amount:,.0f} {currency}"

def clean_phone_number(phone):
    """Clean a phone number by removing non-digit characters."""
    return ''.join(filter(str.isdigit, phone))

def validate_email(email):
    """Validate an email address."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_random_password(length=8):
    """Generate a random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def calculate_age(birth_date):
    """Calculate age from birth date."""
    today = datetime.date.today()
    
    if isinstance(birth_date, str):
        birth_date = datetime.datetime.strptime(birth_date, "%Y-%m-%d").date()
    
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def get_week_start_date(date=None):
    """Get the start date of the week (Monday) for a given date."""
    if date is None:
        date = datetime.date.today()
    
    return date - datetime.timedelta(days=date.weekday())

def get_month_start_date(date=None):
    """Get the start date of the month for a given date."""
    if date is None:
        date = datetime.date.today()
    
    return date.replace(day=1)

def get_year_start_date(date=None):
    """Get the start date of the year for a given date."""
    if date is None:
        date = datetime.date.today()
    
    return date.replace(month=1, day=1)

def format_file_size(size_bytes):
    """Format file size in bytes to a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

