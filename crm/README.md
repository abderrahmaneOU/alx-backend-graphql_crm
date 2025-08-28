# CRM Project – Task Scheduling & Automation

This project demonstrates how to use **cron jobs**, **django-crontab**, and **Celery with django-celery-beat** in a Django + GraphQL CRM system.

---

## 📌 Requirements

- Python 3.x
- Django
- GraphQL (graphene-django)
- Redis (for Celery)
- Packages in `requirements.txt`:
  - django-crontab
  - celery
  - django-celery-beat

---

## 🚀 Setup

### 1. Clone Repository
```bash
git clone https://github.com/<your-username>/alx-backend-graphql_crm.git
cd alx-backend-graphql_crm

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver