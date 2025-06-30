@echo off
REM Telehealth Diabetes Care System - Quick Deployment Script (Windows)
REM This script helps with quick local setup and deployment on Windows

setlocal enabledelayedexpansion

REM Colors for output (Windows doesn't support colors in batch easily, so we'll use echo)
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

:print_status
echo %INFO% %~1
goto :eof

:print_success
echo %SUCCESS% %~1
goto :eof

:print_warning
echo %WARNING% %~1
goto :eof

:print_error
echo %ERROR% %~1
goto :eof

:check_python
REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "Python is not installed. Please install Python 3.8+ and try again."
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
call :print_success "Python %PYTHON_VERSION% found"
goto :eof

:setup_local
call :print_status "Setting up local development environment..."

REM Navigate to project directory
cd /d "%~dp0\My_tele_app\telehealth_diabetes"

REM Check Python
call :check_python

REM Create virtual environment
call :print_status "Creating virtual environment..."
python -m venv venv

REM Activate virtual environment
call :print_status "Activating virtual environment..."
call venv\Scripts\activate.bat

REM Upgrade pip
call :print_status "Upgrading pip..."
python -m pip install --upgrade pip

REM Install dependencies
call :print_status "Installing dependencies..."
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    call :print_status "Creating .env file..."
    (
        echo SECRET_KEY=your-secret-key-change-this-in-production
        echo DEBUG=True
        echo DATABASE_URL=sqlite:///db.sqlite3
        echo ALLOWED_HOSTS=localhost,127.0.0.1
    ) > .env
    call :print_success ".env file created"
) else (
    call :print_warning ".env file already exists"
)

REM Run migrations
call :print_status "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

REM Create superuser (optional)
set /p create_superuser="Do you want to create a superuser? (y/n): "
if /i "%create_superuser%"=="y" (
    python manage.py createsuperuser
)

REM Load sample data
set /p load_data="Do you want to load sample data? (y/n): "
if /i "%load_data%"=="y" (
    call :print_status "Loading sample data..."
    python manage.py populate_medications 2>nul || call :print_warning "Could not load medications data"
    python manage.py populate_education 2>nul || call :print_warning "Could not load education data"
    python manage.py populate_support_groups 2>nul || call :print_warning "Could not load support groups data"
)

REM Collect static files
call :print_status "Collecting static files..."
python manage.py collectstatic --noinput

call :print_success "Local development setup complete!"
echo.
call :print_status "To start the development server, run:"
call :print_status "  cd My_tele_app\telehealth_diabetes"
call :print_status "  venv\Scripts\activate.bat"
call :print_status "  python manage.py runserver"
echo.
call :print_status "Then visit: http://127.0.0.1:8000"
pause
goto :eof

:setup_docker
call :print_status "Setting up Docker deployment..."

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "Docker is not installed. Please install Docker Desktop and try again."
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "Docker Compose is not installed. Please install Docker Compose and try again."
    pause
    exit /b 1
)

REM Navigate to project directory
cd /d "%~dp0\My_tele_app\telehealth_diabetes"

REM Build and start containers
call :print_status "Building and starting Docker containers..."
docker-compose up -d --build

REM Wait for services to be ready
call :print_status "Waiting for services to be ready..."
timeout /t 30 /nobreak >nul

REM Run migrations
call :print_status "Running database migrations..."
docker-compose exec web python manage.py migrate

REM Create superuser (optional)
set /p create_superuser="Do you want to create a superuser? (y/n): "
if /i "%create_superuser%"=="y" (
    docker-compose exec web python manage.py createsuperuser
)

REM Load sample data
set /p load_data="Do you want to load sample data? (y/n): "
if /i "%load_data%"=="y" (
    call :print_status "Loading sample data..."
    docker-compose exec web python manage.py populate_medications 2>nul || call :print_warning "Could not load medications data"
    docker-compose exec web python manage.py populate_education 2>nul || call :print_warning "Could not load education data"
    docker-compose exec web python manage.py populate_support_groups 2>nul || call :print_warning "Could not load support groups data"
)

call :print_success "Docker deployment complete!"
call :print_status "Application is running at: http://localhost"
call :print_status "To view logs: docker-compose logs -f"
call :print_status "To stop: docker-compose down"
pause
goto :eof

:setup_heroku
call :print_status "Setting up Heroku deployment..."

REM Check if Heroku CLI is installed
heroku --version >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "Heroku CLI is not installed. Please install it from https://devcenter.heroku.com/articles/heroku-cli"
    pause
    exit /b 1
)

REM Navigate to project directory
cd /d "%~dp0\My_tele_app\telehealth_diabetes"

REM Login to Heroku
call :print_status "Logging into Heroku..."
heroku login

REM Get app name
set /p APP_NAME="Enter your Heroku app name: "

REM Create Heroku app
call :print_status "Creating Heroku app..."
heroku create %APP_NAME%

REM Add PostgreSQL addon
call :print_status "Adding PostgreSQL addon..."
heroku addons:create heroku-postgresql:hobby-dev --app %APP_NAME%

REM Set environment variables
call :print_status "Setting environment variables..."
heroku config:set SECRET_KEY="your-secret-key-change-this-in-production" --app %APP_NAME%
heroku config:set DEBUG=False --app %APP_NAME%
heroku config:set ALLOWED_HOSTS="%APP_NAME%.herokuapp.com" --app %APP_NAME%

REM Deploy to Heroku
call :print_status "Deploying to Heroku..."
git add .
git commit -m "Deploy to Heroku" 2>nul || call :print_warning "No changes to commit"
git push heroku main

REM Run migrations
call :print_status "Running database migrations..."
heroku run python manage.py migrate --app %APP_NAME%

REM Create superuser (optional)
set /p create_superuser="Do you want to create a superuser? (y/n): "
if /i "%create_superuser%"=="y" (
    heroku run python manage.py createsuperuser --app %APP_NAME%
)

REM Load sample data
set /p load_data="Do you want to load sample data? (y/n): "
if /i "%load_data%"=="y" (
    call :print_status "Loading sample data..."
    heroku run python manage.py populate_medications --app %APP_NAME% 2>nul || call :print_warning "Could not load medications data"
    heroku run python manage.py populate_education --app %APP_NAME% 2>nul || call :print_warning "Could not load education data"
    heroku run python manage.py populate_support_groups --app %APP_NAME% 2>nul || call :print_warning "Could not load support groups data"
)

call :print_success "Heroku deployment complete!"
call :print_status "Application URL: https://%APP_NAME%.herokuapp.com"

REM Open application
heroku open --app %APP_NAME%
pause
goto :eof

:show_menu
echo.
echo ======================================
echo   Telehealth Diabetes Care System
echo        Deployment Script
echo ======================================
echo.
echo Choose deployment option:
echo 1) Local Development Setup
echo 2) Docker Deployment
echo 3) Heroku Deployment
echo 4) Show Deployment Documentation
echo 5) Exit
echo.
goto :eof

:main
:menu_loop
call :show_menu
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    call :setup_local
    goto :end
) else if "%choice%"=="2" (
    call :setup_docker
    goto :end
) else if "%choice%"=="3" (
    call :setup_heroku
    goto :end
) else if "%choice%"=="4" (
    call :print_status "Please check docs\deployment.md for detailed deployment instructions"
    start docs\deployment.md 2>nul || call :print_status "Could not open documentation automatically"
    goto :menu_loop
) else if "%choice%"=="5" (
    call :print_status "Goodbye!"
    goto :end
) else (
    call :print_error "Invalid option. Please choose 1-5."
    goto :menu_loop
)

:end
pause
