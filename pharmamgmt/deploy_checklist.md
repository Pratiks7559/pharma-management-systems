# Production Deployment Checklist

## Before Deployment

- [ ] Set DEBUG = False in settings.py
- [ ] Set strong SECRET_KEY
- [ ] Setup Redis (Redis Cloud or self-hosted)
- [ ] Change database to PostgreSQL (not SQLite)
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Run migrations: `python manage.py migrate`

## Server Setup

- [ ] Get cloud server (AWS EC2 / DigitalOcean)
- [ ] Install: Python 3.11+, Redis, PostgreSQL, Nginx
- [ ] Clone your code to server
- [ ] Install requirements: `pip install -r requirements.txt`

## Environment Variables (on server)

```bash
export REDIS_URL="redis://your-redis-url:6379/1"
export SECRET_KEY="your-secret-key-here"
export DEBUG="False"
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
export ALLOWED_HOSTS="yoursite.com,www.yoursite.com"
```

## Run Application

```bash
# Using systemd service (recommended)
sudo systemctl start pharmamgmt
sudo systemctl enable pharmamgmt

# Or using screen (simple)
screen -S django
waitress-serve --threads=8 --host=127.0.0.1 --port=8000 pharmamgmt.wsgi:application
```

## GoDaddy DNS Setup

1. Login to GoDaddy
2. Go to DNS Management
3. Add A Record:
   - Type: A
   - Name: @
   - Value: YOUR_SERVER_IP
   - TTL: 600

4. Add CNAME for www:
   - Type: CNAME
   - Name: www
   - Value: @
   - TTL: 600

## SSL Certificate (Free)

```bash
sudo certbot --nginx -d yoursite.com -d www.yoursite.com
```

## Monitoring

- [ ] Setup error logging
- [ ] Monitor Redis memory usage
- [ ] Setup backup for database
- [ ] Monitor server CPU/RAM

## Cost Estimate

- Server: $6-10/month (DigitalOcean/AWS)
- Redis: Free (30MB) or $5/month (1GB)
- Domain: Already have (GoDaddy)
- SSL: Free (Let's Encrypt)

**Total: ~$6-15/month**
