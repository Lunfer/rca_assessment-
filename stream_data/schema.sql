CREATE TABLE `rca-assessment.rca_dataset.orders_events`
(
    order_id STRING,
    status STRING,
    amount FLOAT64,
    created_at TIMESTAMP,
    event_timestamp TIMESTAMP,
    ingestion_time TIMESTAMP
)
PARTITION BY DATE(ingestion_time)
CLUSTER BY order_id;
