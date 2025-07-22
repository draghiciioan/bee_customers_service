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

## Integration with Other Services

This service integrates with:
- **bee_auth_service**: For authentication and basic user information
- **bee_orders_service**: For order history
- **bee_scheduling_service**: For appointment history
- **bee_notifications_service**: For personalized messaging

## Monitoring and Logging

- Prometheus metrics exposed at `/metrics`
- Structured logging compatible with Loki/ELK
- Health check endpoint at `/healthcheck`

## Changelog

- **2025-07-22**: Added explicit indexes for `Customer` model (`business_id`, `user_id`, `full_name`, `phone`). Existing deployments require table recreation to apply these indexes.

## License

[License information]

## Contact

[Contact information]

---

Last updated: July 22, 2025