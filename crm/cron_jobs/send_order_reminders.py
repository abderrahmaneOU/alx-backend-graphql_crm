#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta

LOG_FILE = "/tmp/order_reminders_log.txt"
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

query = """
query GetRecentOrders {
  orders(filter: {orderDate_Gte: "%s"}) {
    id
    customer {
      email
    }
  }
}
""" % ( (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d") )

response = requests.post(GRAPHQL_ENDPOINT, json={"query": query})
data = response.json()

with open(LOG_FILE, "a") as f:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for order in data.get("data", {}).get("orders", []):
        f.write(f"{timestamp} - Reminder for Order {order['id']} to {order['customer']['email']}\n")

print("Order reminders processed!")
