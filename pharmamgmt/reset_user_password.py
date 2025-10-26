#!/usr/bin/env python
"""
Script to reset user passwords or create new users for the Pharmacy Management System
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmamgmt.settings')
django.setup()

from core.models import Web_User
from django.contrib.auth.hashers import make_password

def list_users():
    """List all existing users"""
    print("\n=== Existing Users ===")
    users = Web_User.objects.all()
    if users:
        for user in users:
            print(f"Username: {user.username}")
            print(f"  - Active: {user.is_active}")
            print(f"  - User Type: {user.user_type}")
            print(f"  - Superuser: {user.is_superuser}")
            print()
    else:
        print("No users found in the database.")

def reset_password(username, new_password):
    """Reset password for an existing user"""
    try:
        user = Web_User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        print(f"✅ Password reset successfully for user '{username}'")
        print(f"New credentials: {username} / {new_password}")
        return True
    except Web_User.DoesNotExist:
        print(f"❌ User '{username}' not found!")
        return False

def create_user(username, password, user_type='admin'):
    """Create a new user"""
    try:
        if Web_User.objects.filter(username=username).exists():
            print(f"❌ User '{username}' already exists!")
            return False
        
        user = Web_User.objects.create_user(
            username=username,
            password=password,
            user_type=user_type,
            user_contact='N/A',
            is_superuser=True if user_type == 'admin' else False,
            is_staff=True
        )
        print(f"✅ User '{username}' created successfully!")
        print(f"Credentials: {username} / {password}")
        return True
    except Exception as e:
        print(f"❌ Error creating user: {str(e)}")
        return False

def main():
    print("Pharmacy Management System - User Management")
    print("=" * 50)
    
    list_users()
    
    print("\nOptions:")
    print("1. Reset password for existing user")
    print("2. Create new user")
    print("3. Show current valid credentials")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        username = input("Enter username to reset password: ").strip()
        new_password = input("Enter new password: ").strip()
        if username and new_password:
            reset_password(username, new_password)
        else:
            print("❌ Username and password cannot be empty!")
    
    elif choice == '2':
        username = input("Enter new username: ").strip()
        password = input("Enter password: ").strip()
        user_type = input("Enter user type (admin/manager/staff) [default: admin]: ").strip() or 'admin'
        if username and password:
            create_user(username, password, user_type)
        else:
            print("❌ Username and password cannot be empty!")
    
    elif choice == '3':
        print("\n=== Current Valid Credentials ===")
        print("Username: admin")
        print("Password: admin123")
        print("\nTry logging in with these credentials.")
    
    elif choice == '4':
        print("Goodbye!")
        return
    
    else:
        print("❌ Invalid choice!")

if __name__ == '__main__':
    main()