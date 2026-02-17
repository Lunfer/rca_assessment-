# Data Engineering Assignment: Setup & Execution Guide

This guide provides the step-by-step commands to provision the necessary Google Cloud infrastructure and run the real-time data pipeline locally.
* The python packages used are in the ```requirements.txt``` file.
* ``` pip install -r requirements.txt ```
* Also, a virtual enviroment ``` python -m venv .venv ``` was created and activated by first doing that ```Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process``` and then navigating to
```cd venv\scripts`` to run ``` .\activate.ps1 ```.

---
# Part 1: Stream Data


## 1. BigQuery Infrastructure
First, we create the "Storage" layer. We need a dataset (folder) and a table (structure).

### Create the Dataset
```powershell
bq mk --location=europe-west1 rca_dataset
```
### Create the Table (DDL)
Run the following command to execute your schema definition.

```powershell
bq query --use_legacy_sql=false < schema.sql
```

## 2. Pub/Sub Messaging Setup
Next, we set up the "Ingestion" layer to handle incoming data streams.

### Create the Topic

```powershell
gcloud pubsub topics create orders-topic
```
### Create the Subscription
```powershell
gcloud pubsub subscriptions create orders-sub --topic=orders-topic
```
## 3. Execute the Pipeline
Start the Python worker script. This script acts as the subscriber, transforming the data and inserting it into BigQuery.
```powershell
python data_streamer.py
```
_Keep this terminal open. It will stay in "Listening" mode._

## 4. End-to-End Testing
Open a **second terminal tab** in VS Code and run the following command to "inject" a test event into the pipeline.

```powershell
gcloud pubsub topics publish orders-topic --message='{\"id\": \"ORD-101\", \"status\": \"PENDING\", \"amount\": 150.00, \"created_at\": \"2026-02-17T14:00:00Z\", \"timestamp\": \"2026-02-17T14:01:00Z\"}'
```

## 5. Success Verification
- Terminal 1: Look for the log output: Inserted order: ORD-101.
- BigQuery Console: Run the following query to see your data:
```powershell
SELECT * FROM `rca_dataset.orders_events` LIMIT 10;
```

## 6. Resource Cleanup
After finishing the assignment, run:
```powershell
# Delete Pub/Sub Topic (and its subscriptions)
gcloud pubsub topics delete orders-topic

# Delete BigQuery Dataset (and its tables)
bq rm -r -f rca_dataset
```

# Part 2: Aggregated tables
## Solution 1: BigQuery Scheduled Query
This step merges multiple status updates into a single "Latest Status" per order.

### Run the transformation
```powershell
bq query --use_legacy_sql=false --destination_table=rca_dataset.orders --display_name="Hourly_Order_Aggregation" --schedule="every 1 hours" < transform_orders.sql
```
