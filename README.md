# Tender Tracker

## Description

Tender Tracker is a backend service for tracking tender statuses

The service allows users to:

- Create tenders
- Retrieve tenders
- Retrieve a list of tenders
- Filter tenders by status
- Update tender statuses
- Track the history of status changes

Each status change is recorded in a separate history table with information about the previous status, new status, user who made the change, timestamp, and reason

## Tech Stack

- Python 3.11
- Django 5.2
- Django REST Framework
- PostgreSQL 16
- Simple JWT
- drf-spectacular
- Poetry
- Pytest
- Docker
- Docker Compose

## Project Structure

```text
tender_tracker/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── tenders/
│   ├── migrations/
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_api.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── urls.py
│   └── views.py
├── .env.example
├── docker-compose.yml
├── manage.py
├── poetry.lock
├── pyproject.toml
└── pytest.ini
```

## Setup

### Clone The Repository

```bash
git clone <repository-url>
cd tender_tracker
```

### Install Dependencies

```bash
poetry install
```

### Configure Environment Variables

Copy the example environment file

```bash
cp .env.example .env
```

Fill in the required environment variables in `.env`

### Start PostgreSQL

```bash
docker compose up -d
```

### Apply Migrations

```bash
poetry run python manage.py migrate
```

### Create A Superuser

```bash
poetry run python manage.py createsuperuser
```

### Run The Development Server

```bash
poetry run python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

## Environment Variables

The application uses environment variables for Django and PostgreSQL configuration

```text
SECRET_KEY=change_me

POSTGRES_DB=tender_tracker
POSTGRES_USER=tender_user
POSTGRES_PASSWORD=change_me
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### Environment Variables Description

- `SECRET_KEY` Django secret key
- `POSTGRES_DB` PostgreSQL database name
- `POSTGRES_USER` PostgreSQL database user
- `POSTGRES_PASSWORD` PostgreSQL database password
- `POSTGRES_HOST` PostgreSQL service host
- `POSTGRES_PORT` PostgreSQL service port

The `.env` file should not be committed to the repository

## API Documentation

The API documentation is available through Swagger UI

```text
http://127.0.0.1:8000/api/docs/
```

The OpenAPI schema is available at:

```text
http://127.0.0.1:8000/api/schema/
```

## Authentication

The API uses JWT authentication

### Obtain Access Token

Send a POST request to:

```text
/api/auth/token/
```

Request body:

```json
{
    "username": "your_username",
    "password": "your_password"
}
```

The response contains an access token and a refresh token

Use the access token in the `Authorization` header for protected endpoints

```text
Authorization: Bearer <access_token>
```

### Refresh Access Token

Send a POST request to:

```text
/api/auth/token/refresh/
```

Request body:

```json
{
    "refresh": "<refresh_token>"
}
```

## API Endpoints

### Create Tender

**POST** `/api/tenders/`

Creates a new tender

Request body:

```json
{
    "title": "Test Tender",
    "description": "Test Description"
}
```

The tender is created with the `draft` status

The authenticated user is automatically assigned as the tender creator

### Retrieve Tender

**GET** `/api/tenders/<id>/`

Retrieves a tender with its status change history

### Retrieve Tender List

**GET** `/api/tenders/list/`

Retrieves a list of all tenders ordered by creation date

### Filter Tenders By Status

**GET** `/api/tenders/list/?status=active`

Retrieves tenders with the specified status

Supported statuses:

- `draft`
- `active`
- `won`
- `lost`

### Update Tender Status

**PATCH** `/api/tenders/<id>/status/`

Updates the tender status and creates a history record

Request body:

```json
{
    "status": "active",
    "reason": "Tender published"
}
```

The status change is recorded with:

- Previous Status
- New Status
- User
- Timestamp
- Reason

## Tender Status Flow

The following status transitions are supported:

```text
Draft → Active
Active → Won
Active → Lost
```

`Won` and `Lost` are final statuses

Invalid status transitions are rejected with a `400 Bad Request` response

Every successful status change is recorded in the tender status history

## Tests

The project uses Pytest and pytest-django for automated API testing

Run all tests with:

```bash
poetry run pytest
```

The test suite covers:

- Tender Creation
- Tender Retrieval
- Tender List
- Tender Filtering
- Status Updates
- Status Transition Validation
- Status Change History
- Authentication
- Request Validation
- Nonexistent Tenders


