# BeeConect - bee_customers_service

## Overview

**bee_customers_service** is a microservice component of the BeeConect platform that manages extended customer profiles. This service centralizes customer interaction history (orders, appointments), enables personalized customer experiences, and helps businesses with customer retention, loyalty, and segmentation.

## Key Features

- **Customer Profile Management**: Centralized personal data including name, email, phone, gender, preferences
- **Order History**: Integration with bee_orders_service
- **Appointment History**: Integration with bee_scheduling_service
- **Notes and Tags**: Visible only to administrators
- **Customer Statistics**: Number of orders, total value, last order
- **GDPR Compliance**: Support for export and deletion requests

## Architecture

This microservice follows the BeeConect platform's microservice architecture:
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Communication**: RabbitMQ for asynchronous event-driven communication
- **Authentication**: JWT-based via bee_auth_service
- **Containerization**: Docker for isolation and scalability

## Technical Stack

- **Language**: Python 3.12
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL (dedicated database)
- **Async Driver**: `asyncpg` with SQLAlchemy's async engine
- **Message Broker**: RabbitMQ
- **Dependency Management**: Poetry
- **Testing**: pytest, pytest-asyncio
- **Containerization**: Docker
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana
- **Rate Limiting**: slowapi
## Continuous Integration (GitHub Actions)
The pipeline defined in `.github/workflows/ci.yml` installs dependencies, runs `ruff` for linting, and executes the test suite.
Check the **Actions** tab or your pull request checks to see the results.


## Setup and Installation

### Prerequisites

- Python 3.12+
- Poetry
- Docker and Docker Compose
- PostgreSQL
- RabbitMQ

### Local Development Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd bee_customers_service
   ```

2. Install dependencies:
   ```
   poetry install --with dev
   ```

3. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```
The `.env.example` file lists all supported settings.

4. Initialize the database schema using Alembic migrations:
   ```bash
   poetry run alembic upgrade head
   ```
5. Run the service (listens on `http://localhost:8007`):
   ```bash
   poetry run uvicorn main:app --reload --port 8007
   ```
6. Visit `http://localhost:8007/docs` to verify the API is reachable.

### Running Tests Locally

Install dev dependencies and execute the full test suite with coverage:

```bash
poetry install --with dev
poetry run pytest --cov=bee_customers_service -vv
```

Tests rely on the settings in your `.env` file. The CI workflow defined in `.github/workflows/ci.yml` uses the same commands.

### Building and Running the Docker Image

Using Docker is the easiest way to try the service without installing Python and dependencies locally. The provided `docker-compose.yml` starts the API along with PostgreSQL and RabbitMQ.

1. **Build the image:**
   ```
   docker build -t bee_customers_service .
   ```

2. **Run the container:**
   ```
   docker run --env-file .env -p 8007:8007 bee_customers_service
   ```

3. **Alternatively, use Docker Compose (apply migrations first):**
   ```bash
   docker-compose run --rm bee_customers_service alembic upgrade head
   docker-compose up -d
   ```

## API Documentation

Once the service is running, API documentation is available at:
- Swagger UI: http://localhost:8007/docs
- ReDoc: http://localhost:8007/redoc

### Core Endpoints

| Method & Path | Description | Auth Requirement |
|---------------|-------------|-----------------|
| `PATCH /customers/{id}` | Update customer fields such as phone or avatar URL. | Customer themselves or admin |
| `POST /customers/{id}/avatar` | Upload a JPG/PNG avatar (max 1MB). Stored under `uploads/`. | Customer themselves or admin |
| `GET /customers?business_id=...&query=...` | List customers filtered by business and search query. | Admin roles |
| `POST /customers/{id}/tags` | Add one or more tags to a customer profile. | Admin roles |
| `DELETE /customers/{id}/tags/{tag_id}` | Remove a tag from a profile. | Admin roles |
| `POST /customers/{id}/notes` | Create a private note for a customer. | Admin roles |
| `GET /customers/{id}/notes` | List all notes for a customer. | Admin roles |
| `DELETE /customers/{id}/notes/{note_id}` | Delete a note. | Admin roles |
| `GET /customers/{id}/stats` | Retrieve order and appointment statistics. | Customer themselves or admin |

#### Role Requirements

| Action | Who is allowed? |
|--------|----------------|
| `GET /customers?business_id=...` | Only `admin_business` or `admin_manager` |
| `GET /customers/{id}` | The customer themselves or administrators |
| `PATCH /customers/{id}` | The customer themselves or administrators |
| `POST /customers/{id}/tags` & `POST /customers/{id}/notes` | Administrators only |
| `POST /customers/{id}/avatar` | The customer themselves or business administrators |
| `GET /customers/{id}/stats` | The customer themselves or administrators |

Request/response samples are available via Swagger UI. Below are a few examples:

**PATCH /customers/{id}**

Request
```json
{
  "phone": "+40798765432",
  "avatar_url": "https://cdn.example.com/avatars/ana.jpg"
}
```

Response
```json
{
  "id": "uuid",
  "full_name": "Ana Popescu",
  "phone": "+40798765432",
  "avatar_url": "https://cdn.example.com/avatars/ana.jpg"
}
```

**POST /customers/{id}/avatar**

Request: multipart/form-data with field `file` (JPEG/PNG)

Response
```json
{
  "avatar_url": "/uploads/{generated_filename}.jpg"
}
```

**GET /customers?business_id=uuid&query=ana**

Response
```json
[
  {
    "id": "uuid",
    "full_name": "Ana Popescu",
    "email": "ana@email.com"
  }
]
```

**/customers/{id}/stats**

Response
```json
{
  "total_orders": 12,
  "total_appointments": 8,
  "lifetime_value": 2750.0,
  "last_order_date": "2025-07-15"
}
```

#### Validation Rules

- Phone numbers must use the international format (`+407xxxxxxxx`).
- The same tag label cannot be added twice to the same customer profile.

#### Rate Limiting & Log Forwarding

- `PATCH /customers/{id}` is rate limited using `CUSTOMER_PATCH_RATE` (default `5/minute`).
- When `LOG_SERVICE_URL` is set, all structured logs are sent to that endpoint.

### Environment Variables

The service reads configuration from a `.env` file. Copy `\.env.example` and adjust values for your environment:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/bee_customers` |
| `RABBITMQ_URL` | RabbitMQ broker URL | `amqp://guest:guest@localhost:5672/` |
| `RABBITMQ_EXCHANGE` | Exchange used for publishing events | `bee.customers.events` |
| `LOG_SERVICE_URL` | Endpoint for forwarding structured logs | `http://localhost:8100/logs` |
| `CUSTOMER_PATCH_RATE` | Rate limit for `PATCH /customers/{id}` | `5/minute` |
| `CORS_ORIGINS` | Comma separated list of allowed CORS origins | `*` |
| `REDIS_URL` | Redis connection for failed events | `redis://localhost:6379/0` |

File uploads use the local `uploads/` directory and do not require extra variables.

## Integration with Other Services

This service integrates with:
- **bee_auth_service**: For authentication and basic user information
- **bee_orders_service**: For order history
- **bee_scheduling_service**: For appointment history
- **bee_notifications_service**: For personalized messaging

## RabbitMQ Events

The service publishes customer-related events to RabbitMQ. Set the broker URL
via the required `RABBITMQ_URL` environment variable. All events are sent to the
`bee.customers.events` exchange (type `topic`) using routing keys matching
`v1.customer.*`. Each message includes the HTTP `X-Trace-Id` value in the
`trace_id` header for end-to-end observability.

### Sample Payloads

`v1.customer.created`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "business_id": "uuid",
  "full_name": "Ana Popescu",
  "email": "ana@email.com",
  "trace_id": "uuid"
}
```

`v1.customer.updated`
```json
{
  "id": "uuid",
  "fields_changed": ["phone", "avatar_url"],
  "trace_id": "uuid"
}
```

`v1.customer.tagged`
```json
{
  "customer_id": "uuid",
  "tag_id": "uuid",
  "label": "VIP",
  "trace_id": "uuid"
}
```

`v1.customer.note_added`
```json
{
  "customer_id": "uuid",
  "note_id": "uuid",
  "trace_id": "uuid"
}
```

### Resending Failed Events

If RabbitMQ is unavailable, events are queued in Redis under `failed_events`.
Resend them with:

```bash
poetry run python scripts/resend_failed_events.py
```

## Monitoring and Logging

- Prometheus metrics are available at `/metrics` using `prometheus-fastapi-instrumentator` for scraping.
- Logs are emitted in structured JSON format compatible with Loki/ELK.
- Health check endpoint available at `/healthcheck`.

### Log Format

Each log entry is emitted as a single JSON object with the following fields:

- `timestamp` – ISO 8601 time of the event
- `level` – log level name in lowercase
- `service_name` – identifies this service
- `trace_id` – correlation identifier from the request
- `message` – log text

Example:

```json
{
  "timestamp": "2025-07-25T10:00:00Z",
  "level": "info",
  "service_name": "BeeConect Customer Service",
  "trace_id": "uuid",
  "message": "Customer created",
  "customer_id": "uuid"
}
```

## Changelog

- **2025-07-22**: Added explicit indexes for `Customer` model (`business_id`, `user_id`, `full_name`, `phone`). Existing deployments require table recreation to apply these indexes.
- **2025-07-22**: Introduced `RABBITMQ_URL` and `RABBITMQ_EXCHANGE` settings.
- **2025-07-23**: Customer, tag and note actions now publish events with trace IDs.
- **2025-07-23**: Added `LOG_SERVICE_URL` for forwarding logs to an external service.
- **2025-07-24**: Added rate limiting for `PATCH /customers/{id}` using slowapi and `CUSTOMER_PATCH_RATE` setting.
- **2025-07-25**: Documented role requirements, phone number format, tag uniqueness, and log forwarding details.
- **2025-07-26**: Added JSON log formatter with `timestamp`, `level`, `service_name`, and `trace_id` fields.
- **2025-07-27**: Added optional Redis queueing for failed events and management script `scripts/resend_failed_events.py`.
- **2025-07-23**: Switched to asynchronous SQLAlchemy with `asyncpg`; all routes and services are now async.
- **2025-07-28**: Database tables are no longer created automatically. Run migrations or a setup script before starting the service.

## License

[License information]

## Contact

[Contact information]

---

Last updated: July 23, 2025
