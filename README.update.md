# BeeConect Customers Service Update

## Issue Fixed

The issue with the `bbe_customers_service` not working correctly in the beeconect-dev environment has been fixed. The problem was that the database migrations were not being run when the container started, so the database schema was not being created.

## Changes Made

1. Created an entrypoint script (`entrypoint.sh`) that:
   - Waits for PostgreSQL to be ready
   - Runs the database migrations using Alembic
   - Starts the application using Uvicorn

2. Modified the Dockerfile to:
   - Add Alembic as a dependency
   - Make the entrypoint script executable
   - Use the entrypoint script instead of directly running Uvicorn

## How to Test

1. Rebuild the customers-service container:
   ```
   cd C:\Users\jhony\Desktop\BeeConect\beeconect-dev
   make customers-service
   ```

2. Check the logs to ensure the migrations are being run:
   ```
   docker logs -f beeconect-dev-customers-service-1
   ```

   You should see output like:
   ```
   Waiting for PostgreSQL to be ready...
   Running database migrations...
   INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
   INFO  [alembic.runtime.migration] Will assume transactional DDL.
   INFO  [alembic.runtime.migration] Running upgrade  -> 8c70b4aaf501, initial
   Starting the application...
   INFO:     Started server process [1]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8007 (Press CTRL+C to quit)
   ```

3. Test the API endpoints:
   ```
   curl http://localhost:8016/api/customers
   ```

## Additional Notes

If you encounter any issues with the entrypoint script, you may need to ensure it has the correct line endings (LF instead of CRLF) when running in a Linux container. You can fix this by running:

```
dos2unix entrypoint.sh
```

Or by setting Git to automatically handle line endings:

```
git config --global core.autocrlf input
```

Then re-clone the repository or checkout the file again.