# Telehealth Diabetes Care System

A comprehensive Django-based telehealth platform specifically designed for diabetes management in Kenya. This system provides patients with tools for health tracking, medication management, appointment scheduling, educational resources, community support, and goal setting.

## 🌟 Features

### For Patients
- **Health Data Tracking**: Blood glucose, blood pressure, weight, HbA1c monitoring
- **Medication Management**: Smart reminders, refill requests, interaction checking
- **Appointment Scheduling**: Virtual consultations with healthcare providers
- **Educational Resources**: Comprehensive diabetes learning library
- **Support Groups**: Community forums and peer support
- **Goals & Achievements**: SMART goal setting with progress tracking
- **Mental Health Support**: Mood tracking and wellness resources

### For Healthcare Providers
- **Patient Monitoring**: Access to patient health data and trends
- **Appointment Management**: Virtual consultation platform
- **Secure Messaging**: Communication with patients
- **Progress Tracking**: Monitor patient adherence and goals

### For Administrators
- **Content Management**: Educational resources and templates
- **User Management**: Patient and provider account oversight
- **System Analytics**: Platform usage monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django 4.2+
- PostgreSQL (recommended) or SQLite for development

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Techcodes2667/Developer.git
cd My_tele_app/telehealth_diabetes
```

2. **Create virtual environment**
```bash
python -m venv my_tele_appvenv
# On Windows:
my_tele_appvenv\Scripts\activate
# On macOS/Linux:
source my_tele_appvenv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure database**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Populate sample data**
```bash
python manage.py populate_medications
python manage.py populate_education
python manage.py populate_support_groups
```

7. **Run development server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## 📁 Project Structure

```
telehealth_diabetes/
├── telehealth_diabetes/        # Main project settings
├── main/                       # Public pages and core functionality
├── accounts/                   # User authentication and registration
├── patients/                   # Patient profiles and dashboard
├── health_data/               # Health metrics tracking
├── medication_management/     # Medication tracking and reminders
├── appointments/              # Appointment scheduling system
├── education/                 # Educational content and resources
├── mental_health/             # Mental wellness support
├── support_groups/            # Community forums and groups
├── goals/                     # Goal setting and achievement tracking
├── static/                    # Static files (CSS, JS, images)
├── templates/                 # HTML templates
├── media/                     # User uploaded files
└── docs/                      # Documentation
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/telehealth_db
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Configuration
The system supports PostgreSQL for production and SQLite for development.

## 🌐 Deployment

### Quick Deploy Options

#### Option 1: Heroku (Easiest - 15 minutes)
```bash
# Install Heroku CLI, then:
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

#### Option 2: Docker (Recommended - 10 minutes)
```bash
# Ensure Docker is installed, then:
docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

#### Option 3: Railway (Fastest - 5 minutes)
```bash
# Install Railway CLI, then:
railway init
railway add postgresql
railway up
```

#### Option 4: DigitalOcean App Platform
1. Fork this repository on GitHub
2. Connect to DigitalOcean App Platform
3. Select the repository and deploy with one click

### Production Deployment

For comprehensive production deployment instructions, see our detailed guides:

- **[📖 Complete Deployment Guide](docs/deployment.md)** - Covers all deployment scenarios
- **[📋 Deployment Checklist](docs/deployment-checklist.md)** - Ensure nothing is missed
- **[🔒 Security Guidelines](docs/security.md)** - Production security best practices

**Deployment Options Covered:**
- ☁️ Cloud Platforms (Heroku, DigitalOcean, Railway, AWS, GCP)
- 🐳 Docker Containerization
- 🖥️ VPS/Dedicated Server Setup
- 🔐 SSL/HTTPS Configuration
- 📊 Database Optimization
- 📈 Monitoring & Logging
- 💾 Backup Strategies
- 🛡️ Security Hardening

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

Run specific app tests:
```bash
python manage.py test health_data
python manage.py test medication_management
```

## 🌍 Localization

The system is designed for the Kenyan healthcare context with:
- Local healthcare provider integration
- Kenya-specific emergency contacts
- Cultural sensitivity in content
- Local food and nutrition information

## 🔒 Security

- CSRF protection enabled
- User authentication required for sensitive operations
- Data validation and sanitization
- Secure password requirements
- Session management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Support

For support and questions:
- Email: oongugucodes@gmail.com
- GitHub Issues: [Create an issue](https://github.com/Techcodes2667/Developer/issues)

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap team for the UI components
- Chart.js for data visualization
- Kenya Ministry of Health for diabetes care guidelines

## 📊 System Requirements

### Minimum Requirements
- 2GB RAM
- 10GB storage space
- Python 3.8+
- Modern web browser

### Recommended Requirements
- 4GB RAM
- 20GB storage space
- Python 3.10+
- PostgreSQL database
- SSL certificate for production

---

**Built with ❤️ for better diabetes care in Kenya**
