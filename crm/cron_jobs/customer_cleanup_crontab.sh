#!/bin/bash
# Script to delete inactive customers

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Run Django shell command to delete inactive customers
DELETED_COUNT=$(python manage.py shell -c "
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta
cutoff = timezone.now() - timedelta(days=365)
qs = Customer.objects.filter(orders__isnull=True, created_at__lt=cutoff)
count = qs.count()
qs.delete()
print(count)
")

echo "$TIMESTAMP - Deleted $DELETED_COUNT inactive customers" >> $LOG_FILE
