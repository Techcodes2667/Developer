#!/bin/bash

# Telehealth Diabetes Care System - Quick Deployment Script
# This script helps with quick local setup and deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.8+ and try again."
        exit 1
    fi

    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python 3.8+ is required. Found: $PYTHON_VERSION"
        exit 1
    fi

    print_success "Python $PYTHON_VERSION found"
}

# Function for local development setup
setup_local() {
    print_status "Setting up local development environment..."
    
    # Navigate to project directory
    cd "$(dirname "$0")/My_tele_app/telehealth_diabetes"
    
    # Check Python
    check_python
    
    # Create virtual environment
    print_status "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing dependencies..."
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_status "Creating .env file..."
        cat > .env << EOF
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
EOF
        print_success ".env file created"
    else
        print_warning ".env file already exists"
    fi
    
    # Run migrations
    print_status "Running database migrations..."
    python manage.py makemigrations
    python manage.py migrate
    
    # Create superuser (optional)
    read -p "Do you want to create a superuser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python manage.py createsuperuser
    fi
    
    # Load sample data
    read -p "Do you want to load sample data? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Loading sample data..."
        python manage.py populate_medications || print_warning "Could not load medications data"
        python manage.py populate_education || print_warning "Could not load education data"
        python manage.py populate_support_groups || print_warning "Could not load support groups data"
    fi
    
    # Collect static files
    print_status "Collecting static files..."
    python manage.py collectstatic --noinput
    
    print_success "Local development setup complete!"
    print_status "To start the development server, run:"
    print_status "  cd My_tele_app/telehealth_diabetes"
    print_status "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    print_status "  python manage.py runserver"
    print_status ""
    print_status "Then visit: http://127.0.0.1:8000"
}

# Function for Docker deployment
setup_docker() {
    print_status "Setting up Docker deployment..."
    
    # Check if Docker is installed
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker and try again."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
    
    # Navigate to project directory
    cd "$(dirname "$0")/My_tele_app/telehealth_diabetes"
    
    # Build and start containers
    print_status "Building and starting Docker containers..."
    docker-compose up -d --build
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Run migrations
    print_status "Running database migrations..."
    docker-compose exec web python manage.py migrate
    
    # Create superuser (optional)
    read -p "Do you want to create a superuser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose exec web python manage.py createsuperuser
    fi
    
    # Load sample data
    read -p "Do you want to load sample data? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Loading sample data..."
        docker-compose exec web python manage.py populate_medications || print_warning "Could not load medications data"
        docker-compose exec web python manage.py populate_education || print_warning "Could not load education data"
        docker-compose exec web python manage.py populate_support_groups || print_warning "Could not load support groups data"
    fi
    
    print_success "Docker deployment complete!"
    print_status "Application is running at: http://localhost"
    print_status "To view logs: docker-compose logs -f"
    print_status "To stop: docker-compose down"
}

# Function for Heroku deployment
setup_heroku() {
    print_status "Setting up Heroku deployment..."
    
    # Check if Heroku CLI is installed
    if ! command_exists heroku; then
        print_error "Heroku CLI is not installed. Please install it from https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    # Navigate to project directory
    cd "$(dirname "$0")/My_tele_app/telehealth_diabetes"
    
    # Login to Heroku
    print_status "Logging into Heroku..."
    heroku login
    
    # Get app name
    read -p "Enter your Heroku app name: " APP_NAME
    
    # Create Heroku app
    print_status "Creating Heroku app..."
    heroku create $APP_NAME
    
    # Add PostgreSQL addon
    print_status "Adding PostgreSQL addon..."
    heroku addons:create heroku-postgresql:hobby-dev --app $APP_NAME
    
    # Set environment variables
    print_status "Setting environment variables..."
    SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    heroku config:set SECRET_KEY="$SECRET_KEY" --app $APP_NAME
    heroku config:set DEBUG=False --app $APP_NAME
    heroku config:set ALLOWED_HOSTS="$APP_NAME.herokuapp.com" --app $APP_NAME
    
    # Deploy to Heroku
    print_status "Deploying to Heroku..."
    git add .
    git commit -m "Deploy to Heroku" || print_warning "No changes to commit"
    git push heroku main
    
    # Run migrations
    print_status "Running database migrations..."
    heroku run python manage.py migrate --app $APP_NAME
    
    # Create superuser (optional)
    read -p "Do you want to create a superuser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        heroku run python manage.py createsuperuser --app $APP_NAME
    fi
    
    # Load sample data
    read -p "Do you want to load sample data? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Loading sample data..."
        heroku run python manage.py populate_medications --app $APP_NAME || print_warning "Could not load medications data"
        heroku run python manage.py populate_education --app $APP_NAME || print_warning "Could not load education data"
        heroku run python manage.py populate_support_groups --app $APP_NAME || print_warning "Could not load support groups data"
    fi
    
    print_success "Heroku deployment complete!"
    print_status "Application URL: https://$APP_NAME.herokuapp.com"
    
    # Open application
    heroku open --app $APP_NAME
}

# Main menu
show_menu() {
    echo
    echo "======================================"
    echo "  Telehealth Diabetes Care System"
    echo "       Deployment Script"
    echo "======================================"
    echo
    echo "Choose deployment option:"
    echo "1) Local Development Setup"
    echo "2) Docker Deployment"
    echo "3) Heroku Deployment"
    echo "4) Show Deployment Documentation"
    echo "5) Exit"
    echo
}

# Main script
main() {
    while true; do
        show_menu
        read -p "Enter your choice (1-5): " choice
        
        case $choice in
            1)
                setup_local
                break
                ;;
            2)
                setup_docker
                break
                ;;
            3)
                setup_heroku
                break
                ;;
            4)
                print_status "Opening deployment documentation..."
                if command_exists xdg-open; then
                    xdg-open "docs/deployment.md"
                elif command_exists open; then
                    open "docs/deployment.md"
                else
                    print_status "Please check docs/deployment.md for detailed deployment instructions"
                fi
                ;;
            5)
                print_status "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please choose 1-5."
                ;;
        esac
    done
}

# Run main function
main
