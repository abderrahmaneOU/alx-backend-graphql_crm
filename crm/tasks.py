from celery import shared_task
from datetime import datetime
import requests

@shared_task
def generate_crm_report():
    query = """
    query {
      customers { id }
      orders { id totalAmount }
    }
    """
    response = requests.post("http://localhost:8000/graphql", json={"query": query})
    data = response.json().get("data", {})

    num_customers = len(data.get("customers", []))
    num_orders = len(data.get("orders", []))
    revenue = sum([o.get("totalAmount", 0) for o in data.get("orders", [])])

    log_file = "/tmp/crm_report_log.txt"
    with open(log_file, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} - Report: {num_customers} customers, {num_orders} orders, {revenue} revenue\n")
