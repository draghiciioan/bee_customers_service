# Set the environment variables
$env:CORS_ORIGINS = "http://localhost:3000,http://localhost:8080"
$env:DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/bee_customers"

# Run the application
Write-Host "Starting the application with CORS_ORIGINS=$env:CORS_ORIGINS"
python -c "from app.core.config import settings; print(f'CORS_ORIGINS type: {type(settings.CORS_ORIGINS)}, value: {settings.CORS_ORIGINS}')"
Write-Host "If you see the CORS_ORIGINS value printed above without errors, the fix was successful."