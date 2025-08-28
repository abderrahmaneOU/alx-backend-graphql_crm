# Weekly CRM Report via Celery

This optional task uses Celery and django-celery-beat to generate a weekly CRM report summarizing:
- Total number of customers
- Total number of orders
- Total revenue from orders

The report runs **every Monday at 6:00 AM** and logs to `/tmp/crm_report_log.txt`.

---

## 🛠️ Setup Instructions

### 1. Install Redis and Python Dependencies

Install Redis:

```bash
sudo apt update
sudo apt install redis
```

Install required Python packages:

```bash
pip install -r requirements.txt
```

Make sure `requirements.txt` includes:

```
celery==5.3.6
django-celery-beat==2.6.0
```

---

### 2. Configure Django

- Add `'django_celery_beat'` to `INSTALLED_APPS` in `crm/settings.py`
- Add the following Celery configuration in `crm/settings.py`:

```python
from celery.schedules import crontab

CELERY_BROKER_URL = 'redis://localhost:6379/0'

CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}
```

---

### 3. Run Migrations

```bash
python manage.py migrate
```

---

### 4. Start Services

Start the Celery worker:

```bash
celery -A crm worker -l info
```

Start Celery Beat scheduler:

```bash
celery -A crm beat -l info
```

---

### 5. Verify Output

Check the file `/tmp/crm_report_log.txt` after Monday 6 AM or trigger the task manually:

```bash
python manage.py shell
>>> from crm.tasks import generate_crm_report
>>> generate_crm_report.delay()
```

Expected log format:

```
2025-07-14 06:00:00 - Report: 10 customers, 24 orders, 1024.50 revenue
```

---

✅ **Done!** Your Celery report task is now set up and scheduled.