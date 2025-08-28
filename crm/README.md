# CRM Celery Setup

## Requirements
- Redis
- Celery
- django-celery-beat

## Setup
```bash
sudo apt install redis-server
pip install -r requirements.txt
python manage.py migrate
