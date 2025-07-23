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
- **Message Broker**: RabbitMQ
- **Dependency Management**: Poetry
- **Testing**: pytest, pytest-asyncio
- **Containerization**: Docker
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana

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
   poetry install
   ```

3. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the service:
   ```
   poetry run uvicorn main:app --reload
   ```

### Docker Setup

1. Build and run with Docker Compose:
   ```
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

### Environment Variables

- `DATABASE_URL` - PostgreSQL connection string.
- `RABBITMQ_URL` - RabbitMQ connection URL.
- `RABBITMQ_EXCHANGE` - Exchange used for publishing events (`bee.customers.events`).
- `LOG_SERVICE_URL` - Optional endpoint for forwarding structured logs.

File uploads currently use the local `uploads/` directory. No dedicated environment variables are defined for this feature.

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

## Monitoring and Logging

- Prometheus metrics exposed at `/metrics`
- Structured logging compatible with Loki/ELK
- Health check endpoint at `/healthcheck`

## Changelog

- **2025-07-22**: Added explicit indexes for `Customer` model (`business_id`, `user_id`, `full_name`, `phone`). Existing deployments require table recreation to apply these indexes.
- **2025-07-22**: Introduced `RABBITMQ_URL` and `RABBITMQ_EXCHANGE` settings.
- **2025-07-23**: Customer, tag and note actions now publish events with trace IDs.
- **2025-07-23**: Added `LOG_SERVICE_URL` for forwarding logs to an external service.

## License

[License information]

## Contact

[Contact information]

---

Last updated: July 23, 2025