```mermaid

graph TD
    A[Cloud Scheduler] -->|Triggers Hourly| B[BigQuery Scheduled Query];
    B -->|Reads recent events from| C[(BQ: orders_events)];
    B -->|MERGEs latest status into| D[(BQ: orders)];

```
