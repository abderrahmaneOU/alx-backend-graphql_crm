from datetime import datetime
import requests

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_file = "/tmp/crm_heartbeat_log.txt"

    try:
        response = requests.post("http://localhost:8000/graphql", json={"query": "{ hello }"})
        status = response.json().get("data", {}).get("hello", "No response")
    except Exception:
        status = "GraphQL check failed"

    with open(log_file, "a") as f:
        f.write(f"{timestamp} CRM is alive - {status}\n")


def update_low_stock():
    mutation = """
    mutation {
      updateLowStockProducts {
        success
        products {
          name
          stock
        }
      }
    }
    """
    response = requests.post("http://localhost:8000/graphql", json={"query": mutation})
    data = response.json()

    log_file = "/tmp/low_stock_updates_log.txt"
    with open(log_file, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for p in data.get("data", {}).get("updateLowStockProducts", {}).get("products", []):
            f.write(f"{timestamp} - {p['name']} updated to stock {p['stock']}\n")
