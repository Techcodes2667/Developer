# Deployment Guide

This comprehensive guide covers deploying the Telehealth Diabetes Care System to various production environments including cloud platforms, VPS, and local servers.

## Table of Contents
- [Quick Deployment Options](#quick-deployment-options)
- [Production Requirements](#production-requirements)
- [Local Development Deployment](#local-development-deployment)
- [Cloud Platform Deployment](#cloud-platform-deployment)
- [VPS/Dedicated Server Deployment](#vpsdedicated-server-deployment)
- [Docker Deployment](#docker-deployment)
- [Database Configuration](#database-configuration)
- [Web Server Configuration](#web-server-configuration)
- [SSL/HTTPS Setup](#sslhttps-setup)
- [Environment Variables](#environment-variables)
- [Monitoring and Logging](#monitoring-and-logging)
- [Backup and Recovery](#backup-and-recovery)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)

## Quick Deployment Options

### Option 1: Heroku (Easiest - 15 minutes)
```bash
# Install Heroku CLI and deploy
git clone https://github.com/Techcodes2667/Developer.git
cd Developer/My_tele_app/telehealth_diabetes
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Option 2: DigitalOcean App Platform (Easy - 20 minutes)
1. Fork the repository on GitHub
2. Connect to DigitalOcean App Platform
3. Select the repository and configure build settings
4. Add PostgreSQL database addon
5. Deploy with one click

### Option 3: Railway (Easy - 10 minutes)
```bash
# Deploy to Railway
npm install -g @railway/cli
railway login
railway init
railway add postgresql
railway up
```

### Option 4: Docker (Intermediate - 30 minutes)
```bash
# Clone and run with Docker
git clone https://github.com/Techcodes2667/Developer.git
cd Developer/My_tele_app/telehealth_diabetes
docker-compose up -d
```

## Local Development Deployment

### Prerequisites
- Python 3.8+
- Git
- Code editor (VS Code recommended)

### Step-by-Step Local Setup

1. **Clone the Repository**
```bash
git clone https://github.com/Techcodes2667/Developer.git
cd Developer/My_tele_app/telehealth_diabetes
```

2. **Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Environment Configuration**
Create `.env` file:
```env
SECRET_KEY=your-development-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

6. **Load Sample Data (Optional)**
```bash
python manage.py populate_medications
python manage.py populate_education
python manage.py populate_support_groups
```

7. **Run Development Server**
```bash
python manage.py runserver
```

8. **Access Application**
- Open browser to `http://127.0.0.1:8000`
- Admin panel: `http://127.0.0.1:8000/admin`

## Cloud Platform Deployment

### Heroku Deployment (Recommended for Beginners)

#### Prerequisites
- Heroku account
- Heroku CLI installed
- Git repository

#### Step 1: Prepare Application
Create `Procfile` in project root:
```
web: gunicorn telehealth_diabetes.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate
```

Create `runtime.txt`:
```
python-3.11.6
```

Update `requirements.txt` to include:
```
gunicorn==21.2.0
dj-database-url==2.1.0
whitenoise==6.6.0
psycopg2-binary==2.9.7
```

#### Step 2: Configure Settings
Update `settings.py`:
```python
import dj_database_url
import os

# Heroku configuration
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'])

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

#### Step 3: Deploy to Heroku
```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-telehealth-app

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="your-telehealth-app.herokuapp.com"

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Run migrations
heroku run python manage.py migrate
heroku run python manage.py createsuperuser

# Open application
heroku open
```

### DigitalOcean App Platform

#### Step 1: Prepare Repository
Ensure your code is in a GitHub repository with proper `requirements.txt` and environment configuration.

#### Step 2: Create App
1. Go to DigitalOcean App Platform
2. Click "Create App"
3. Connect your GitHub repository
4. Select the repository and branch

#### Step 3: Configure Build Settings
```yaml
# .do/app.yaml
name: telehealth-diabetes
services:
- name: web
  source_dir: /My_tele_app/telehealth_diabetes
  github:
    repo: your-username/Developer
    branch: main
  run_command: gunicorn telehealth_diabetes.wsgi:application --bind 0.0.0.0:$PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DEBUG
    value: "False"
  - key: SECRET_KEY
    value: "your-secret-key"
databases:
- name: telehealth-db
  engine: PG
  version: "13"
```

#### Step 4: Deploy
1. Review configuration
2. Click "Create Resources"
3. Wait for deployment to complete

### Railway Deployment

#### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

#### Step 2: Deploy
```bash
# Login to Railway
railway login

# Initialize project
railway init

# Add PostgreSQL database
railway add postgresql

# Deploy
railway up

# Set environment variables
railway variables set SECRET_KEY="your-secret-key"
railway variables set DEBUG=False

# Run migrations
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

## Production Requirements

### System Requirements

**Minimum Requirements:**
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 50GB SSD
- **OS**: Ubuntu 20.04 LTS or CentOS 8
- **Network**: 100 Mbps connection

**Recommended Requirements:**
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 100GB SSD
- **OS**: Ubuntu 22.04 LTS
- **Network**: 1 Gbps connection

### Software Dependencies

- **Python**: 3.8+
- **PostgreSQL**: 12+
- **Nginx**: 1.18+
- **Redis**: 6.0+ (for caching and sessions)
- **Supervisor**: 4.0+ (for process management)

## Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose installed

### Step 1: Create Docker Files

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "telehealth_diabetes.wsgi:application", "--bind", "0.0.0.0:8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_DB: telehealth_db
      POSTGRES_USER: telehealth_user
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: gunicorn telehealth_diabetes.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=your-secret-key-here
      - DATABASE_URL=postgresql://telehealth_user:secure_password@db:5432/telehealth_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

**nginx.conf:**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream web {
        server web:8000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://web;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /app/staticfiles/;
        }

        location /media/ {
            alias /app/media/;
        }
    }
}
```

### Step 2: Deploy with Docker
```bash
# Clone repository
git clone https://github.com/Techcodes2667/Developer.git
cd Developer/My_tele_app/telehealth_diabetes

# Build and run
docker-compose up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load sample data
docker-compose exec web python manage.py populate_medications
docker-compose exec web python manage.py populate_education
```

### Step 3: Access Application
- Application: `http://localhost`
- Admin: `http://localhost/admin`

### Docker Management Commands
```bash
# View logs
docker-compose logs -f web

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Update application
git pull
docker-compose up -d --build

# Backup database
docker-compose exec db pg_dump -U telehealth_user telehealth_db > backup.sql

# Restore database
docker-compose exec -T db psql -U telehealth_user telehealth_db < backup.sql
```

## VPS/Dedicated Server Deployment

### Prerequisites
- Ubuntu 22.04 LTS server
- Root or sudo access
- Domain name (optional)

## Server Setup

### Initial Server Configuration

1. **Update System**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Install System Dependencies**
```bash
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx redis-server
sudo apt install -y supervisor git curl wget
sudo apt install -y build-essential libpq-dev
```

3. **Create Application User**
```bash
sudo adduser --system --group --home /opt/telehealth telehealth
sudo usermod -aG sudo telehealth
```

4. **Configure Firewall**
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Security Hardening

1. **SSH Configuration**
```bash
# Edit /etc/ssh/sshd_config
sudo nano /etc/ssh/sshd_config

# Add/modify these settings:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
Port 2222  # Change default port
```

2. **Fail2Ban Setup**
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

3. **Automatic Updates**
```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Database Configuration

### PostgreSQL Setup

1. **Create Database and User**
```bash
sudo -u postgres psql

CREATE DATABASE telehealth_prod;
CREATE USER telehealth_user WITH PASSWORD 'secure_random_password';
ALTER ROLE telehealth_user SET client_encoding TO 'utf8';
ALTER ROLE telehealth_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE telehealth_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE telehealth_prod TO telehealth_user;
\q
```

2. **Configure PostgreSQL**
```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/12/main/postgresql.conf

# Optimize for production
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

3. **Configure Authentication**
```bash
# Edit pg_hba.conf
sudo nano /etc/postgresql/12/main/pg_hba.conf

# Add line for application
local   telehealth_prod   telehealth_user                     md5
```

4. **Restart PostgreSQL**
```bash
sudo systemctl restart postgresql
```

### Database Backup Configuration

1. **Create Backup Script**
```bash
sudo nano /opt/telehealth/backup_db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/telehealth/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="telehealth_prod"
DB_USER="telehealth_user"

mkdir -p $BACKUP_DIR

pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_DIR/telehealth_backup_$DATE.sql.gz

# Keep only last 7 days of backups
find $BACKUP_DIR -name "telehealth_backup_*.sql.gz" -mtime +7 -delete
```

2. **Schedule Backups**
```bash
sudo crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/telehealth/backup_db.sh
```

## Application Deployment

### Code Deployment

1. **Clone Repository**
```bash
sudo -u telehealth git clone https://github.com/Techcodes2667/Developer.git /opt/telehealth/app
cd /opt/telehealth/app/My_tele_app/telehealth_diabetes
```

2. **Create Virtual Environment**
```bash
sudo -u telehealth python3 -m venv /opt/telehealth/venv
source /opt/telehealth/venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Environment Configuration

1. **Create Production Settings**
```bash
sudo -u telehealth nano /opt/telehealth/app/My_tele_app/telehealth_diabetes/.env
```

```env
# Django Settings
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

# Database
DATABASE_URL=postgresql://telehealth_user:secure_random_password@localhost:5432/telehealth_prod

# Redis
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Static and Media Files
STATIC_ROOT=/opt/telehealth/static
MEDIA_ROOT=/opt/telehealth/media
```

2. **Create Directories**
```bash
sudo mkdir -p /opt/telehealth/static
sudo mkdir -p /opt/telehealth/media
sudo mkdir -p /opt/telehealth/logs
sudo chown -R telehealth:telehealth /opt/telehealth/
```

### Database Migration

```bash
cd /opt/telehealth/app/My_tele_app/telehealth_diabetes
source /opt/telehealth/venv/bin/activate

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# Load sample data (optional)
python manage.py populate_medications
python manage.py populate_education
python manage.py populate_support_groups
```

## Web Server Configuration

### Gunicorn Configuration

1. **Create Gunicorn Configuration**
```bash
sudo nano /opt/telehealth/gunicorn.conf.py
```

```python
bind = "unix:/opt/telehealth/gunicorn.sock"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
user = "telehealth"
group = "telehealth"
tmp_upload_dir = None
errorlog = "/opt/telehealth/logs/gunicorn_error.log"
accesslog = "/opt/telehealth/logs/gunicorn_access.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
loglevel = "info"
```

2. **Create Systemd Service**
```bash
sudo nano /etc/systemd/system/telehealth.service
```

```ini
[Unit]
Description=Telehealth Diabetes Care System
After=network.target

[Service]
Type=notify
User=telehealth
Group=telehealth
RuntimeDirectory=telehealth
WorkingDirectory=/opt/telehealth/app/My_tele_app/telehealth_diabetes
Environment=PATH=/opt/telehealth/venv/bin
ExecStart=/opt/telehealth/venv/bin/gunicorn --config /opt/telehealth/gunicorn.conf.py telehealth_diabetes.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

3. **Enable and Start Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable telehealth
sudo systemctl start telehealth
sudo systemctl status telehealth
```

### Nginx Configuration

1. **Create Nginx Configuration**
```bash
sudo nano /etc/nginx/sites-available/telehealth
```

```nginx
upstream telehealth_app {
    server unix:/opt/telehealth/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Client Max Body Size
    client_max_body_size 10M;
    
    # Static Files
    location /static/ {
        alias /opt/telehealth/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media Files
    location /media/ {
        alias /opt/telehealth/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Favicon
    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }
    
    # Robots.txt
    location = /robots.txt {
        access_log off;
        log_not_found off;
    }
    
    # Application
    location / {
        proxy_pass http://telehealth_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }
}
```

2. **Enable Site**
```bash
sudo ln -s /etc/nginx/sites-available/telehealth /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL/HTTPS Setup

### Let's Encrypt SSL Certificate

1. **Install Certbot**
```bash
sudo apt install certbot python3-certbot-nginx
```

2. **Obtain Certificate**
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

3. **Auto-renewal**
```bash
sudo crontab -e

# Add certificate renewal check
0 12 * * * /usr/bin/certbot renew --quiet
```

### SSL Security Test

Test your SSL configuration at: https://www.ssllabs.com/ssltest/

## Environment Variables

### Required Environment Variables

Create a `.env` file or set these environment variables:

```env
# Django Core Settings
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security Settings (Production)
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Static and Media Files
STATIC_ROOT=/path/to/static/files
MEDIA_ROOT=/path/to/media/files
STATIC_URL=/static/
MEDIA_URL=/media/

# Cloud Storage (Optional)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Monitoring (Optional)
SENTRY_DSN=your-sentry-dsn
```

### Platform-Specific Environment Variables

#### Heroku
```bash
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="your-app.herokuapp.com"
```

#### DigitalOcean App Platform
Set in the app configuration dashboard or `.do/app.yaml`:
```yaml
envs:
- key: SECRET_KEY
  value: "your-secret-key"
- key: DEBUG
  value: "False"
```

#### Railway
```bash
railway variables set SECRET_KEY="your-secret-key"
railway variables set DEBUG=False
```

#### Docker
Set in `docker-compose.yml`:
```yaml
environment:
  - SECRET_KEY=your-secret-key
  - DEBUG=False
  - DATABASE_URL=postgresql://user:pass@db:5432/dbname
```

### Generating Secret Key

```python
# Generate a new secret key
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Or use online generator: https://djecrety.ir/

## Troubleshooting

### Common Deployment Issues

#### 1. Static Files Not Loading

**Problem**: CSS/JS files return 404 errors

**Solution**:
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_ROOT and STATIC_URL settings
# Ensure web server is configured to serve static files
```

#### 2. Database Connection Errors

**Problem**: `django.db.utils.OperationalError`

**Solutions**:
```bash
# Check database URL format
DATABASE_URL=postgresql://username:password@host:port/database

# Test database connection
python manage.py dbshell

# Check database service status
sudo systemctl status postgresql
```

#### 3. Permission Denied Errors

**Problem**: File permission issues

**Solution**:
```bash
# Fix file permissions
sudo chown -R www-data:www-data /path/to/app
sudo chmod -R 755 /path/to/app

# For media uploads
sudo chmod -R 775 /path/to/media
```

#### 4. Memory/Performance Issues

**Problem**: Application running slowly or crashing

**Solutions**:
```bash
# Check memory usage
free -h
htop

# Optimize Django settings
# Enable caching, optimize database queries
# Use connection pooling

# Scale horizontally
# Add more server instances
```

#### 5. SSL Certificate Issues

**Problem**: SSL certificate not working

**Solutions**:
```bash
# Renew Let's Encrypt certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates

# Test SSL configuration
openssl s_client -connect yourdomain.com:443
```

#### 6. Environment Variable Issues

**Problem**: Settings not loading correctly

**Solutions**:
```bash
# Check environment variables are set
printenv | grep SECRET_KEY

# Verify .env file location and format
# Ensure python-decouple is installed
pip install python-decouple
```

### Debugging Commands

```bash
# Check Django configuration
python manage.py check

# Test database migrations
python manage.py showmigrations

# Check for missing static files
python manage.py findstatic admin/css/base.css

# Test email configuration
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])

# Check logs
tail -f /var/log/nginx/error.log
tail -f /var/log/supervisor/telehealth.log
```

### Performance Monitoring

#### Application Performance
```bash
# Install monitoring tools
pip install django-silk
pip install sentry-sdk

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ...
    'silk',
]

# Add middleware
MIDDLEWARE = [
    'silk.middleware.SilkyMiddleware',
    # ...
]
```

#### Server Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor in real-time
htop  # CPU and memory usage
iotop  # Disk I/O
nethogs  # Network usage

# Check disk space
df -h

# Check system logs
journalctl -f
```

### Backup and Recovery

#### Database Backup
```bash
# PostgreSQL backup
pg_dump -U username -h hostname database_name > backup.sql

# Restore database
psql -U username -h hostname database_name < backup.sql

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U telehealth_user telehealth_db | gzip > /backups/db_backup_$DATE.sql.gz
find /backups -name "db_backup_*.sql.gz" -mtime +7 -delete
```

#### File Backup
```bash
# Backup media files
tar -czf media_backup_$(date +%Y%m%d).tar.gz /path/to/media/

# Backup entire application
tar -czf app_backup_$(date +%Y%m%d).tar.gz /path/to/app/
```

### Security Checklist

- [ ] Use HTTPS in production
- [ ] Set secure environment variables
- [ ] Enable Django security middleware
- [ ] Configure proper file permissions
- [ ] Set up firewall rules
- [ ] Enable fail2ban for SSH protection
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Use strong passwords
- [ ] Enable two-factor authentication

### Support Resources

- **Documentation**: [Django Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)
- **Community**: [Django Forum](https://forum.djangoproject.com/)
- **Security**: [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- **Performance**: [Django Performance](https://docs.djangoproject.com/en/stable/topics/performance/)

---

**Deployment Support:** For deployment assistance, contact oongugucodes@gmail.com

## Monitoring and Logging

### Log Configuration

1. **Django Logging Settings**
```python
# Add to settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/opt/telehealth/logs/django.log',
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

2. **Log Rotation**
```bash
sudo nano /etc/logrotate.d/telehealth
```

```
/opt/telehealth/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 telehealth telehealth
    postrotate
        systemctl reload telehealth
    endscript
}
```

### System Monitoring

1. **Install Monitoring Tools**
```bash
sudo apt install htop iotop nethogs
```

2. **System Health Check Script**
```bash
sudo nano /opt/telehealth/health_check.sh
```

```bash
#!/bin/bash
LOG_FILE="/opt/telehealth/logs/health_check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$DATE - WARNING: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEM_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ $MEM_USAGE -gt 80 ]; then
    echo "$DATE - WARNING: Memory usage is ${MEM_USAGE}%" >> $LOG_FILE
fi

# Check if services are running
systemctl is-active --quiet telehealth || echo "$DATE - ERROR: Telehealth service is down" >> $LOG_FILE
systemctl is-active --quiet nginx || echo "$DATE - ERROR: Nginx service is down" >> $LOG_FILE
systemctl is-active --quiet postgresql || echo "$DATE - ERROR: PostgreSQL service is down" >> $LOG_FILE
```

3. **Schedule Health Checks**
```bash
sudo crontab -e

# Run health check every 5 minutes
*/5 * * * * /opt/telehealth/health_check.sh
```

## Backup and Recovery

### Automated Backup System

1. **Full Backup Script**
```bash
sudo nano /opt/telehealth/full_backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/telehealth/backups"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/opt/telehealth/app"

mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U telehealth_user -h localhost telehealth_prod | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Media files backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C /opt/telehealth media/

# Configuration backup
tar -czf $BACKUP_DIR/config_backup_$DATE.tar.gz -C /opt/telehealth app/My_tele_app/telehealth_diabetes/.env

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*backup_*.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*backup_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

2. **Schedule Backups**
```bash
sudo crontab -e

# Daily backup at 3 AM
0 3 * * * /opt/telehealth/full_backup.sh
```

### Disaster Recovery

1. **Recovery Script**
```bash
sudo nano /opt/telehealth/restore.sh
```

```bash
#!/bin/bash
BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    exit 1
fi

# Stop application
sudo systemctl stop telehealth

# Restore database
gunzip -c $BACKUP_FILE | psql -U telehealth_user -h localhost telehealth_prod

# Start application
sudo systemctl start telehealth

echo "Restore completed"
```

## Performance Optimization

### Database Optimization

1. **PostgreSQL Tuning**
```sql
-- Create indexes for frequently queried fields
CREATE INDEX idx_glucose_patient_date ON health_data_bloodglucosereading(patient_id, recorded_at);
CREATE INDEX idx_medication_patient_active ON medication_management_patientmedication(patient_id, is_active);
CREATE INDEX idx_appointment_patient_date ON appointments_appointment(patient_id, scheduled_datetime);
```

2. **Query Optimization**
```python
# Use select_related and prefetch_related
appointments = Appointment.objects.select_related('patient', 'provider').filter(
    patient=patient_profile
)

# Use database functions
from django.db.models import Count, Avg
stats = BloodGlucoseReading.objects.filter(
    patient=patient_profile
).aggregate(
    avg_glucose=Avg('value'),
    reading_count=Count('id')
)
```

### Caching Configuration

1. **Redis Caching**
```python
# Add to settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session storage
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

2. **View Caching**
```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def dashboard(request):
    # View logic here
    pass
```

### Static File Optimization

1. **Enable Compression**
```bash
# Install compression tools
sudo apt install brotli

# Compress static files
find /opt/telehealth/static -name "*.css" -exec brotli {} \;
find /opt/telehealth/static -name "*.js" -exec brotli {} \;
```

2. **CDN Configuration** (Optional)
```python
# settings.py for CDN
STATIC_URL = 'https://cdn.yourdomain.com/static/'
MEDIA_URL = 'https://cdn.yourdomain.com/media/'
```

---

**Deployment Support:** For deployment assistance, contact oongugucodes@gmail.com
