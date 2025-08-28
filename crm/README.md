# CRM Celery Setup

## Setup Instructions

### 1. Install Redis and Dependencies
sudo apt update
sudo apt install redis-server
pip install -r requirements.txt

### 2. Run Migrations
python manage.py migrate

### 3. Start Celery Worker
celery -A crm worker -l info

### 4. Start Celery Beat
celery -A crm beat -l info

### 5. Verify Logs
cat /tmp/crm_report_log.txt
