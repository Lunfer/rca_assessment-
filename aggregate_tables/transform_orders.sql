MERGE `rca-assessment.rca_dataset.orders` T
USING (
    SELECT 
        order_id,
        status,
        amount,
        created_at,
        event_timestamp as last_updated_at
    FROM `rca-assessment.rca_dataset.orders_events`
    WHERE ingestion_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
    QUALIFY ROW_NUMBER() OVER(PARTITION BY order_id ORDER BY event_timestamp DESC) = 1
) S
ON T.order_id = S.order_id
WHEN MATCHED THEN
  UPDATE SET 
      status = S.status, 
      last_updated_at = S.last_updated_at,
      amount = S.amount
WHEN NOT MATCHED THEN
  INSERT (order_id, status, amount, created_at, last_updated_at)
  VALUES (order_id, status, amount, created_at, last_updated_at)
