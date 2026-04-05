# TimeCapsule - Digital Time Capsule Platform

## Project Description
A web application where users can create digital time capsules with messages and images, set future opening dates, and share capsules with others.

### Prerequisites
- Python 3.13+
- PostgreSQL
- Redis (for Celery)

### Installation
1. Clone repo in PyCharm: https://github.com/MariyanDimov-250504/TimeCapsule 
2. Create venv (via terminal: python -m venv venv)
3. Install dependencies (via terminal: pip install -r requirements.txt)
4. Setup Database:
    CREATE DATABASE timecapsule_db;
    CREATE USER 'timecapsule_user' WITH PASSWORD 'your_password';
5. Create .env file:
    DB_NAME=timecapsule_db
    DB_USER=timecapsule_user
    DB_PASSWORD=your_password
    DB_HOST=localhost
    DB_PORT=5432
    SECRET_KEY=your_secret_key
    DEBUG=False
    REDIS_URL=redis://localhost:6379 (this is by default)
6. Start localhost testing: python manage.py runserver
7. Make sure Redis is running on your system (in searchbar open Services, find Redis, status Running)
8. In terminal run (separate): celery -A TimeCapsule worker --loglevel=info
9. Visit http://127.0.0.1:8000
10. You can visit Render demo: https://timecapsule-project.onrender.com

### Running tests
Use command: python manage.py test


📦 Features
User registration, login, profile with picture
Create time capsules with future opening dates
Privacy levels: Public, Shared, Private
Add text and image content to capsules
Share capsules with specific users
Real-time notifications when capsules are shared
Report inappropriate content
REST API endpoints
Responsive design with Bootstrap 5

🗄️ Tech Stack
Django 6.0
PostgreSQL
Redis & Celery (async tasks)
Django REST Framework
Bootstrap 5

📝 Environment Variables 
Variable        Description
SECRET_KEY      Django secret key
DEBUG           Set to False in production
DB_NAME         PostgreSQL database name
DB_USER         PostgreSQL username
DB_PASSWORD     PostgreSQL password
DB_HOST         Database host
DB_PORT         Database port (5432)
REDIS_URL       Redis connection URL

👥 User Groups
Timekeeper: Can open any capsule
Guardian: Can verify capsules