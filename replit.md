# Pharmacy Management System

## Overview

This is a comprehensive Django-based Pharmacy Management System designed to handle inventory, sales, purchases, customer management, and financial tracking for pharmacy operations. The system provides a web-based interface with user authentication, role-based access control, and comprehensive reporting capabilities.

## System Architecture

### Frontend Architecture
- **Template Engine**: Django Templates with Jinja2-style syntax
- **CSS Framework**: Bootstrap 5.3.0 for responsive design
- **Icons**: Font Awesome 6.0.0 for consistent iconography
- **JavaScript**: Vanilla JavaScript with Bootstrap components for interactivity
- **Layout**: Sidebar-based navigation with collapsible menu structure

### Backend Architecture
- **Framework**: Django 5.2 with Python
- **Database ORM**: Django ORM (configured for SQLite by default, extensible to PostgreSQL)
- **Authentication**: Custom user model extending AbstractUser
- **File Handling**: Django's built-in file upload system for images
- **Pagination**: Django's built-in pagination system

### Data Storage Solutions
- **Primary Database**: SQLite (development), ready for PostgreSQL migration
- **File Storage**: Local filesystem for uploaded images and documents
- **Session Management**: Django's session framework

## Key Components

### User Management
- **Custom User Model**: Extended AbstractUser with additional fields (user_type, contact, profile image)
- **Role-Based Access**: Admin, Manager, and Staff roles with different permissions
- **Authentication System**: Login/logout functionality with session management

### Inventory Management
- **Product Master**: Complete product catalog with barcode support
- **Batch Tracking**: Individual batch management with expiry dates
- **Stock Management**: Real-time stock calculation based on purchases and sales
- **Supplier Management**: Comprehensive supplier database

### Sales System
- **Customer Management**: Customer database with credit terms
- **Sales Invoicing**: Invoice generation with multiple rate structures (A, B, C)
- **Batch-Specific Pricing**: Different rates for different product batches
- **Payment Tracking**: Payment history and outstanding balance management

### Purchase System
- **Purchase Invoicing**: Purchase order and invoice management
- **Supplier Integration**: Linked to supplier master data
- **Batch Entry**: Product batch information entry during purchase
- **Financial Tracking**: Purchase payment tracking and outstanding calculations

### Reporting System
- **Inventory Reports**: Stock levels, batch-wise inventory, expiry date tracking
- **Financial Reports**: Sales, purchase, and payment summaries
- **Dashboard Analytics**: Key performance indicators and alerts

## Data Flow

1. **Purchase Flow**: Invoice → Product Entry → Stock Update → Payment Tracking
2. **Sales Flow**: Customer Selection → Product Selection (with batch) → Invoice Generation → Payment Processing
3. **Inventory Flow**: Purchase Updates → Stock Calculation → Low Stock Alerts → Expiry Monitoring
4. **Financial Flow**: Transaction Recording → Payment Tracking → Outstanding Management → Reporting

## External Dependencies

### Python Packages
- Django 5.2 (web framework)
- Pillow (image processing)
- Standard library modules for CSV processing and date handling

### Frontend Dependencies (CDN)
- Bootstrap 5.3.0-alpha1 (CSS framework)
- Font Awesome 6.0.0 (icons)
- jQuery (for Bootstrap components)

### Development Tools
- Django's built-in development server
- Django's admin interface for data management
- Django's migration system for database schema management

## Deployment Strategy

### Development Environment
- Django development server on localhost
- SQLite database for rapid development
- Static files served by Django's development server
- Media files handled through Django's FileSystemStorage

### Production Considerations
- **Database**: Ready for PostgreSQL integration (Drizzle ORM compatibility noted)
- **Static Files**: Configured for production static file serving
- **Media Files**: File upload handling with proper validation
- **Security**: CSRF protection, session security, and user authentication
- **Scalability**: Modular design supports horizontal scaling

### Configuration
- Environment-based settings (DEBUG, SECRET_KEY, ALLOWED_HOSTS)
- Replit-specific configuration for deployment
- Media and static file handling for cloud deployment

## Changelog
- June 30, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.