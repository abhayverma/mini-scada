# Mini-SCADA Industrial HMI System
A production-grade, containerized industrial Supervisory Control and Data Acquisition (SCADA) system. This project features a decoupled microservices architecture designed for real-time telemetry ingestion, fault monitoring, and secure grid operations.

## 🚀 Architecture Overview
The system is composed of five independent, containerized services orchestrated via Docker Compose.
- *Ingestion Layer:* Paho MQTT broker captures real-time data from grid simulators.
- *Processing Layer:* Python-based worker service with Pydantic schema validation.
- *Storage Layer:* TimescaleDB (PostgreSQL) for high-frequency time-series telemetry.
- *Caching Layer:* Redis for low-latency real-time state and alarm propagation.
- *API Layer:* FastAPI with strictly enforced Role-Based Access Control (RBAC).
- *Frontend Layer:* Vue 3 HMI with secure, reactive UI components.
- *Automation Layer:* A dedicated db-seed init-container handles Alembic schema migrations and data seeding to ensure a zero-friction startup.

## 🛠 Prerequisites
- Docker & Docker Compose installed.
- (Optional) Node.js and Python 3.11+ for local non-Docker development

## ⚡ Getting Started

1. Clone the repository
```Bash
git clone https://github.com/abhayverma/mini-scada
cd mini-scada
```
2. Environment & Secrets Management
- *🔒 Production Security Note:* In a true production environment, all sensitive credentials (database passwords, JWT keys) MUST be injected at runtime via a secure secrets manager (e.g., HashiCorp Vault, AWS Secrets Manager, or Kubernetes Secrets). Hardcoded `.env` files should never be committed to version control.
- For the purpose of local evaluation and testing, the Docker Compose stack expects the following environment variables to be present in the build environment. You can pass these via your CI/CD pipeline, or temporarily provision a local `.env` file in the `backend/` directory:
```Code snippet
DATABASE_URL=postgresql://scada_user:password@timescaledb:5432/scada_db
REDIS_URL=redis://redis:6379/0
MQTT_BROKER=broker
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
3. Launch the system
```Bash
docker compose up -d --build
```
Note: The db-seed container will automatically pause for 5 seconds to allow the database to initialize, run all Alembic migrations, and safely seed the default users before the data pipelines begin.

## 🌐 Application URLs & Access
Once the containers are healthy, access the system here:
- *HMI Dashboard (Vue UI):* `http://localhost:3000`
- *API Swagger Documentation:* `http://localhost:8000/docs`

### Default Seeded Credentials
Use these accounts to test the RBAC implementations across the UI and API:
- *Admin:* `admin / admin123`
- *Dispatcher:* `dispatcher / dispatch123`
- *Operator:* `operator / operator123`

## 🔐 Security & Roles (RBAC)

| Role | Telemetry/Alarms | Switch Operations | Audit Logs
| -------- | -------- | -------- | -------- |
| Operator | ✅ Read-Only | ❌ Denied & Hidden | ❌ Denied |
| Dispatcher | ✅ Read-Only | ✅ Authorized | ❌ Denied |
| Admin | ✅ Read-Only | ✅ Authorized | ✅ Authorized |

## 👥 User Management via Swagger UI
Instead of building a separate administrative frontend, this project leverages FastAPI's built-in OpenAPI Swagger interface for user provisioning and management.
To create a new user:
1. Navigate to the API Docs at http://localhost:8000/docs.
2. Click the green Authorize button at the top right and log in using the `admin` credentials (`admin` / `admin123`).
3. Scroll down to the Administration section and expand `POST /api/admin/users`.
4. Click Try it out and provide a JSON payload using one of the strict Enum roles (`admin`, `dispatcher`, `operator`):
```JSON
{
  "username": "night_shift_1",
  "password": "securepassword!23",
  "role": "dispatcher"
}
```
5. Click Execute. The system will validate the request, hash the password using `bcrypt`, and provision the account. You can immediately use these new credentials to log into the Vue HMI!

## 🏗 Key Technical Decisions
- *Defensive Data Pipeline:* Utilized Pydantic models for strict telemetry validation, ensuring malformed simulator data cannot corrupt the database.
- *Time-Series Optimization:* Implemented TimescaleDB hypertables for efficient historical data querying and storage management.
- *Decoupled UI:* Vue 3 component visibility is gated by user roles, ensuring the DOM is never rendered for unauthorized users.
- *Transactional Integrity:* Standardized on SQLAlchemy session management to prevent partial database failures.

## 📈 Troubleshooting & Maintenance

### Common Issues
- *Charts empty?* Check worker logs for `ValidationError` or `DB Flush Error`:
```Bash
docker compose logs -f worker
```
- *Access Denied (403)?* Ensure your JWT token contains the correct role claim. Admins cannot delete themselves to prevent system lockouts.

### Service Rebuilds
If you modify the source code, use the following commands to refresh specific containers without restarting the entire stack:
- Backend API: `docker compose up -d --build api` 
- Worker: `docker compose up -d --build worker`
- Frontend: `docker compose up -d --build frontend`