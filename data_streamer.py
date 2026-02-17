import json
import datetime
from google.cloud import pubsub_v1
from google.cloud import bigquery

# Configuration
PROJECT_ID = "rca-assessment"
SUBSCRIPTION_ID = "orders-sub"
DATASET_ID = "rca_dataset"
TABLE_ID = "orders_events"

# Initialize Clients
subscriber = pubsub_v1.SubscriberClient()
bq_client = bigquery.Client()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

def transform_data(data):
    """
    Simple transformation: 
    1. Parse JSON
    2. Rename 'id' to 'order_id'
    3. Add processing timestamp
    """
    payload = json.loads(data)
    return {
        "order_id": payload.get("id"),
        "status": payload.get("status"),
        "amount": payload.get("amount"),
        "created_at": payload.get("created_at"), # The order creation time
        "event_timestamp": payload.get("timestamp"), # When the status changed
        "ingestion_time": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

def callback(message):
    try:
        # 1. Transform
        row = transform_data(message.data)
        
        # 2. Write to BigQuery
        errors = bq_client.insert_rows_json(table_ref, [row])
        
        if errors:
            print(f"BigQuery Error: {errors}")
            message.ack()
        else:
            print(f"Inserted order: {row['order_id']}")
            message.ack()
            
    except Exception as e:
        print(f"Processing Error: {e}")
        message.ack()  # ACK the message so it doesn't get redelivered

# Main Loop
print(f"Listening for messages on {subscription_path}...")
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

try:
    streaming_pull_future.result()
except KeyboardInterrupt:
    streaming_pull_future.cancel()
