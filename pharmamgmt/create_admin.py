import os
import django
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

# Import Django models after setup
from core.models import Web_User
from django.contrib.auth.hashers import make_password

def create_admin_user():
    """Create an admin user for the Pharmacy Management System"""
    
    # Check if admin user already exists
    if Web_User.objects.filter(username='admin').exists():
        print("Admin user already exists.")
        return
    
    # Create the admin user
    admin_user = Web_User(
        username='admin',
        email='admin@example.com',
        password=make_password('admin123'),  # Set a default password
        first_name='Admin',
        last_name='User',
        user_type='admin',
        is_staff=True,
        is_superuser=True,
        is_active=True
    )
    
    # Save the user to the database
    admin_user.save()
    print("Admin user created successfully with username 'admin' and password 'admin123'")
    print("IMPORTANT: Please change the default password after first login.")

if __name__ == '__main__':
    create_admin_user()