# Installation Guide

This guide provides detailed instructions for setting up the Telehealth Diabetes Care System in different environments.

## Table of Contents
- [Development Setup](#development-setup)
- [Production Deployment](#production-deployment)
- [Docker Installation](#docker-installation)
- [Troubleshooting](#troubleshooting)

## Development Setup

### Prerequisites

Before installing the system, ensure you have the following installed:

- **Python 3.8 or higher**
- **pip** (Python package installer)
- **Git** (for version control)
- **PostgreSQL** (recommended) or SQLite (for development)
- **Node.js** (optional, for frontend development)

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/Techcodes2667/Developer.git
cd My_tele_app/telehealth_diabetes
```

#### 2. Create Virtual Environment

**On Windows:**
```bash
python -m venv my_tele_appvenv
my_tele_appvenv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv my_tele_appvenv
source my_tele_appvenv/bin/activate
```

#### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Database Setup

**For SQLite (Development):**
```bash
python manage.py makemigrations
python manage.py migrate
```

**For PostgreSQL (Recommended):**

1. Install PostgreSQL and create a database:
```sql
CREATE DATABASE telehealth_db;
CREATE USER telehealth_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE telehealth_db TO telehealth_user;
```

2. Update `settings.py` or create `.env` file:
```env
DATABASE_URL=postgresql://telehealth_user:your_password@localhost:5432/telehealth_db
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 5. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

#### 6. Load Sample Data

```bash
# Load medication data
python manage.py populate_medications

# Load educational content
python manage.py populate_education

# Load support groups
python manage.py populate_support_groups
```

#### 7. Collect Static Files

```bash
python manage.py collectstatic
```

#### 8. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000`

### Environment Configuration

Create a `.env` file in the project root directory:

```env
# Django Settings
SECRET_KEY=your-very-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/telehealth_db

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Media and Static Files
MEDIA_URL=/media/
STATIC_URL=/static/

# Security (for production)
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
```

## Production Deployment

### Prerequisites for Production

- **Ubuntu 20.04 LTS** (recommended)
- **Python 3.8+**
- **PostgreSQL 12+**
- **Nginx**
- **Gunicorn**
- **SSL Certificate**

### Production Installation Steps

#### 1. System Updates

```bash
sudo apt update
sudo apt upgrade -y
```

#### 2. Install System Dependencies

```bash
sudo apt install python3-pip python3-dev python3-venv
sudo apt install postgresql postgresql-contrib
sudo apt install nginx
sudo apt install git
```

#### 3. Database Setup

```bash
sudo -u postgres psql

CREATE DATABASE telehealth_db;
CREATE USER telehealth_user WITH PASSWORD 'secure_password';
ALTER ROLE telehealth_user SET client_encoding TO 'utf8';
ALTER ROLE telehealth_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE telehealth_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE telehealth_db TO telehealth_user;
\q
```

#### 4. Application Setup

```bash
cd /var/www/
sudo git clone https://github.com/Techcodes2667/Developer.git
sudo chown -R $USER:$USER /var/www/My_tele_app
cd My_tele_app/telehealth_diabetes

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 5. Production Environment Configuration

Create `/var/www/My_tele_app/telehealth_diabetes/.env`:

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DATABASE_URL=postgresql://telehealth_user:secure_password@localhost:5432/telehealth_db

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

#### 6. Database Migration and Static Files

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 7. Gunicorn Configuration

Create `/etc/systemd/system/telehealth.service`:

```ini
[Unit]
Description=Telehealth Diabetes Care System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/My_tele_app/telehealth_diabetes
Environment="PATH=/var/www/My_tele_app/telehealth_diabetes/venv/bin"
ExecStart=/var/www/My_tele_app/telehealth_diabetes/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/My_tele_app/telehealth_diabetes/telehealth.sock telehealth_diabetes.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 8. Nginx Configuration

Create `/etc/nginx/sites-available/telehealth`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /var/www/My_tele_app/telehealth_diabetes;
    }
    location /media/ {
        root /var/www/My_tele_app/telehealth_diabetes;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/My_tele_app/telehealth_diabetes/telehealth.sock;
    }
}
```

#### 9. Enable and Start Services

```bash
sudo systemctl start telehealth
sudo systemctl enable telehealth
sudo ln -s /etc/nginx/sites-available/telehealth /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## Docker Installation

### Using Docker Compose

Create `docker-compose.yml`:

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
      POSTGRES_PASSWORD: telehealth_password

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://telehealth_user:telehealth_password@db:5432/telehealth_db

volumes:
  postgres_data:
```

Create `Dockerfile`:

```dockerfile
FROM python:3.9

WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

Run with Docker:

```bash
docker-compose up --build
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Error

**Problem:** `django.db.utils.OperationalError: could not connect to server`

**Solution:**
- Ensure PostgreSQL is running
- Check database credentials in `.env` file
- Verify database exists and user has permissions

#### 2. Static Files Not Loading

**Problem:** CSS/JS files not loading in production

**Solution:**
```bash
python manage.py collectstatic --noinput
```

Ensure Nginx is configured to serve static files.

#### 3. Permission Denied Errors

**Problem:** Permission errors when running commands

**Solution:**
```bash
sudo chown -R $USER:$USER /var/www/My_tele_app
chmod +x manage.py
```

#### 4. Module Import Errors

**Problem:** `ModuleNotFoundError: No module named 'xyz'`

**Solution:**
```bash
pip install -r requirements.txt
```

Ensure virtual environment is activated.

### Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/Techcodes2667/Developer/issues)
2. Create a new issue with detailed error information
3. Contact support at oongugucodes@gmail.com

### Logs and Debugging

**View Django logs:**
```bash
tail -f /var/log/telehealth/django.log
```

**View Nginx logs:**
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

**View Gunicorn logs:**
```bash
sudo journalctl -u telehealth -f
```
