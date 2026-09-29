# EVE Healthcare API

## 1. Project Overview
A backend service for diagnostic test bookings and simulated payments, built with FastAPI and PostgreSQL. 

## 2. Features
- **Authentication**: JWT-based auth with secure password hashing.
- **Centres & Tests**: Manage diagnostic centres and the tests they offer with a many-to-many relationship.
- **Bookings**: Users can book tests at available centres. Server-side validation of prices and availability.
- **Payments**: Simulate payment provider workflows.
- **Webhooks**: Idempotent webhook processing to safely update booking and payment states.

## 3. Architecture
The project follows a clean layered architecture:
- **API (Routes)**: Handles HTTP requests, validation (Pydantic), and responses.
- **Services**: Contains the core business logic.
- **Models**: SQLAlchemy ORM models representing the database schema.
- **Schemas**: Pydantic models for request/response serialization and validation.
- **Core**: Configuration and security utilities.

## 4. Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0 (Async)
- **Migrations**: Alembic
- **Authentication**: JWT & Passlib (Bcrypt)

## 5. Setup Instructions (Docker)
1. Clone the repository.
2. Ensure you have Docker and Docker Compose installed.
3. Build and run: `docker-compose up -d --build`
4. The API will be available at `http://localhost:8000`
5. Swagger Docs available at `http://localhost:8000/docs`

## 6. Running Migrations
To initialize the database tables inside the Docker container:
```bash
docker-compose exec backend alembic upgrade head
```

## 7. Webhook Idempotency Explanation
The webhook endpoint (`POST /api/v1/payments/webhook`) is designed to be completely idempotent to handle network retries gracefully.
- Each webhook event payload contains a unique `event_id`.
- The system stores this `event_id` in a `webhook_events` table with a UNIQUE constraint.
- When an event arrives, we attempt to insert it. If a duplicate constraint violation occurs, the transaction rolls back safely, and we return a 200 OK indicating it was already processed.
- This prevents double-crediting or duplicate booking status updates.
