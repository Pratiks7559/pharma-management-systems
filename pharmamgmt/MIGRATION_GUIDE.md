# SQLite to PostgreSQL Migration Guide

## Prerequisites
1. Install PostgreSQL on your system
2. Create a new PostgreSQL database

## Step-by-Step Instructions

### Step 1: Install PostgreSQL Adapter
```bash
cd c:\pharmaproject pratk\WebsiteHostingService\WebsiteHostingService\WebsiteHostingService\pharmamgmt
pip install psycopg2-binary
```

### Step 2: Export Data from SQLite
```bash
python migrate_to_postgres.py
```
This will create `datadump.json` with all your data.

### Step 3: Setup PostgreSQL Database
Open PostgreSQL command line (psql) and run:
```sql
CREATE DATABASE pharma_db;
CREATE USER pharma_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE pharma_db TO pharma_user;
```

### Step 4: Update settings.py
Replace the DATABASES section in `pharmamgmt/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pharma_db',
        'USER': 'pharma_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
    }
}
```

### Step 5: Create Tables in PostgreSQL
```bash
python manage.py migrate
```

### Step 6: Import Data
```bash
python manage.py loaddata datadump.json
```

### Step 7: Verify Migration
```bash
python manage.py runserver
```

## Troubleshooting

### If loaddata fails:
1. Try loading in parts:
```bash
python manage.py loaddata datadump.json --exclude auth --exclude contenttypes
```

2. Or use this alternative script:
```bash
python import_data.py
```

### If you get permission errors:
```sql
ALTER DATABASE pharma_db OWNER TO pharma_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO pharma_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO pharma_user;
```

## Rollback (if needed)
Your original SQLite database (db.sqlite3) is still intact. Just revert the DATABASES setting in settings.py.
