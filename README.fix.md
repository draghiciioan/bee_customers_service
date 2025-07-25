# BeeConect Customers Service Fix

## Issue Fixed

The `bee_customers_service` was failing to start with the following error:

```
pydantic_settings.exceptions.SettingsError: error parsing value for field "CORS_ORIGINS" from source "EnvSettingsSource"
```

The root cause was a conflict between Pydantic's automatic JSON parsing for list types and our custom parsing logic for the `CORS_ORIGINS` environment variable.

## Changes Made

1. Modified `app/core/config.py` to change the type annotation for `CORS_ORIGINS` from `list` to `str`:

   **Before:**
   ```python
   CORS_ORIGINS: list = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")]
   ```

   **After:**
   ```python
   CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
   ```

2. This change allows the application to use the existing parsing logic in `main.py` to convert the string to a list:

   ```python
   cors_origins = settings.CORS_ORIGINS
   if isinstance(cors_origins, str):
       cors_origins = [origin.strip() for origin in cors_origins.split(",")]
   ```

## How to Test

1. Rebuild the customers-service container:
   ```
   cd C:\Users\jhony\Desktop\BeeConect\beeconect-dev
   make customers-service
   ```

2. Check the logs to ensure the application starts correctly:
   ```
   docker logs -f beeconect-dev-customers-service-1
   ```

   You should see the application starting without any errors related to `CORS_ORIGINS`.

3. Test the API endpoints:
   ```
   curl http://localhost:8016/api/customers
   ```

## Technical Explanation

Pydantic's `BaseSettings` class expects complex types like lists to be provided as JSON strings in environment variables. When we defined `CORS_ORIGINS` as a list type in `config.py`, Pydantic tried to parse the environment variable as JSON before our custom parsing logic ran.

By changing the type to `str`, we avoid this conflict and let the application handle the parsing in `main.py`, which already has the logic to convert a comma-separated string to a list.

This is a more robust approach because:
1. It follows Pydantic's expected behavior for environment variables
2. It allows for different formats of the `CORS_ORIGINS` environment variable (comma-separated string or "*" wildcard)
3. It maintains compatibility with the existing code in `main.py`