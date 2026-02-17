# Data Engineering Assignment: Setup & Execution Guide

This guide provides the step-by-step commands to provision the necessary Google Cloud infrastructure and run the real-time data pipeline locally.

---

## 1. Environment Preparation (Windows PowerShell)
To allow the Google Cloud SDK scripts to run in your VS Code terminal, set the execution policy for the current session:

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

---
## 2. BigQuery Infrastructure
First, we create the "Storage" layer. We need a dataset (folder) and a table (structure).

### Create the Dataset
```
bq mk --location=europe-west1 rca_dataset
```
### Create the Table (DDL)
Run the following command to execute your schema definition. (Ensure your DDL script is saved as ```schema.sql``` in your current directory):

```
bq query --use_legacy_sql=false < schema.sql
```

## 3. Pub/Sub Messaging Setup
Next, we set up the "Ingestion" layer to handle incoming data streams.

### Create the Topic

```
gcloud pubsub topics create orders-topic
```
### Create the Subscription
```
gcloud pubsub subscriptions create orders-sub --topic=orders-topic
```
## 4. Execute the Pipeline
Start the Python worker script. This script acts as the subscriber, transforming the data and inserting it into BigQuery.
```
python data_streamer.py
```
_Keep this terminal open. It will stay in "Listening" mode._

## 5. End-to-End Testing
Open a **second terminal tab** in VS Code and run the following command to "inject" a test event into the pipeline.
**Important:** We use backslashes (\") to escape the double quotes so PowerShell passes the JSON correctly to the Python script.

```
gcloud pubsub topics publish orders-topic --message='{\"id\": \"ORD-101\", \"status\": \"PENDING\", \"amount\": 150.00, \"created_at\": \"2026-02-17T14:00:00Z\", \"timestamp\": \"2026-02-17T14:01:00Z\"}'
```

## 6. Success Verification
- Terminal 1: Look for the log output: Inserted order: ORD-101.
- BigQuery Console: Run the following query to see your data:
```
SELECT * FROM `rca_dataset.orders_events` LIMIT 10;
```

## 7. Resource Cleanup
To avoid any unexpected cloud costs after finishing the assignment, run:
```
# Delete Pub/Sub Topic (and its subscriptions)
gcloud pubsub topics delete orders-topic

# Delete BigQuery Dataset (and its tables)
bq rm -r -f rca_dataset
```