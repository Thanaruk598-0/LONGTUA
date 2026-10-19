# LONGTUA — Personal Adaptive Planner

## Technology Stack

- Mobile: React Native, Expo
- Backend: Python, FastAPI, Pydantic, SQLAlchemy
- Database: PostgreSQL
- Migrations: Alembic
- Infrastructure: Docker Compose

## Project Structure

- `mobile/` — Mobile application
- `backend/` — FastAPI backend
- `infra/` — Docker Compose and local infrastructure
- `docs/` — Architecture, requirements, UI/UX and roadmap

## Prerequisites

- Git
- Node.js and npm
- Python
- Docker Desktop

## Start PostgreSQL

Configure `infra/.env` using `infra/.env.example` as a reference.

From the project root, run:

    docker compose -f infra/docker-compose.yml up -d
    docker compose -f infra/docker-compose.yml ps

PostgreSQL is exposed locally on `127.0.0.1:5433`.

## Start Backend

Configure `backend/.env` using `backend/.env.example` as a reference.

From the project root, run:

    cd backend
    .\.venv\Scripts\Activate.ps1
    python -m uvicorn app.main:app --reload

Backend URLs:

- Health: http://127.0.0.1:8000/api/health
- API documentation: http://127.0.0.1:8000/docs

To apply database migrations manually:

    cd backend
    .\.venv\Scripts\Activate.ps1
    alembic upgrade head

For tests, use `backend/.env.test.example` as the template. The CI workflow
provisions its own PostgreSQL service and runs migrations before pytest.

## Mobile Development

From the project root, run:

    cd mobile
    npx expo start

Follow the Expo CLI instructions to open the app on a development device.

## Environment Files

Development, test, and infrastructure environments use separate environment
templates. Never commit real `.env` files, database credentials, tokens, or
private keys. Use `.env.example` files as templates only.
