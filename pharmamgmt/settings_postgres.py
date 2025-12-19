# PostgreSQL Database Configuration
# Add this to your settings.py DATABASES section

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pharma_db',  # Change this to your database name
        'USER': 'postgres',  # Change this to your PostgreSQL username
        'PASSWORD': 'your_password',  # Change this to your PostgreSQL password
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
    }
}
