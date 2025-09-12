# Dependency Decision: Redis + Celery

## Decision
Added Redis and Celery to handle background data ingestion tasks as required by PRD.

## Context
The PRD specifies that data ingestion from Excel files (customer_data.xlsx and loan_data.xlsx) must be done using background workers, not synchronously in the web request.

## Options Considered
1. **Django Background Tasks** - Built-in but limited for production use
2. **Celery + Redis** - Industry standard for background task processing
3. **Django Q** - Simpler but less scalable than Celery

## Why Celery + Redis
- **Scalability**: Can handle thousands of background tasks
- **Reliability**: Task results are stored and can be retrieved
- **Monitoring**: Rich monitoring and debugging tools available
- **Production Ready**: Widely used in production Django applications
- **Future Proof**: Easy to add more background tasks (emails, reports, etc.)

## Implementation
- Redis as message broker for task queuing
- Celery worker processes running in separate Docker container
- Tasks defined in `loans/tasks.py`
- Management command `ingest_data` supports both sync and async modes

## Alternative Considered
Could have used Django Background Tasks for simplicity, but Celery provides better production scalability and is more appropriate for the assignment requirements.

## Approval Status
✅ Approved - Required for PRD compliance with background ingestion requirement.
